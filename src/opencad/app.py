"""Qt desktop prototype. A temporary shell to validate command workflows."""
import argparse
import json
import os
import sys
from pathlib import Path
from math import hypot
from PySide6.QtCore import Qt, QPointF, QRectF, Signal
from PySide6.QtGui import QColor, QPainter, QPen, QKeySequence, QAction, QFontDatabase, QFont
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QTabWidget, QPushButton, QLabel, QDockWidget, QPlainTextEdit,
    QLineEdit, QListWidget, QFormLayout, QFileDialog, QMessageBox,QInputDialog)
from .model import Document, Point, Line, Circle
from .qcad_views import Arc,Polyline
from .commands import CommandBus
from .lisp import LispRuntime
from .interop import load_dxf, save_dxf
from .properties import PropertiesPanel


class Canvas(QWidget):
    clicked = Signal(object)
    moved = Signal(object)
    cancelled = Signal()

    def __init__(self, window):
        super().__init__()
        self.window = window
        self.scale = 4.0
        self.offset = QPointF(110, 380)
        self.grid = True
        self.snap = False
        self.cursor = None
        self.selection_start = None
        self.selection_end = None
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMinimumSize(600, 320)
        self.setObjectName("cadCanvas")

    def screen(self, p):
        return QPointF(self.offset.x()+p.x*self.scale, self.offset.y()-p.y*self.scale)

    def world(self, p):
        x, y = (p.x()-self.offset.x())/self.scale, (self.offset.y()-p.y())/self.scale
        if self.snap:
            x, y = round(x/10)*10, round(y/10)*10
        return Point(x, y)

    def mousePressEvent(self, event):
        self.setFocus()
        if event.button() == Qt.MouseButton.LeftButton:
            if self.window.mode is None and hasattr(self.window.doc,'select'):
                self.selection_start=event.position(); self.selection_end=None
                self.selection_modifiers=event.modifiers()
            else:
                self.clicked.emit(self.world(event.position()))
        elif event.button() == Qt.MouseButton.RightButton:
            self.cancelled.emit()

    def mouseMoveEvent(self, event):
        if self.selection_start is not None: self.selection_end=event.position()
        self.cursor = self.world(event.position())
        self.moved.emit(self.cursor)
        self.update()

    def mouseReleaseEvent(self,event):
        if event.button()==Qt.MouseButton.LeftButton and self.selection_start is not None:
            start,end=self.selection_start,event.position()
            self.selection_start=self.selection_end=None
            if (end-start).manhattanLength()<4:
                self.window.on_point(self.world(end),self.selection_modifiers)
            else:
                mode='window' if end.x()>start.x() else 'crossing'
                self.window.select_region(mode,self.world(start),self.world(end),self.selection_modifiers)
            self.update()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.cancelled.emit()
        elif event.key() in (Qt.Key.Key_Return,Qt.Key.Key_Enter) and self.window.mode=='PLINE':
            self.window.finish_polyline(False)
        else:
            super().keyPressEvent(event)

    def wheelEvent(self, event):
        screen = event.position()
        before = Point((screen.x()-self.offset.x())/self.scale, (self.offset.y()-screen.y())/self.scale)
        self.scale = max(.05, min(200, self.scale * (1.2 if event.angleDelta().y() > 0 else 1/1.2)))
        self.offset = QPointF(screen.x()-before.x*self.scale, screen.y()+before.y*self.scale)
        self.update()

    def fit(self):
        points = []
        for e in self.window.doc.entities.values():
            if not self.window.doc.layers[e.layer].visible:
                continue
            points += ([e.start,e.end] if isinstance(e,Line) else list(e.vertices) if isinstance(e,Polyline) else
                       [Point(e.center.x-e.radius,e.center.y-e.radius), Point(e.center.x+e.radius,e.center.y+e.radius)])
        if points:
            left,right = min(p.x for p in points), max(p.x for p in points)
            bottom,top = min(p.y for p in points), max(p.y for p in points)
            self.scale = min((self.width()-100)/max(1,right-left), (self.height()-100)/max(1,top-bottom))
            self.offset = QPointF(self.width()/2 - (left+right)/2*self.scale,
                                  self.height()/2 + (bottom+top)/2*self.scale)
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.fillRect(self.rect(), QColor("#151c25"))
        step = 10*self.scale
        if self.grid and step >= 8:
            p.setPen(QPen(QColor("#253140"), 1))
            x = self.offset.x() % step
            while x < self.width():
                p.drawLine(QPointF(x,0), QPointF(x,self.height()))
                x += step
            y = self.offset.y() % step
            while y < self.height():
                p.drawLine(QPointF(0,y), QPointF(self.width(),y))
                y += step
        for e in self.window.doc.entities.values():
            layer = self.window.doc.layers[e.layer]
            if not layer.visible:
                continue
            p.setPen(QPen(QColor("#53c7ff" if e.id in self.window.selected else layer.color), 2))
            if isinstance(e,Line):
                p.drawLine(self.screen(e.start),self.screen(e.end))
            elif isinstance(e,Arc):
                rect=QRectF(self.screen(Point(e.center.x-e.radius,e.center.y+e.radius)),
                    self.screen(Point(e.center.x+e.radius,e.center.y-e.radius)))
                p.drawArc(rect,round(e.start_angle*16),round((e.end_angle-e.start_angle)%360*16))
            elif isinstance(e,Polyline):
                for a,b in zip(e.vertices,e.vertices[1:]): p.drawLine(self.screen(a),self.screen(b))
                if e.closed: p.drawLine(self.screen(e.vertices[-1]),self.screen(e.vertices[0]))
            else:
                p.drawEllipse(self.screen(e.center),e.radius*self.scale,e.radius*self.scale)
        if self.window.pending_points:
            p.setPen(QPen(QColor('#53c7ff'),1,Qt.PenStyle.DashLine))
            for a,b in zip(self.window.pending_points,self.window.pending_points[1:]):
                p.drawLine(self.screen(a),self.screen(b))
        if self.window.anchor and self.cursor:
            p.setPen(QPen(QColor("#53c7ff"),1,Qt.PenStyle.DashLine))
            if self.window.mode == "CIRCLE":
                r = hypot(self.cursor.x-self.window.anchor.x,self.cursor.y-self.window.anchor.y)*self.scale
                p.drawEllipse(self.screen(self.window.anchor),r,r)
            else:
                p.drawLine(self.screen(self.window.anchor),self.screen(self.cursor))
        if self.selection_start is not None and self.selection_end is not None:
            crossing=self.selection_end.x()<self.selection_start.x()
            color=QColor('#79daab' if crossing else '#53c7ff')
            p.setPen(QPen(color,1,Qt.PenStyle.DashLine if crossing else Qt.PenStyle.SolidLine))
            color.setAlpha(35); p.setBrush(color)
            p.drawRect(QRectF(self.selection_start,self.selection_end).normalized()); p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(QColor("#8fe4ae"),2))
        origin = self.screen(Point(0,0))
        p.drawLine(origin,origin+QPointF(45,0))
        p.drawText(origin+QPointF(48,4),"X")
        p.setPen(QPen(QColor("#f8c477"),2))
        p.drawLine(origin,origin+QPointF(0,-45))
        p.drawText(origin+QPointF(-4,-50),"Y")
        if self.cursor:
            at = self.screen(self.cursor)
            p.setPen(QPen(QColor("#c1d2e3"),1))
            p.drawLine(at-QPointF(12,0),at+QPointF(12,0))
            p.drawLine(at-QPointF(0,12),at+QPointF(0,12))
        p.end()


