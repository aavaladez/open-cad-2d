---
name: cad-command-cloner
description: Implementar equivalentes abiertos de comandos CAD desde contratos funcionales trazables, incluyendo alias, transacciones y pruebas de variantes.
---

# cad-command-cloner

Trabajar sobre el repositorio vigente y sus decisiones. Leer AGENTS.md, docs/PRODUCT.md y docs/STATUS.md. Usar documentación pública y experimentos autorizados. No copiar recursos propietarios de Autodesk. No modificar protecciones ni ampliar permisos.

## Procedimiento y aceptación

1. Leer contrato por ID del Excel y arquitectura vigente. Si falta semántica, aplicar cad-reverse-engineering.
2. Generar contrato inicial sólo si falta. El script no implementa código ni sobrescribe archivos.
3. Separar entrada interactiva, validación, operación y presentación. Usar el CommandBus y transacciones; seguir integración C++/QCAD del roadmap sin duplicar el motor definitivo.
4. Configurar aliases sin colisiones. Registrar las variantes ausentes, comandos con guion y transparentes como pendientes.
5. Implementar el contrato con geometría comprobable, tolerancias declaradas, conservación Z, rollback y undo/redo. Crear pruebas contra resultados analíticos o un motor externo identificado.
6. Actualizar matriz/STATUS y preparar PR pequeño asociado al Issue.

Aceptación: ninguna mutación tras error/cancelación, aliases equivalentes y prueba por variante. «Cloner» significa equivalencia funcional, nunca copiar código, textos extensos ni recursos propietarios.

## Automatización

Desde la raíz del repo:

```powershell
python .agents/skills/cad-command-cloner/scripts/scaffold.py --id ACAD-0002 --output build/contracts/line.json
python -m unittest discover -s tests -p test_commands.py -v
```

Los helpers delegan en tools/cad_workflow.py. Reportes en build/ son evidencia de ejecución, no autorización ni prueba de compatibilidad externa. Documentar resultados en docs/STATUS.md y docs/SKILLS.md.
