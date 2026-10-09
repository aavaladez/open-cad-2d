# Skills especializadas

Seis skills CAD originales en `.agents/skills/`, con frontmatter, procedimientos, helper por
skill y criterios de aceptación. Ruteo en AGENTS.md. El inicializador se niega a
sobrescribir skills existentes. No se modificó configuración global de Codex.

Automatización común `tools/cad_workflow.py`: contratos por ID real del Excel,
ejecución LSP, captura/smoke Qt, roundtrip DXF, comparador JSON y runner de regresión.
Contratos nacen pendientes y aceptación en false; no confundir scaffold con implementación.
Comparador rechaza baseline del propio prototipo, falta de procedencia y tolerancia
negativa/no finita; distingue booleano de número y detecta pérdida de Z.

`tests/test_workflow.py` prueba comportamiento de esos helpers, preservación de
contratos existentes, IDs desconocidos y comandos 3D excluidos. `test_commands.py`,
`test_ui.py`, `test_lisp.py` y `test_interop.py` validan los flujos de cada skill.
Validación estructural con quick_validate.py de skill-creator; resultados en STATUS.
El runner registra cuántas pruebas ejecutó y rechaza suites vacías. La prueba
negativa se ejecutó en Python 3.12 y 3.14, cuyos códigos unittest para cero tests
difieren; no basta con comprobar que el subproceso devolvió cero.

Las skills facilitan trabajo autónomo: contrato/evidencia → implementación →
pruebas → matriz/Issue/PR. No descargan código propietario, no amplían permisos,
no inventan observaciones y no ejecutan publicaciones fuera del alcance autorizado.

## cad-audit-gate y revisión de las seis skills

Revisadas las seis SKILL.md el 2026-10-09; se conservan sus procedimientos y
helpers, reutilizándolos para A1 según AUDIT_GATE.md. Añadida cad-audit-gate con
helper de evidencias, reporte y congelación persistente; tests negativos del
controlador en test_audit_gate.py. El test de entrypoints comprende siete helpers.
No instaladas herramientas adicionales. Un test sintético del gate no acredita
que el producto alcance sus seis criterios.