class MainWindow(QMainWindow):
    def __init__(self, document=None):
        super().__init__()
        self.doc = document if document is not None else Document()
        if document is not None:
            from .qcad_backend import QcadCommandBus
            self.bus = QcadCommandBus(self.doc)
        else:
            self.bus = CommandBus(self.doc)
        self.lisp = LispRuntime(self.bus)
        self.selected = set()
        self.mode = None
        self.anchor = None
        self.pending_points = []
        self.boundary_selection = set()
        self.offset_target = None
        self.offset_distance = None
        self.setWindowTitle("OPEN CAD 2D · Prototipo 0.1")
        if document is not None:
            self.setWindowTitle("OPEN CAD 2D · QCAD integrado experimental")
        self.resize(1360, 860)
        self.setStyleSheet("""
QMainWindow,QWidget {background:#252f3b;color:#e1e8ef;font-family:'Arial';font-size:12px;}
QPushButton {background:#344353;border:1px solid #465a70;border-radius:4px;padding:8px 14px;}
QPushButton:hover {background:#44617c;} QPushButton:checked {background:#23658c;}
QLineEdit,QPlainTextEdit,QListWidget {background:#18222e;border:1px solid #465a70;padding:5px;}
QTabBar::tab {padding:9px 20px;background:#293544;} QTabBar::tab:selected {background:#3d5268;}
QDockWidget::title {padding:7px;background:#344353;}
""")
        self.canvas = Canvas(self)
        self.canvas.clicked.connect(self.on_point)
        self.canvas.cancelled.connect(self.cancel)
        self.canvas.moved.connect(lambda v:self.coords.setText(f"X {v.x:.3f}   Y {v.y:.3f}   Z {v.z:.3f}"))
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0,0,0,0)
        self.ribbon = QTabWidget()
        self.ribbon.setMaximumHeight(140)
        home = QWidget()
        row = QHBoxLayout(home)
        for label, action in [("Línea",lambda:self.start("LINE")),("Círculo",lambda:self.start("CIRCLE")),
                ("Borrar",self.erase_selection),("Deshacer",lambda:self.execute("UNDO")),
                ("Rehacer",lambda:self.execute("REDO")),("Extensión",self.canvas.fit)]:
            b = QPushButton(label)
            b.clicked.connect(action)
            row.addWidget(b)
        if document is not None:
            move=QPushButton('Mover selección'); move.clicked.connect(self.start_move); row.addWidget(move)
            curves=QWidget(); curve_row=QHBoxLayout(curves)
            for label,action in [('Arco 3 puntos',lambda:self.start('ARC')),('Polilínea',lambda:self.start('PLINE')),
                    ('Finalizar polilínea',lambda:self.finish_polyline(False)),('Cerrar polilínea',lambda:self.finish_polyline(True))]:
                button=QPushButton(label); button.clicked.connect(action); curve_row.addWidget(button)
            curve_row.addStretch()
            modify=QWidget(); modify_row=QHBoxLayout(modify)
            for label,action in [('Recortar',lambda:self.start_cut('TRIM')),('Alargar',lambda:self.start_cut('EXTEND')),('Desfase',self.start_offset)]:
                button=QPushButton(label); button.clicked.connect(action); modify_row.addWidget(button)
            modify_row.addStretch()
        row.addStretch()
        self.ribbon.addTab(home,"Inicio")
        files = QWidget()
        row = QHBoxLayout(files)
        for label, action in [("Abrir DXF",self.open_file),("Guardar DXF",self.save_file),("Cargar LSP",self.load_lsp),("Alias JSON",self.load_aliases)]:
            b = QPushButton(label)
            b.clicked.connect(action)
            row.addWidget(b)
        row.addStretch()
        self.ribbon.addTab(files,"Archivo y extensiones")
        if document is not None: self.ribbon.addTab(curves,'Curvas 2D')
        if document is not None: self.ribbon.addTab(modify,'Modificar 2D')
        layout.addWidget(self.ribbon)
        self.drawing_tabs = QTabWidget()
        self.drawing_tabs.addTab(self.canvas,"Dibujo1 · Modelo")
        layout.addWidget(self.drawing_tabs,1)
        tabs = QHBoxLayout()
        model = QPushButton("Modelo")
        model.setCheckable(True)
        model.setChecked(True)
        tabs.addWidget(model)
        future = QLabel("Presentaciones: siguiente etapa")
        tabs.addWidget(future)
        tabs.addStretch()
        layout.addLayout(tabs)
        self.setCentralWidget(central)
        self.history = QPlainTextEdit()
        self.history.setReadOnly(True)
        self.history.setMaximumBlockCount(500)
        self.entry = QLineEdit()
        self.entry.setObjectName("commandEntry")
        self.entry.setPlaceholderText("Comando: LINE 0,0 120,0 · CIRCLE 60,40 18 · LAYER NEW Ejes")
        self.entry.returnPressed.connect(self.submit)
        console = QWidget()
        stack = QVBoxLayout(console)
        stack.addWidget(self.history)
        stack.addWidget(self.entry)
        self.console = self.dock("Línea de comandos",console,Qt.DockWidgetArea.BottomDockWidgetArea)
        self.console.setMinimumHeight(170)
        self.layers = QListWidget()
        self.layers.currentTextChanged.connect(self.set_layer)
        self.dock("Capas",self.layers,Qt.DockWidgetArea.RightDockWidgetArea)
        self.properties = PropertiesPanel(self)
        self.dock("Propiedades",self.properties,Qt.DockWidgetArea.RightDockWidgetArea)
        self.coords = QLabel("X 0.000   Y 0.000   Z 0.000")
        self.statusBar().addWidget(self.coords,1)
        for label, attr in [("REJILLA","grid"),("SNAP 10","snap")]:
            b = QPushButton(label)
            b.setCheckable(True)
            b.setChecked(getattr(self.canvas,attr))
            b.toggled.connect(lambda state,a=attr:self.toggle(a,state))
            self.statusBar().addPermanentWidget(b)
        for shortcut, action in [("Escape",self.cancel),("Ctrl+Z",lambda:self.execute("UNDO")),("Ctrl+Y",lambda:self.execute("REDO"))]:
            a = QAction(self)
            a.setShortcut(QKeySequence(shortcut))
            a.triggered.connect(action)
            self.addAction(a)
        self.refresh()
        capabilities = ("Documento QCAD experimental. LINE/CIRCLE/ARC y PLINE recta. DXF R2000/R2010 limitado; guardado R2010."
                        if document is not None else
                        "OPEN CAD 2D · LINE/CIRCLE y operaciones básicas. DXF limitado a LINE/CIRCLE.")
        self.history.appendPlainText(capabilities+"\nLSP: subconjunto documentado. Escape cancela herramienta; rueda amplía.")

    def dock(self,title,widget,area):
        d = QDockWidget(title,self)
        d.setWidget(widget)
        self.addDockWidget(area,d)
        return d

    def toggle(self,attr,state):
        setattr(self.canvas,attr,state)
        self.canvas.update()

    def refresh(self):
        self.selected.intersection_update(self.doc.entities)
        self.layers.blockSignals(True)
        self.layers.clear()
        for name in self.doc.layers:
            self.layers.addItem(name)
        self.layers.setCurrentRow(list(self.doc.layers).index(self.doc.current_layer))
        self.layers.blockSignals(False)
        info = [repr(self.doc.entities[i]) for i in sorted(self.selected)]
        self.properties.setPlainText("\n".join(info) if info else f"{len(self.doc.entities)} entidades\nCapa actual: {self.doc.current_layer}\nSeleccione una entidad para consultar sus atributos.")
        self.properties.refresh()
        self.canvas.update()

    def set_layer(self,name):
        if name:
            self.execute('LAYER SET ' + json.dumps(name,ensure_ascii=False))

    def execute(self,text):
        try:
            result = self.bus.execute_text(text)
            self.history.appendPlainText("> " + text + ("\n"+str(result) if result is not None else ""))
            self.refresh()
            return True
        except (ValueError,KeyError,TypeError,ArithmeticError,RuntimeError) as e:
            self.history.appendPlainText("Error: " + str(e))
            return False

    def submit(self):
        text = self.entry.text().strip()
        self.entry.clear()
        if self.mode=='PLINE' and text.upper() in ('','C','CLOSE'):
            self.finish_polyline(bool(text))
        elif text.upper() in ("LINE","L","CIRCLE","C","ARC","A","PLINE","PL") and self.bus.aliases.get(text.upper(),text.upper()) in self.bus.definitions:
            self.start(self.bus.aliases.get(text.upper(),text.upper()))
        elif text.startswith("("):
            try:
                self.lisp.run(text)
                self.history.appendPlainText("> " + text)
                self.refresh()
            except Exception as e:
                self.history.appendPlainText("LSP: " + str(e))
        else:
            self.execute(text)

    def start(self,mode):
        self.mode,self.anchor = mode,None
        self.pending_points=[]
        self.boundary_selection=set(); self.offset_target=None
        self.history.appendPlainText(mode + ": indique primer punto o centro. Escape cancela.")
        if mode=='PLINE': self.history.appendPlainText('PLINE recta: puntos sucesivos; Finalizar/Enter confirma, Cierra con CLOSE. Escape descarta el lote.')
        if mode=='ARC': self.history.appendPlainText('ARC: punto inicial, intermedio y final, en ese orden.')
        self.canvas.setFocus()
        self.canvas.update()

    def cancel(self):
        if self.mode is None: self.selected.clear(); self.refresh()
        self.mode,self.anchor = None,None
        self.pending_points=[]
        self.boundary_selection=set(); self.offset_target=None
        self.canvas.selection_start=self.canvas.selection_end=None
        self.canvas.update()

    def start_move(self):
        if self.selected:
            self.start('MOVE')
            self.history.appendPlainText('MOVE: punto base y destino de la selección')

    def finish_polyline(self,closed):
        if self.mode!='PLINE': return
        coordinates=' '.join(f'{p.x},{p.y},{p.z}' for p in self.pending_points)
        if self.execute('PLINE '+coordinates+(' CLOSE' if closed else '')): self.cancel()

    def start_cut(self,mode):
        if not self.selected:
            self.history.appendPlainText(mode+': seleccione las aristas límite y vuelva a pulsar la herramienta'); return
        boundaries=set(self.selected); self.start(mode); self.boundary_selection=boundaries
        self.history.appendPlainText(mode+': pulse la porción de LINE a retirar o el extremo a alargar. Límites finitos en XY; Escape termina.')

    def start_offset(self):
        distance,accepted=QInputDialog.getDouble(self,'Desfase','Distancia positiva',1,0,1e12,6)
        if not accepted: return
        if distance<=0: self.history.appendPlainText('OFFSET: distancia positiva requerida'); return
        self.start('OFFSET'); self.offset_distance=distance
        self.history.appendPlainText('OFFSET: pulse LINE/CIRCLE/ARC y después un punto del lado. Escape cancela.')

    def merge_selection(self,ids,modifiers):
        if modifiers & Qt.KeyboardModifier.ShiftModifier: self.selected.difference_update(ids)
        elif modifiers & Qt.KeyboardModifier.ControlModifier: self.selected.symmetric_difference_update(ids)
        else: self.selected.update(ids)
        self.refresh()

    def select_region(self,mode,a,b,modifiers=Qt.KeyboardModifier.NoModifier):
        try: self.merge_selection(self.doc.select(mode,a,b),modifiers)
        except (ValueError,RuntimeError) as error: self.history.appendPlainText('Error de selección: '+str(error))

    def on_point(self,p,modifiers=Qt.KeyboardModifier.NoModifier):
        if self.mode:
            if self.mode in ('TRIM','EXTEND','OFFSET'):
                try:
                    tolerance=8/self.canvas.scale
                    if self.mode=='OFFSET' and self.offset_target is not None:
                        if self.execute(f'OFFSET {self.offset_target} {self.offset_distance} {p.x},{p.y},{p.z}'): self.cancel()
                    else:
                        targets=self.doc.select('point',p,tolerance=tolerance)-self.boundary_selection
                        if not targets: raise ValueError('No hay un objetivo válido en el punto')
                        target=min(targets)
                        if self.mode=='OFFSET':
                            self.offset_target=target; self.history.appendPlainText('OFFSET: indique el lado de la copia')
                        else:
                            ids=','.join(str(i) for i in sorted(self.boundary_selection))
                            self.execute(f'{self.mode} {ids} {target} {p.x},{p.y},{p.z} {tolerance}')
                except (ValueError,RuntimeError) as error: self.history.appendPlainText('Error: '+str(error))
                return
            if self.mode in ('ARC','PLINE'):
                self.pending_points.append(p); self.anchor=p
                if self.mode=='ARC' and len(self.pending_points)==3:
                    coordinates=' '.join(f'{v.x},{v.y},{v.z}' for v in self.pending_points)
                    if self.execute('ARC '+coordinates): self.cancel()
                    else: self.pending_points=[]; self.anchor=None
                self.canvas.update(); return
            if self.anchor is None:
                self.anchor = p
            else:
                a = self.anchor
                if self.mode == 'MOVE':
                    ids=','.join(str(i) for i in sorted(self.selected))
                    if self.execute(f'MOVE {ids} {p.x-a.x},{p.y-a.y},{p.z-a.z}'):
                        self.mode,self.anchor=None,None
                elif self.mode == "LINE":
                    if self.execute(f"LINE {a.x},{a.y},{a.z} {p.x},{p.y},{p.z}"):
                        self.anchor = p
                else:
                    if self.execute(f"CIRCLE {a.x},{a.y},{a.z} {hypot(p.x-a.x,p.y-a.y)}"):
                        self.cancel()
            self.canvas.update()
            return
        if hasattr(self.doc,'select'):
            try: self.merge_selection(self.doc.select('point',p,tolerance=8/self.canvas.scale),modifiers)
            except (ValueError,RuntimeError) as error: self.history.appendPlainText('Error de selección: '+str(error))
            return
        nearest, distance = None,8/self.canvas.scale
        for e in self.doc.entities.values():
            if not self.doc.layers[e.layer].visible:
                continue
            if isinstance(e,Circle):
                d = abs(hypot(p.x-e.center.x,p.y-e.center.y)-e.radius)
            else:
                dx,dy = e.end.x-e.start.x,e.end.y-e.start.y
                t = max(0,min(1,((p.x-e.start.x)*dx+(p.y-e.start.y)*dy)/(dx*dx+dy*dy))) if dx or dy else 0
                d = hypot(p.x-e.start.x-t*dx,p.y-e.start.y-t*dy)
            if d < distance:
                nearest,distance = e.id,d
        self.selected = {nearest} if nearest is not None else set()
        self.refresh()

    def erase_selection(self):
        if self.selected:
            self.execute("ERASE " + ",".join(str(i) for i in sorted(self.selected)))

    def dialog_error(self,action,e):
        QMessageBox.warning(self,action,str(e))

    def open_file(self):
        path,_ = QFileDialog.getOpenFileName(self,"Abrir DXF",filter="DXF (*.dxf)")
        if path:
            try:
                if not isinstance(self.doc,Document):
                    answer=QMessageBox.question(self,"Abrir DXF experimental",
                        "LINE/CIRCLE/ARC y PLINE recta sin anchura, capas y unidades del subconjunto documentado. "
                        "Tablas estándar y handles se regeneran al guardar. "
                        "Abrir sustituye el dibujo activo y su historial. ¿Continuar?",
                        QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No,QMessageBox.StandardButton.No)
                    if answer!=QMessageBox.StandardButton.Yes:
                        return
                    self.doc.open_dxf(path)
                    self.selected.clear()
                else:
                    new = load_dxf(path)
                    # Keep a replacement undoable in the temporary model.
                    with self.doc.transaction():
                        self.doc.restore(new.snapshot())
                self.cancel()
                self.refresh()
                self.canvas.fit()
            except Exception as e:
                self.dialog_error("Abrir DXF",e)

    def save_file(self):
        path,_ = QFileDialog.getSaveFileName(self,"Guardar DXF",filter="DXF (*.dxf)")
        if path:
            try:
                if not isinstance(self.doc,Document):
                    self.doc.save_dxf(path if Path(path).suffix else path+".dxf")
                    self.history.appendPlainText("DXF R2010 verificado: LINE/CIRCLE/ARC y PLINE recta, capas y unidades; tablas estándar regeneradas.")
                else:
                    save_dxf(self.doc,path if Path(path).suffix else path+".dxf")
                self.history.appendPlainText("Guardado: " + path)
            except Exception as e:
                self.dialog_error("Guardar DXF",e)

    def load_lsp(self):
        path,_ = QFileDialog.getOpenFileName(self,"Cargar LSP",filter="AutoLISP (*.lsp *.LSP)")
        if path:
            try:
                self.lisp.load(path)
                self.history.appendPlainText("LSP cargado: " + path)
                self.refresh()
            except Exception as e:
                self.dialog_error("AutoLISP",e)

    def load_aliases(self):
        path,_ = QFileDialog.getOpenFileName(self,"Alias",filter="JSON (*.json)")
        if path:
            try:
                self.bus.set_aliases(json.loads(Path(path).read_text(encoding="utf-8")))
            except Exception as e:
                self.dialog_error("Alias",e)

    def closeEvent(self,event):
        if not isinstance(self.doc,Document):
            self.doc.close()
        super().closeEvent(event)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke-test", type=Path)
    parser.add_argument("--qcad",action='store_true',help='Adaptador QCAD experimental compilado en este proyecto')
    args = parser.parse_args()
    app = QApplication.instance() or QApplication(sys.argv[:1])
    if not QFontDatabase.families():
        # Offscreen Windows may not enumerate system fonts. Load an existing OS
        # font for rendering only; no proprietary font is shipped with OPEN CAD.
        for font in (Path(os.environ.get("WINDIR","C:/Windows"))/"Fonts/arial.ttf",
                     Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")):
            if font.is_file() and QFontDatabase.addApplicationFont(str(font)) >= 0:
                app.setFont(QFont("Arial" if sys.platform=="win32" else "DejaVu Sans",10))
                break
    if args.qcad:
        if args.smoke_test:
            parser.error('Usar el fixture funcional QCAD; el smoke temporal no acredita ese backend')
        from .qcad_backend import QcadDocument
        root=Path(__file__).resolve().parents[2]
        doc=QcadDocument(root/'build/native/opencad-qcad-engine.exe',root/'.cache/upstream/qcad',root/'.cache/qt/6.10.3/msvc2022_64')
        window=MainWindow(doc)
    else:
        window = MainWindow()
    if args.smoke_test:
        window.lisp.run('(command "LINE" \'(0 0 2) \'(120 0 2) \'(120 80 2) \'(0 80 2) \'(0 0 2)) (command "CIRCLE" \'(60 40 2) 18)')
        window.refresh()
        window.show()
        app.processEvents()
        window.canvas.fit()
        app.processEvents()
        args.smoke_test.mkdir(parents=True,exist_ok=True)
        if not window.grab().save(str(args.smoke_test / "prototype.png")):
            raise RuntimeError("No se pudo guardar la captura")
        save_dxf(window.doc,args.smoke_test / "smoke.dxf")
        reopened = load_dxf(args.smoke_test / "smoke.dxf")
        assert list(reopened.entities.values()) == list(window.doc.entities.values())
        (args.smoke_test / "smoke.json").write_text(json.dumps({"entities":len(reopened.entities),"qt":True,"dxf_roundtrip":True,"qcad_integrated":False},indent=2)+"\n")
        window.close()
        return 0
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
