# Adaptador de aplicación QCAD — experimental

La UI existente, CommandBus y el intérprete LSP utilizan un documento C++ QCAD
autoritativo. `native/adapter/session.cpp` posee RDocumentInterface/documento;
`server.cpp` recibe JSON por stdin y devuelve snapshots por stdout. No hay puerto
de red, shell ni descubrimiento de plugins. Se registran sólo factories DXF CE.

`src/opencad/qcad_backend.py` arranca el proceso auditado y comprueba protocolo/pin.
Las dataclasses Python son proyecciones descartables para dibujar/seleccionar;
modificarlas no modifica QCAD. LINE/CIRCLE/MOVE/ERASE y capas mutan objetos QCAD.
DIST sigue siendo cálculo analítico de puntos en el bus, sin editar geometría.

## Transacciones y ownership

begin clona objetos QCAD en staging C++; no altera el documento ni su historial.
commit aplica una única ROperation/RTransaction y devuelve IDs persistentes.
rollback descarta staging; el redo previo permanece disponible tras un LSP fallido.
El LSP usa transacciones anidadas en el puente: sólo el nivel exterior confirma.
Crear capa, dibujar y bloquearla en un script comparte la misma transacción.
La operación permite las banderas finales de capa después de validar cada edición
contra el bloqueo vigente en staging; no se eliminan controles de permisos del editor.
RDocumentInterface posee RDocument; applyOperation posee/elimina la operación.

## Ejecutar en el checkout Windows

Compilar según M1.md, instalar dependencias de pyproject.toml y ejecutar:

```powershell
python -m opencad.app --qcad
python tools/check_qcad_application.py --binary build/native/opencad-qcad-engine.exe --source .cache/upstream/qcad --qt .cache/qt/6.10.3/msvc2022_64 --output build/qcad-ui
ctest --test-dir build/native --output-on-failure
```

El modo sin --qcad conserva el prototipo temporal. El modo QCAD falla explícitamente
si falta el binario o termina el proceso; no cambia silenciosamente al motor Python.
Las rutas SDK/checkout son de desarrollo; distribución portátil nativa pendiente.

## Evidencia funcional local

26 comprobaciones en Windows con Python 3.12 y 3.14: alias LINE con XYZ/undo, IDs,
rollback LSP y conservación redo, capa nueva/bloqueada/undo en un lote, resultado
numérico personalizado, rutina propia .LSP, consola, Ribbon/ratón, Escape, selección
y propiedades de lectura. El diálogo de selección de LSP se sustituye por una ruta
determinista; el botón, carga y ejecución posteriores sí se ejercitan con QtTest.
Screenshot inspeccionada; reports/PNG en docs/evidence/qcad-application*.
Regresión 41 tests por runtime; CTest 4/4 suites. No comparación ejecutada en AutoCAD.

## Límites y siguiente paso

DXF UI deshabilitado explícitamente hasta implementar preflight/conservación,
importación temporal y confirmación segura. Las primitivas load/save del protocolo
nativo son internas, sin garantía general de conservación: sólo LINE/CIRCLE XY+Z.
No usar con archivos de producción. Falta edición de propiedades, selección múltiple,
ARC/PLINE/cotas y las variantes del catálogo. Cero requisitos declarados completos.

Staging y snapshot son O(N); respuestas limitadas a 4 MB y timeout 15 s.
Un timeout cierra el motor; no hay autosave/recuperación, grandes dibujos no probados.
No hay instalador nativo ni prueba de DPI/accesibilidad/equipo limpio. Estos riesgos
deben resolverse antes de A1. La lectura getline del servidor limita tamaño después
de leer; el cliente limita solicitudes a 1 MB, sin afirmar sandbox de sistema.

Esta evidencia es application_integration_partial, installed=false, no una candidata
A1: 0/6 criterios acreditados integralmente. Continuar roadmap sin congelar todavía.
