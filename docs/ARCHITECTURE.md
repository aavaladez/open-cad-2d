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
localmente y probó geometría/Z y documentos; el adaptador de aplicación experimental
posterior se describe en native/ADAPTER.md y ADR-012.

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

## Adaptador experimental comprobado

La UI Python/Qt existente puede arrancar con --qcad. Un proceso C++ local posee
el único RDocument autoritativo. El bus/LSP intercambia JSON mediante pipes; Python
sólo conserva vistas descartables para canvas/selección/propiedades. Cada comando o
LSP confirma una transacción QCAD; staging de objetos QCAD permite rollback sin
perder redo. No existe sincronización entre dos documentos editables divergentes.
LINE/CIRCLE/MOVE/ERASE/capas probados; ciclo DXF UI posterior experimental probado;
despliegue nativo pendiente. Abrir valida en otro proceso y sustituye el candidato
sólo tras contraste independiente; guardar valida temporal CE y canonicaliza R2010
con ezdxf antes de os.replace. Ver native/DXF_APPLICATION.md y sus límites explícitos.
No comprometer ABI de extensiones. Ver native/ADAPTER.md para límites/performance.

## Seguridad del intérprete

LSP sin eval/exec, shell, red, COM o I/O desde el código interpretado. Límites
de tamaño, profundidad y pasos; rollback completo en fallo. No constituye un
aislamiento del sistema operativo. Nuevas capacidades deben diseñarse explícitamente.
Compatibilidad .NET/ARX/VBA del Excel necesita contratos equivalentes y auditoría
antes de decidir qué APIs abiertas pueden implementarla; no prometer carga binaria Autodesk.

## Control de entrada a auditoría A1

La candidata debe demostrar un único documento autoritativo QCAD compartido por
UI, comandos, AutoLISP y DXF; un test del core aislado no acredita integración.
Vincular evidencias funcionales al mismo commit/binario instalado, fixtures y
versiones. Aplicar [AUDIT_GATE.md](AUDIT_GATE.md). Al verificar sus seis puntos,
congelar candidata y limitar cambios a auditoría/correcciones. La siguiente fase
necesita ausencia de bloqueantes y aprobación explícita del director.
