# Estado verificable — 2026-10-09

M0 preparado para revisión. No hay declaración de paridad profesional ni de
compatibilidad completa con AutoCAD, AutoLISP, DXF o DWG.

## Entregado

- Auditoría de QCAD CE y LibreCAD 3 con commits y evidencia de fuente fijados.
  Selección provisional de QCAD CE; integración y compilación nativa pendientes.
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

Windows 10.0.26200 AMD64; Python 3.14.4 para desarrollo y 3.12.14 para portable;
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

Avisos de deprecación de pyparsing en ezdxf no son fallos. El primer portable
falló por ICU de Poppler recogida del PATH; `packaging/opencad.spec` excluye esas
dos DLL ajenas. Qt usa ICU de Windows System32; reconstrucción y smoke posteriores
aprobados. No se modificaron protecciones ni bibliotecas del sistema.

No ejecutadas: compilación QCAD/LibreCAD, comparación con motor externo, AutoCAD,
instalar/desinstalar Inno, equipo Windows limpio, DPI/accesibilidad manual,
Linux/macOS locales. La primera CI remota aprobó Windows/macOS y falló Ubuntu por
falta de libEGL.so.1, antes de ejecutar QtTest. Se añaden libegl1/libopengl0 al runner;
la nueva ejecución debe acreditar la corrección. Consultar checks del PR para
estado remoto; no se sustituye el fallo por una omisión de tests.

## Siguiente prioridad

Issue #2 / M1: toolchain C++/Qt6 aislado y build CE del commit auditado, seguido
de adaptador documental/transacciones y corpus DXF. El entorno inicial no aporta
compilador C++/SDK Qt de desarrollo acreditados; los wheels PySide no sustituyen
esa validación. No extender el motor temporal como base definitiva.

La entrega local incluye avisos/licencias; antes de una release de distribución
final faltan SBOM completo, fuentes correspondientes, pruebas en instalación limpia
y validación de la receta del instalador.
