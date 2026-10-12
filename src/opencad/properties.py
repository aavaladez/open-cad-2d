"""Original property panel, editing only through the authoritative command bus."""
from PySide6.QtWidgets import QWidget,QVBoxLayout,QFormLayout,QLineEdit,QComboBox,QPushButton,QPlainTextEdit
from .model import Line,Circle
from .commands import point


class PropertiesPanel(QWidget):
    def __init__(self,window):
        super().__init__(); self.window=window
        layout=QVBoxLayout(self); self.summary=QPlainTextEdit(); self.summary.setReadOnly(True)
        self.summary.setMaximumHeight(90); layout.addWidget(self.summary)
        form=QFormLayout(); layout.addLayout(form); self.fields={}
        for key,label in [('start','Inicio XYZ'),('end','Fin XYZ'),('center','Centro XYZ'),('radius','Radio')]:
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
            field.clear(); field.setEnabled(False)
        if len(selected)==1:
            e=selected[0]
            values={'start':e.start,'end':e.end} if isinstance(e,Line) else {'center':e.center,'radius':e.radius}
            for key,value in values.items():
                text=','.join(format(v,'.17g') for v in (value.x,value.y,value.z)) if key!='radius' else format(value,'.17g')
                self.fields[key].setText(text); self.fields[key].setEnabled(enabled); self.original[key]=text
        self.layer.setEnabled(enabled); self.apply.setEnabled(enabled)

    def submit(self):
        try:
            changes={}
            for key,field in self.fields.items():
                if field.isEnabled() and field.text()!=self.original[key]:
                    value=float(field.text()) if key=='radius' else point(field.text())
                    changes[key]=value if key=='radius' else [value.x,value.y,value.z]
            if self.layer.currentText()!=self.original['layer']:
                changes['layer']=self.layer.currentText()
            if changes:
                self.window.bus.edit_properties(self.window.selected,changes)
                self.window.history.appendPlainText('Propiedades aplicadas a '+str(len(self.window.selected))+' entidades')
                self.window.refresh()
        except (ValueError,RuntimeError,TypeError,KeyError) as error:
            self.window.history.appendPlainText('Error de propiedades: '+str(error))
