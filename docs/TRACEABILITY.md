# Trazabilidad de la integración parcial

Catálogo: SHA-256 del Excel en COMMAND_MATRIX.md; ninguna fila eliminada ni completa.
24 variantes qcad_partial, una prototype_partial (DIST), 386 pendientes, 61 exclusiones.
Las pruebas funcionales complementan los tests temporales; las variantes ausentes
siguen en coverage.json. Versiones/hashes de binario y DLL en los reportes, no una
candidata instalada A1. Los reportes históricos no se atribuyen a cambios posteriores.

| IDs Excel | Variante y código | Evidencia funcional |
| --- | --- | --- |
| ACAD-0002 LINE | CadSession line / QcadCommandBus; cadena XYZ, alias y ratón | check_qcad_application native_ids/chain_z/ribbon_mouse_edits_qcad |
| ACAD-0007 CIRCLE | CadSession circle; centro/radio | console_edits_qcad, rutina rectangle.lsp |
| ACAD-0037 MOVE | CadSession move; IDs y vector XYZ | check_qcad_dxf R2000/R2010_analytic_move, locked_layer_rejected |
| ACAD-0053 ERASE | CadSession erase; IDs | erase_native/erase_undo |
| ACAD-0076/0077 UNDO/REDO | RDocumentInterface, BatchOperation | chain_single_undo/whole_lsp_undo/redo_survives_failed_lsp/save_preserves_undo_redo |
| ACAD-0107 LAYER | staging QCAD NEW/SET/ON/OFF/LOCK/UNLOCK | staged_layer_batch/layer_batch_rollback/layer_flags_saved |
| ACAD-0262 OPEN | qcad_interop.open_document y botón UI; DXF acotado | failed_open_preserves_document/ui_open_cancel/ui_open |
| ACAD-0265 SAVEAS | qcad_interop.save_document; R2010 canónico | ui_edit_save/ui_reopen; tests/test_qcad_interop atomicidad |
| ACAD-0335 APPLOAD y fila LOAD del catálogo | LispRuntime.load y botón Cargar LSP, sin módulos ARX/DLL | lsp_file_ui/custom_console_command |
| ACAD-0095 DIST | bus temporal; XY/XYZ analítico, sin ángulo requerido | test_commands.Commands.test_dist_analytic; sigue prototype_partial |

Helpers: tools/check_qcad_application.py (28 comprobaciones), tools/check_qcad_dxf.py
(24), tests/test_qcad_interop.py (5 límites). No sumarlos como comandos terminados.
Evidencias actuales docs/evidence/qcad-dxf*; antecedentes qcad-application*/qcad-document*.

Seguimiento: Issues #2/#3/#4/#5 y gate #10. PR #12 documental, #13 adaptador;
siguiente cambio DXF apilado sobre #13. No merge/release automático.

Actualización 2026-10-12: ACAD-0086 SELECT y ACAD-0091 PROPERTIES pasan a qcad_partial,
con contratos en requirements/specs y 30 comprobaciones en check_qcad_editing.py.
MOVE incorpora selección/punto base-destino y cancelación; los requisitos siguen
parciales. Matriz actual: 13 qcad_partial, un prototype_partial, 397 pendientes y
61 exclusiones. Reportes nuevos qcad-editing*, conservando todos los antecedentes.

Módulo posterior: ACAD-0038 COPY, ACAD-0039 ROTATE, ACAD-0040 SCALE, implementados
en CadSession/QcadCommandBus; check_qcad_transforms.py (23 casos) y TRANSFORMS.md.
Matriz actual: 16 qcad_partial, un prototype_partial, 394 pendientes, 61 exclusiones.
Pruebas exactas de variantes/errores/undo y DXF; opciones restantes siguen pendientes.

ARC ACAD-0008 y PLINE ACAD-0003: contratos propios en requirements/specs,
CadSession/QcadCommandBus, proyecciones qcad_views.py, panel/canvas y qcad_interop.
check_qcad_curves.py: 69 casos analíticos/Qt/DXF (Python 3.12/3.14); CURVES.md
define variantes ausentes. evidence/qcad-curves*. Matriz 18 qcad_partial; sin completos.
COPY/ROTATE/SCALE/MOVE/SELECT/PROPERTIES se amplían a estos tipos mediante los
mismos módulos; Z, selección de arco y errores comprobados sin sustituir motor.

TRIM ACAD-0043, EXTEND ACAD-0044 y OFFSET ACAD-0042: contratos en requirements/specs;
geometry_ops.cpp y CadSession, QcadCommandBus y herramientas Ribbon sobre selección
nativa. check_qcad_cutting.py 55 casos; native/CUTTING.md define baselines/opciones
pendientes. evidence/qcad-cutting*. Matriz 21 qcad_partial; cero completos/A1 0/6.

DIMLINEAR ACAD-0176, DIMALIGNED ACAD-0177, DIMRADIUS ACAD-0179: contracts en
requirements/specs, dimensions.cpp/CadSession y qcad_dimensions_io.py; UI/bus
existentes. check_qcad_dimensions.py58 casos: medida, tipos, propiedades/transformación,
Qt, UTF8, R2000/R2010, datos/cachés, undo/redo y rechazo sin mutación. native/DIMENSIONS.md
y evidence/qcad-dimensions*. Matriz24 parciales, sin asociaciones automáticas/completos.

Los mismos IDs de ARC/PLINE/COPY/ROTATE/SCALE/TRIM/EXTEND/OFFSET/DIMLINEAR/
DIMALIGNED/DIMRADIUS añaden prueba de COMMAND LSP sobre su subconjunto real en
check_qcad_lisp_essential.py34 casos, plan_a1.lsp y native/LISP_ESSENTIAL.md.
Carga APPLOAD/LOAD y comando propio conservan traza previa y amplían corpus. No
añadir filas/estados completos; variantes de prompts/selección ENAME pendientes.

Recuperación de estabilidad, sin nuevo comando del catálogo: CadSession.snapshot
transaction_active → QcadDocument._confirmed_view → RecoveryStore → restore_recovery.
21 comprobaciones check_qcad_recovery.py (staging, caída sólo del hijo, original
intacto, restauración Qt/QCAD, LSP reiniciado, DXF) y cinco límites test_recovery.py.
native/RECOVERY.md y evidence/qcad-recovery*. No reparar DXF arbitrarios ni acreditar
RECOVER por esta función. CI #19/#20 success exacthead: evidence/pr19-20-ci-2026-10-12.json.
