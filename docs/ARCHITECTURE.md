# Arquitectura

## Base seleccionada

QCAD Community, commit `4c830eb4d80285ca64b1f2c2dc0987f729344126`, para
integración progresiva del motor y documentos. Ver AUDIT.md y DECISIONS.md.
LibreCAD 3 queda como alternativa auditada. No incorporar plugins comerciales.

## Destino C++/Qt

UI Qt Widgets original → CommandBus/estado interactivo → operaciones transaccionales
→ adaptador QCAD (RDocument/RDocumentInterface/RStorage/RSpatialIndex).
El puente AutoLISP usa el mismo catálogo y operaciones. Los backends de archivo
informan capacidades y pérdidas antes de cargar/guardar. La UI no calcula geometría
profesional por su cuenta. Extensiones abiertas con manifest/versiones API.

No comprometer ABI de plugins o formato propio antes del primer adaptador probado.
RPluginInterface es un punto de extensión real de QCAD; su uso por OPEN CAD aún pendiente.
Qt 6 es objetivo actual de ambas bases auditadas. CMake raíz ofrece build del
checkout CE fijado y CTest del prototipo. El spike posterior M1 compiló QCAD
localmente y probó geometría/Z en C++; el adaptador documental sigue pendiente.

## Prototipo temporal verificable

Python/PySide6 (Qt 6) permite probar en el entorno sin compilador C++. `model.py`
contiene Point/Line/Circle con Z, capas y snapshot transaccional; `commands.py`
resuelve aliases, valida y despacha; `lisp.py` interpreta subconjunto acotado;
`interop.py` usa ezdxf; `app.py` ofrece canvas, herramientas y docks.

CommandBus admite LINE, CIRCLE, MOVE, ERASE, LAYER, UNDO, REDO y DIST con variantes
acotadas. Abrir DXF sustituye el documento dentro de una transacción undoable.
Guardar escribe temporal en el directorio destino y reemplaza tras éxito.
Documento de referencia en memoria; sin índice espacial, precisión topológica
robusta, autosave, múltiples documentos ni grandes dibujos. No usarlo como motor definitivo.

## Migración

Primero reproducir fixtures actuales con QCAD; después portar catálogo/aliases,
undo y semántica LSP. Mantener casos analíticos como contrato independiente.
Reemplazar el backend del prototipo o portar su UI a C++ según el spike real;
no asumir que importar QCAD a Python es directo ni introducir dos documentos divergentes.

## Seguridad y extensibilidad

LSP sin eval/exec, shell, red, COM o I/O desde el código interpretado. Límites
de tamaño, profundidad y pasos; rollback completo en fallo. No constituye un
aislamiento del sistema operativo. Nuevas capacidades deben diseñarse explícitamente.
Compatibilidad .NET/ARX/VBA del Excel necesita contratos equivalentes y auditoría
antes de decidir qué APIs abiertas pueden implementarla; no prometer carga binaria Autodesk.
