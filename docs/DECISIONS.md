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

## ADR-009 — Spike nativo comprobado y parche mínimo

2026-10-09: Qt 6.10.3/MSVC aislados, cuatro flags -L de QCAD sustituidos por
target_link_directories entrecomillado; pin y aplicación idempotente verificados.
Build CE y fixture geométrico C++ aprobados. QCAD Qt6 requiere qcadjsapi/qtjsapi
adicionales para ECMAScript; auditados, sin integrar. El build no acredita comandos
ni adaptador documental. Mantener M1 parcial y PR independiente sobre M0.

## ADR-010 — Primera auditoría integral y detención obligatoria

2026-10-09, decisión explícita del director. A1 requiere seis demostraciones
funcionales: QCAD documental/persistente, UI, comandos esenciales/acotación,
LSP/comandos propios, ciclo DXF conservador e instalación Windows probada.
No exige completar el catálogo de 472 entradas. Reutilizar las seis skills y
añadir cad-audit-gate. Criterios/evidencias en AUDIT_GATE.md.

Al cumplir los seis: detener funciones nuevas y congelar candidata; regresión,
compatibilidad y auditoría de arquitectura/código/UI/rendimiento/estabilidad/LSP/
DXF/deuda/licencias/dependencias/seguridad. Registrar severidad y correcciones,
resolver bloqueantes, generar informe y PAUSAR. Ninguna aprobación técnica
automática sustituye aprobación del usuario para la siguiente fase. Regla
prioritaria sobre instrucciones previas de continuar después del punto de control.

## ADR-011 — Documento QCAD probado antes del adaptador de aplicación

2026-10-09: fixture original RDocument/RDocumentInterface y plugin DXF CE con
registro explícito, sin descubrimiento/carga de plugins comerciales. Documento
real DXF R2000 producido por ezdxf, edición transaccional y contraste independiente
de salida. Mantener QCAD como documento autoritativo; no ampliar el motor temporal.

La prueba reprodujo pérdida de Z en importación LINE/CIRCLE y exportación CIRCLE.
Parche GPL original de cuatro líneas, pin y git apply --check/reverse --check.
Aceptación local del subconjunto aprobada; no acredita DXF general, OCS arbitrario
ni A1. RDocumentInterface posee/destruye RDocument; éste posee storage/index.
Usar QStringLiteral en texto de operaciones para evitar resolución al overload bool
(la llamada con literal char* eligió atributos actuales y desactivó undo).

Compilar fixture y upstream en Release para coincidir en runtime. Declarar todos
los productos importados y dependencias de los parches; repetir el build incremental
upstream para no comprobar un plugin antiguo después de editar fuentes.

## ADR-012 — UI existente sobre documento QCAD autoritativo

2026-10-09: conservar UI/CommandBus/LSP y conectar un proceso C++ QCAD por pipes.
La integración funcional local prueba que las ediciones provienen del documento
nativo; las dataclasses Python son vistas descartables, no un segundo motor.
Staging clona objetos QCAD y confirma una sola RTransaction por comando/script;
rollback conserva historial redo y estado de capas. Las comprobaciones funcionales
usan geometría analítica, QtTest y rutinas LSP originales.

Proceso local con dispatch explícito, sin red ni plugins descubiertos. Pin/protocolo
verificados; fallo del motor explícito sin fallback. DXF UI deshabilitado hasta
validación conservadora. Uso Windows de desarrollo, sin autosave ni instalación;
O(N), timeout y límites de mensajes documentados en native/ADAPTER.md. Revisar
rendimiento/recuperación antes de A1. Continúa aceptación parcial y cero completos.
