# Decisiones técnicas

| ID | Fecha | Decisión y evidencia | Consecuencia / revisión |
| --- | --- | --- | --- |
| ADR-001 | 2026-10-09 | Preservar íntegramente Excel con IDs hoja/fila y SHA-256 | 472 entradas y 8 notas; exclusiones 3D visibles; regeneración determinista |
| ADR-002 | 2026-10-09 | QCAD CE como base seleccionada tras auditoría comparativa | Fijar commit; aceptar sólo tras spike compilado de documento, undo y DXF; LC3 alternativa |
| ADR-003 | 2026-10-09 | Qt6/C++ como destino, Python/PySide6 temporal por ausencia de toolchain | Prototipo permite pruebas hoy; no declarar QCAD integrado ni mantener segundo motor profesional |
| ADR-004 | 2026-10-09 | GPL-3.0-or-later para fuente original OPEN CAD | Revisar por módulo y avisos; sin plugins comerciales ni activos Autodesk |
| ADR-005 | 2026-10-09 | DXF acotado LINE/CIRCLE y ezdxf para prototipo | Z/capas/INSUNITS probados; bloquear entidades/atributos detectados fuera del subconjunto; DWG pendiente |
| ADR-006 | 2026-10-09 | AutoLISP por intérprete explícito y puente CommandBus | Tamaño/profundidad/pasos acotados; funciones faltantes fallan; sin COM/red/shell |
| ADR-007 | 2026-10-09 | Seis skills versionadas con helpers y tests | Inicialización sin sobrescribir skills previas; no generan evidencia ficticia |
| ADR-008 | 2026-10-09 | Repo público aavaladez/open-cad-2d y rama codex/initial-audit | Autorización del director para elegir/crear repo; cambios por PR, no merge automático |

Las decisiones de implementación son revisables con resultados. Ninguna añade
gastos, disminuye protecciones o modifica los requisitos por preferencia del agente.
