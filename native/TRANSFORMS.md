# Modificación esencial QCAD — 2026-10-12

Módulo incremental sobre propiedades/selección, sin extender el motor Python temporal.
QcadCommandBus registra COPY/CO, ROTATE/RO y SCALE/SC sólo en el modo QCAD. Los aliases
personalizados pasan por el mismo registro. El prototipo temporal los sigue rechazando.

Consola: COPY ids dx,dy,dz; ROTATE ids baseXYZ grados; SCALE ids baseXYZ factor.
Separar varios IDs con coma. Operaciones QCAD sobre clones, validación del lote y una
transacción. COPY crea nuevas entidades mediante constructores públicos que conservan
RLineData/RCircleData; los originales permanecen intactos y el bus devuelve nuevos IDs.
No alterar interfaces protegidas upstream para cambiar IDs.

ROTATE gira en XY alrededor de la base, ángulo positivo antihorario; SCALE aplica un
factor positivo uniforme en XY. Z permanece como atributo original, incluso con base
de Z distinta. COPY sí admite desplazamiento XYZ. Ésta es la variante 2D autorizada,
no una transformación 3D equivalente en todas las opciones de AutoCAD.

Todas las fuentes deben estar en capas desbloqueadas. Rechazar selección vacía/ID
desconocido, números no finitos, escala cero/negativa y geometría degenerada o desbordada.
La validación geométrica también protege el commit de MOVE/propiedades. Undo/redo
corresponde a toda la selección; errores conservan geometría e historial redo.

Pendientes: Multiple/Array de COPY, Reference/Copy de ROTATE/SCALE, herramientas de
ratón específicas y otros tipos de entidad. COMMAND del intérprete LSP mantiene su
lista acotada anterior; no se declara soporte LSP de estas tres operaciones todavía.

## Evidencia funcional

```powershell
./tools/build_qcad.ps1
python tools/check_qcad_transforms.py --binary build/native/opencad-qcad-engine.exe --source .cache/upstream/qcad --qt .cache/qt/6.10.3/msvc2022_64 --output build/transforms
ctest --test-dir build/native --output-on-failure
```

23 comprobaciones por runtime Python 3.12/3.14 en Windows. Baseline original: línea
(0,0,7)→(3,4,9), círculo (10,20,9), radio 3. COPY delta (10,2,5) produce extremos
(10,2,12)→(13,6,14); ROTATE 90 produce fin (-4,3,9); SCALE factor 2 con base (1,2,100)
produce extremos (-1,-2,7)→(5,6,9) y círculo (19,38,9), radio 6. Tolerancia 1e-9.
Incluye aliases, nuevas identidades/originales intactos, historial, errores/capas,
consola real QtTest y DXF guardado/reabierto con contraste ezdxf. CTest 7/7; conserva
las suites anteriores de propiedades, AutoLISP, DXF, geometría y 46 tests Python.

Referencia pública para los contratos de base/ángulo/factor:
[ROTATE/SCALE](https://help.autodesk.com/cloudhelp/2025/ENU/AutoCAD-DidYouKnow/files/GUID-D988658E-0A92-4353-B614-6C30CF6281A2.htm).
Los resultados son analíticos y del motor QCAD; no corpus ejecutado en AutoCAD.
Continúa evidencia de desarrollo parcial, sin instalación ni aceptación A1.
