# Estado verificable — 2026-10-09

M0 preparado para revisión. No hay declaración de paridad profesional ni de
compatibilidad completa con AutoCAD, AutoLISP, DXF o DWG.

## Regla permanente A1 y estado de entrada

Decisión del director incorporada: continuar hasta seis pruebas funcionales de
aplicación, después detener funciones nuevas, congelar candidata, auditar y PAUSAR
para aprobación explícita de la siguiente fase. No exige completar 472 requisitos.
Ver AUDIT_GATE.md, ADR-010 y requirements/audit-gate.json.

Entrada actual **0/6 acreditados integralmente**: QCAD documental, UI, comandos,
LSP y DXF parciales; Windows instalado pendiente. Esto no invalida pruebas
locales del prototipo/core; no las convierte en aceptación de aplicación instalada.
Seis skills revisadas y reutilizadas; cad-audit-gate añadida, validación estructural
aprobada. Regresión tras integración del controlador: 41/41 tests aprobados en
Python 3.14 y 3.12; diez tests nuevos verifican estados/rechazos con artefactos sintéticos,
sin acreditar funcionalidades CAD. Reportes de entrada y regresión en evidence/a1/.

## Entregado

- Ciclo DXF integrado experimental: R2000/R2010 en documento QCAD candidato,
  edición/guardado/reapertura, contraste ezdxf y sustitución atómica tras validación.
  CLAYER y OFF corregidos tras reproducir pérdidas. Writer final híbrido CE/ezdxf
  R2010 para corregir diccionarios estándar de salida; límites en native/DXF_APPLICATION.md.
  24 comprobaciones DXF por runtime, 28 de aplicación, 46/46 tests por runtime,
  CTest 5/5. Tabla de trazabilidad y matriz actualizadas: 11 qcad_partial, un
  prototype_partial, 399 pendientes, 61 exclusiones. Cero completos; A1 0/6.

- Adaptador experimental: UI existente y AutoLISP editan un RDocument QCAD
  autoritativo, transacciones con staging C++, rollback conservando redo y bloqueo
  de capas. 26 comprobaciones funcionales por runtime (Python 3.12/3.14), regresión
  41/41 por runtime y CTest 4/4 aprobados. native/ADAPTER.md y evidence/qcad-application*.
  DXF UI deshabilitado, propiedades de lectura y despliegue nativo pendientes.
  No acredita los seis criterios A1 ni comandos completos del Excel.

- M1 documental: fixture QCAD CE real con importación DXF R2000, añadir/mover,
  undo/redo, guardar/reabrir y lector independiente ezdxf. Pérdida Z de LINE/CIRCLE
  reproducida y corregida mediante parche acotado. Build local y CTest 3/3 aprobados
  (41 tests Python + geometría + documento); native/DOCUMENT.md y evidence/qcad-document*.
  No acredita UI/LSP integrada ni instalador; A1 permanece 0/6.
- Gobierno A1 publicado en PR #11, listo para revisión, 8/8 checks aprobados.
  Issue #10 mantiene los seis criterios. No se ha fusionado ni autorizado otra fase.

- Auditoría de QCAD CE y LibreCAD 3 con commits y evidencia de fuente fijados.
  Selección provisional de QCAD CE; build nativo local posteriormente aprobado,
  fixture documental comprobado; integración experimental de aplicación comprobada
  (native/M1.md, native/ADAPTER.md).
- Excel íntegro, SHA-256 y 472 filas preservadas, catálogo JSON/CSV y matriz por
  entrada. 12 parciales, 399 pendientes y 61 exclusiones 3D. Cero comandos completos.
- Gobierno técnico, CMake, CI, Issues 1–7 y seis Agent Skills con helpers,
  procedimientos, pruebas y aceptación. No se sobrescribieron skills anteriores.
- Prototipo Qt6 original: Ribbon básico, consola, canvas, selección individual,
  propiedades de lectura, capas, aliases, undo/redo, LINE/CIRCLE/MOVE/ERASE/DIST.
  Etiquetas de presentaciones no equivalen a soporte de layouts.
- Subconjunto LSP acotado, rutina original y DXF R2010 LINE/CIRCLE/capas/XYZ/INSUNITS.
  Biblioteca y variantes no implementadas se documentan en AUTOLISP e INTEROP.
- Portable Windows experimental construido y arrancado; receta Inno pendiente.

## Verificaciones ejecutadas

Windows 11 10.0.26300 AMD64; Python 3.14.4 para desarrollo y 3.12.14 para portable;
PySide6/Qt 6.10.3, ezdxf 1.4.3 y PyInstaller 6.16.0.

