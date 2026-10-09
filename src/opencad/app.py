"""Qt desktop prototype. A temporary shell to validate command workflows."""
import argparse
import json
import os
import sys
from pathlib import Path
from math import hypot
from PySide6.QtCore import Qt, QPointF, Signal
from PySide6.QtGui import QColor, QPainter, QPen, QKeySequence, QAction, QFontDatabase, QFont
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QTabWidget, QPushButton, QLabel, QDockWidget, QPlainTextEdit,
    QLineEdit, QListWidget, QFormLayout, QFileDialog, QMessageBox)
from .model import Document, Point, Line, Circle
from .commands import CommandBus
from .lisp import LispRuntime
from .interop import load_dxf, save_dxf


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
            self.clicked.emit(self.world(event.position()))
        elif event.button() == Qt.MouseButton.RightButton:
            self.cancelled.emit()

    def mouseMoveEvent(self, event):
        self.cursor = self.world(event.position())
        self.moved.emit(self.cursor)
        self.update()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.cancelled.emit()
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
            points += ([e.start,e.end] if isinstance(e,Line) else
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
            else:
                p.drawEllipse(self.screen(e.center),e.radius*self.scale,e.radius*self.scale)
        if self.window.anchor and self.cursor:
            p.setPen(QPen(QColor("#53c7ff"),1,Qt.PenStyle.DashLine))
            if self.window.mode == "CIRCLE":
                r = hypot(self.cursor.x-self.window.anchor.x,self.cursor.y-self.window.anchor.y)*self.scale
                p.drawEllipse(self.screen(self.window.anchor),r,r)
            else:
                p.drawLine(self.screen(self.window.anchor),self.screen(self.cursor))
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
    def __init__(self):
        super().__init__()
        self.doc = Document()
        self.bus = CommandBus(self.doc)
        self.lisp = LispRuntime(self.bus)
        self.selected = set()
        self.mode = None
        self.anchor = None
        self.setWindowTitle("OPEN CAD 2D · Prototipo 0.1")
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
        self.properties = QPlainTextEdit()
        self.properties.setReadOnly(True)
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
        self.history.appendPlainText("OPEN CAD 2D · LINE/CIRCLE y operaciones básicas. DXF limitado a LINE/CIRCLE.\nLSP: subconjunto documentado. Escape cancela herramienta; rueda amplía.")

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
        except (ValueError,KeyError,TypeError,ArithmeticError) as e:
            self.history.appendPlainText("Error: " + str(e))
            return False

    def submit(self):
        text = self.entry.text().strip()
        self.entry.clear()
        if text.upper() in ("LINE","L","CIRCLE","C"):
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
        self.history.appendPlainText(mode + ": indique primer punto o centro. Escape cancela.")
        self.canvas.setFocus()
        self.canvas.update()

    def cancel(self):
        self.mode,self.anchor = None,None
        self.canvas.update()

    def on_point(self,p):
        if self.mode:
            if self.anchor is None:
                self.anchor = p
            else:
                a = self.anchor
                if self.mode == "LINE":
                    if self.execute(f"LINE {a.x},{a.y},{a.z} {p.x},{p.y},{p.z}"):
                        self.anchor = p
                else:
                    if self.execute(f"CIRCLE {a.x},{a.y},{a.z} {hypot(p.x-a.x,p.y-a.y)}"):
                        self.cancel()
            self.canvas.update()
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
                new = load_dxf(path)
                # Keep a replacement undoable to prevent discarding the current drawing.
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke-test", type=Path)
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
