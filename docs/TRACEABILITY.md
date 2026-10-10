# Trazabilidad de la integración parcial

Catálogo: SHA-256 del Excel en COMMAND_MATRIX.md; ninguna fila eliminada ni completa.
11 variantes qcad_partial, una prototype_partial (DIST), 399 pendientes, 61 exclusiones.
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