| Verificación | Resultado | Evidencia |
| --- | --- | --- |
| Regresión Python 3.14 | 30/30 aprobadas | evidence/regression-python314.json |
| Regresión Python 3.12 | 30/30 aprobadas | evidence/regression-python312.json |
| CTest | 1/1 suite aprobada, 30 tests internos | evidence/ctest-regression.json |
| Seis SKILL.md | 6/6 válidas por quick_validate.py | evidence/validation.json |
| Qt fuente y portable | Arranque, captura, 5 entidades y DXF roundtrip | evidence/portable-smoke.json, prototype.png |
| Comparación DIST | Baseline analítico independiente 3–4–12, aprobado | evidence/dist-comparison.json |
| LSP y DXF helpers | Ejecutados; resultado del mismo backend, comparación externa false | evidence/lsp.json, interop.json |
| Regeneración Excel/matriz | 472 filas y clasificación reproducida | catalog.json, coverage.json y tests/catalog |
| CI remota commit 4ce542f | Windows/Linux/macOS y portable aprobados (4/4 jobs) | evidence/ci-4ce542f.json |
| CI remota commit e50e1ab | Repetición tras corrección CMake: prototipo y portable aprobados (4/4 jobs) | evidence/ci-e50e1ab.json |
| QCAD CE C++/Qt6 | Build local aprobado; línea/círculo/Z contra baseline analítico | evidence/qcad-build.json, qcad-geometry.json |
| CTest nativo | 2/2 suites: regresión Python + geometría QCAD | evidence/ctest-native.txt |
| Regresión actual Python 3.14/3.12 | 31/31 por runtime; suite vacía rechazada | evidence/regression-python314-current.json, regression-python312-current.json |
| CI actual commit 9a33372 | 31 pruebas en Windows/Linux/macOS y portable: 4/4 jobs aprobados | evidence/ci-9a33372.json |
| CI nativa commit 9a33372 | En ejecución al registrar evidencia; sin aceptación remota todavía | evidence/native-ci-pending.json |

El runner actual registra número de pruebas y código real del subproceso; una
suite vacía no obtiene aceptación incluso cuando unittest devuelve cero (Python
3.12). Añadida prueba negativa y salida UTF-8 explícita para los subprocesos.
CTest local volvió a aprobar 2/2 suites después del cambio (31 pruebas Python).

Avisos de deprecación de pyparsing en ezdxf no son fallos. El primer portable
falló por ICU de Poppler recogida del PATH; `packaging/opencad.spec` excluye esas
dos DLL ajenas. Qt usa ICU de Windows System32; reconstrucción y smoke posteriores
aprobados. No se modificaron protecciones ni bibliotecas del sistema.

No ejecutadas: compilación LibreCAD, comparación de comandos con motor externo, AutoCAD,
instalar/desinstalar Inno, equipo Windows limpio, DPI/accesibilidad manual,
Linux/macOS locales. La primera CI remota aprobó Windows/macOS y falló Ubuntu por
falta de libEGL.so.1, antes de ejecutar QtTest. Añadidos libegl1/libopengl0 al runner,
la ejecución [37987669951](https://github.com/aavaladez/open-cad-2d/actions/runs/37987669951)
aprobó los cuatro jobs, incluido arranque del portable. Artefactos descargables
desde esa ejecución; esto no acredita instalación limpia ni paridad de funciones.

## Siguiente prioridad

Issue #2 / M1: toolchain C++/Qt6 aislado y build CE del commit auditado, seguido
de adaptador documental/transacciones y corpus DXF. La búsqueda inicial de PATH
no encontró compilador; una inspección posterior con vswhere identifica Visual
Studio Build Tools 2026 y componente VC x64 instalado. El spike posterior
instaló Qt 6.10.3 aislado y aprobó build
CE y geometría C++. El fixture documental posterior valida transacciones/undo/DXF
del subconjunto con segundo lector. El adaptador posterior conecta UI/bus/LSP al
documento QCAD. M1/M2 siguen parciales: falta corpus conservador de aplicación,
propiedades editables y variantes. Los handlers ECMAScript Qt6 de upstream no se
han integrado; la UI original no depende de ellos. No ampliar el motor temporal.
Prioridad: ciclo DXF conservador del documento autoritativo; luego comandos/cotas,
recuperación y distribución/instalación Windows para entrada A1.

CI del PR documental #12/c528c72: prototipo/portable y native run 38013268736
aprobados. PR #13/4697e5e: 8 checks prototipo/portable aprobados; native run
38014407702 todavía en ejecución al consultar. CI del ciclo DXF posterior pendiente.
No atribuir pruebas del prototipo portable a un despliegue QCAD instalado.

La entrega local incluye avisos/licencias; antes de una release de distribución
final faltan SBOM completo, fuentes correspondientes, pruebas en instalación limpia
y validación de la receta del instalador.
