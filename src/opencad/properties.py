"""Original property panel, editing only through the authoritative command bus."""
from PySide6.QtWidgets import QWidget,QVBoxLayout,QFormLayout,QLineEdit,QComboBox,QPushButton,QPlainTextEdit
from .model import Line,Circle
from .qcad_views import Arc,Polyline,Dimension
from .commands import point


class PropertiesPanel(QWidget):
    def __init__(self,window):
        super().__init__(); self.window=window
        layout=QVBoxLayout(self); self.summary=QPlainTextEdit(); self.summary.setReadOnly(True)
        self.summary.setMaximumHeight(90); layout.addWidget(self.summary)
        form=QFormLayout(); self.form=form; layout.addLayout(form); self.fields={}
        for key,label in [('start','Inicio XYZ'),('end','Fin XYZ'),('center','Centro XYZ'),('radius','Radio'),
                ('start_angle','Ángulo inicial °'),('end_angle','Ángulo final °'),
                ('vertices','Vértices XYZ; XYZ'),('elevation','Elevación'),('closed','Cerrada true/false'),
                ('position','Definición XYZ'),('chord','Punto de radio XYZ'),('angle','Dirección de cota °'),('text','Texto de cota')]:
            edit=QLineEdit(); edit.setObjectName('property_'+key); form.addRow(label,edit); self.fields[key]=edit
        self.layer=QComboBox(); self.layer.setObjectName('property_layer'); form.addRow('Capa',self.layer)
        self.apply=QPushButton('Aplicar propiedades'); self.apply.clicked.connect(self.submit); layout.addWidget(self.apply)
        layout.addStretch(); self.original={}

    def toPlainText(self): return self.summary.toPlainText()

    def setPlainText(self,text): self.summary.setPlainText(text)

    def refresh(self):
        doc=self.window.doc; selected=[doc.entities[i] for i in sorted(self.window.selected)]
        enabled=hasattr(self.window.bus,'edit_properties') and bool(selected)
        self.original={}; self.layer.clear(); self.layer.addItem(''); self.layer.addItems(list(doc.layers))
        self.layer.setCurrentText(selected[0].layer if selected and len({e.layer for e in selected})==1 else '')
        self.original['layer']=self.layer.currentText()
        for key,field in self.fields.items():
            field.clear(); field.setEnabled(False); self.form.setRowVisible(field,False)
        if len(selected)==1:
            e=selected[0]
            if isinstance(e,Dimension):
                values={'position':e.position,'text':e.text}
                if e.start is not None: values.update(start=e.start,end=e.end)
                if e.chord is not None: values['chord']=e.chord
                if e.angle is not None: values['angle']=e.angle
            elif isinstance(e,Line): values={'start':e.start,'end':e.end}
            elif isinstance(e,Polyline): values={'vertices':e.vertices,'elevation':e.vertices[0].z,'closed':e.closed}
            else:
                values={'center':e.center,'radius':e.radius}
                if isinstance(e,Arc): values.update(start_angle=e.start_angle,end_angle=e.end_angle)
            for key,value in values.items():
                if key in ('start','end','center','position','chord'): text=','.join(format(v,'.17g') for v in (value.x,value.y,value.z))
                elif key=='text': text=value
                elif key=='vertices': text='; '.join(','.join(format(v,'.17g') for v in (p.x,p.y,p.z)) for p in value)
                elif key=='closed': text=str(value).lower()
                else: text=format(value,'.17g')
                self.fields[key].setText(text); self.fields[key].setEnabled(enabled); self.form.setRowVisible(self.fields[key],True); self.original[key]=text
        self.layer.setEnabled(enabled); self.apply.setEnabled(enabled)

    def submit(self):
        try:
            changes={}
            for key,field in self.fields.items():
                if field.isEnabled() and field.text()!=self.original[key]:
                    if key in ('radius','start_angle','end_angle','elevation','angle'): changes[key]=float(field.text())
                    elif key=='text': changes[key]=field.text()
                    elif key=='closed':
                        if field.text().strip().lower() not in ('true','false'): raise ValueError('Cerrada: true o false requerido')
                        changes[key]=field.text().strip().lower()=='true'
                    elif key=='vertices':
                        changes[key]=[[p.x,p.y,p.z] for p in map(point,field.text().split(';'))]
                    else:
                        p=point(field.text()); changes[key]=[p.x,p.y,p.z]
            if self.layer.currentText()!=self.original['layer']:
                changes['layer']=self.layer.currentText()
            if changes:
                self.window.bus.edit_properties(self.window.selected,changes)
                self.window.history.appendPlainText('Propiedades aplicadas a '+str(len(self.window.selected))+' entidades')
                self.window.refresh()
        except (ValueError,RuntimeError,TypeError,KeyError) as error:
            self.window.history.appendPlainText('Error de propiedades: '+str(error))
