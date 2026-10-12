# Estado verificable — 2026-10-12

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

- Recuperación privada del último estado QCAD confirmado, separada de staging.
  Manifest/hash/publicación atómica y dos generaciones por sesión; candidato QCAD
  con confirmación/reinicio de historial, selección y LSP. Original intacto.
  21 comprobaciones por runtime Python3.12/3.14, 58 tests y CTest12/12; captura
  inspeccionada. native/RECOVERY.md y evidence/qcad-recovery*. CI general/nativa
  #19/#20 aprobada en heads exactos; listos para revisión sin merge. Cadena
  #13–#20 conservada. A1 sigue0/6: aplicación nativa empaquetada/instalada y
  Windows limpio sobre una misma candidata pendientes.

- Consolidación LSP de capacidades existentes: allowlist nativa explícita para
  ARC/PLINE, transformaciones, TRIM/EXTEND/OFFSET y las tres cotas. COMMAND NIL,
  aliases sin ampliación de permisos; límite/rollback/historial conservados.
  plan_a1.lsp propio define PLANO_A1 y cad_ajustar, probados desde carga/UI/consola
  y sobre geometría QCAD/DXF.34 comprobaciones por runtime,53 tests y CTest11/11.
  native/LISP_ESSENTIAL.md y evidence/qcad-lisp-essential*. Matriz sigue24 parciales,
  cero completos. Archivos/historial/COM/shell/ssget/entget no habilitados.
  A1 sigue0/6: recuperación y Windows instalado/entorno limpio pendientes.

- Acotación QCAD nativa: DIMLINEAR/DIMALIGNED/DIMRADIUS como DIMENSION en documento,
  medidas analíticas, puntos XYZ planares, propiedades/texto/<>/UTF8, Ribbon/consola,
  selección y transformaciones con undo/redo. Renderizador básico CE GPL y writer
  híbrido de bloques gráficos válidos; cotejo de cachés antes de apertura para impedir
  pérdida de anotaciones modificadas. R2000 legado se normaliza a UTF8 sólo tras
  preflight/contraste, original intacto. native/DIMENSIONS.md declara límites.
  58 comprobaciones por runtime Python3.12/3.14, regresión51/51 y CTest10/10.
  24 qcad_partial, un prototype_partial,386 pendientes y61 exclusiones; cero completos.
  Sin asociación paramétrica de cotas con fuente ni variantes completas; estilos
  avanzados/glyphs/DPI pendientes. A1 sigue0/6: consolidación/recuperación e
  instalación limpia sobre la misma candidata pendientes, sin congelación.

- CI general/nativa de #17 y #18 comprobada success en sus commits exactos;
  ambos listos para revisión, sin fusionar. Acotación nueva se apila sobre #18
  y queda en borrador hasta verificar su propia CI. Cadena #13–#18 preservada.

- TRIM/EXTEND/OFFSET nativos: objetivos LINE y límites finitos LINE/CIRCLE/ARC/
  PLINE recta para recorte/alargamiento; división de tramo interior, selección del
  extremo e intersección más próxima, Z interpolada/prolongada. OFFSET distancia/lado
  para LINE/CIRCLE/ARC, fuente intacta y Z conservada. Mismo bus, UI y transacciones;
  pruebas de bloqueo, límites consultables bloqueados, ambigüedades, error/redo y DXF.
  55 comprobaciones por runtime, regresión 48/48 y CTest 9/9. native/CUTTING.md,
  contratos ACAD-0042/43/44 y evidence/qcad-cutting*. Matriz: 21 qcad_partial,
  un prototype_partial, 389 pendientes, 61 exclusiones, cero completos. Cotas,
  consolidación LSP/recuperación y Windows instalado siguen pendientes; A1 0/6.

- ARC/PLINE sobre QCAD: ARC por tres puntos o centro/radio/ángulos, PLINE recta
  abierta/cerrada como una entidad nativa, selección exacta XY, propiedades y
  transformaciones, transacciones/undo/redo. Conservación de ARC Z y elevación
  LWPOLYLINE R2000/R2010; bulges/anchuras/PLINEGEN rechazados sin perder el activo.
  69 comprobaciones funcionales por runtime Python 3.12/3.14, 48 tests de regresión
  por runtime y CTest 8/8. native/CURVES.md y evidence/qcad-curves*. Captura revisada.
  18 qcad_partial, un prototype_partial, 392 pendientes, 61 exclusiones; cero completos.
  A1 sigue 0/6, candidata null, sin congelación. Restan TRIM/EXTEND/OFFSET, cotas,
  recuperación y aplicación Windows instalada en entorno limpio. Variantes ARC/PLINE
  y COMMAND LSP de estos comandos pendientes explícitamente.

- CI remota comprobada en los heads exactos de #13–#16: general y Windows-native
  success. Cadena de bases preservada, todos abiertos/sin fusionar; #15/#16 pasan
  de borrador a listos para revisión. La nueva entrega ARC/PLINE depende de #16;
  no promoverla hasta verificar sus propios checks. No publicar release por CI verde.

- COPY/ROTATE/SCALE en QCAD: clones validados, transacción por selección, originales
  intactos/nuevos IDs, aliases, conservación Z, undo/redo, bloqueos y rechazos.
  23 comprobaciones funcionales por runtime y CTest 7/7. native/TRANSFORMS.md y
  evidence/qcad-transforms*. Sólo variantes LINE/CIRCLE; sin Reference/Array ni
  puente LSP para estos tres comandos. Matriz: 16 qcad_partial, un prototype_partial,
  394 pendientes y 61 exclusiones. Cero completos; A1 continúa 0/6.

- Propiedades editables y selección sobre QCAD: LINE XYZ, CIRCLE centro/radio, capa
  común de selección mixta, edición atómica y sincronización con undo/redo. Selección
  nativa XY, ventana/cruce, acumulación/Shift y MOVE UI con base/destino/cancelación.
  30 comprobaciones por runtime Python 3.12/3.14, regresión 46/46 y CTest 6/6,
  incluidos LSP/DXF existentes. native/EDITING.md y evidence/qcad-editing*.
  Criterios A1 siguen parciales: acotación/comandos, recuperación e instalación
  limpia pendientes. Sin congelación ni autorización de fase siguiente.

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

CI verificada 2026-10-12: PR #13/4697e5e (runs 38014407702/38014407807) y
PR #14/ff5f552 (38015692655/38015692620) aprobados; heads/dependencias intactos.
Ambos listos para revisión, sin merge. PR #15/8d3a7ee: verificación del prototipo y
portable run 38266420863 aprobada; nativo run 38266420898 todavía en ejecución al
consultar. CI del módulo posterior de transformaciones pendiente.
No atribuir pruebas del prototipo portable a un despliegue QCAD instalado.

La entrega local incluye avisos/licencias; antes de una release de distribución
final faltan SBOM completo, fuentes correspondientes, pruebas en instalación limpia
y validación de la receta del instalador.
