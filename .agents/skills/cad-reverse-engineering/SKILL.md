---
name: cad-reverse-engineering
description: Investigar comportamiento CAD mediante documentación pública y referencias independientes antes de implementar una función.
---

# cad-reverse-engineering

Trabajar sobre el repositorio vigente y sus decisiones. Leer AGENTS.md, docs/PRODUCT.md y docs/STATUS.md. Usar documentación pública y experimentos autorizados. No copiar recursos propietarios de Autodesk. No modificar protecciones ni ampliar permisos.

## Procedimiento y aceptación

1. Resolver el ID de fila en `requirements/catalog.json`. Nombres repetidos y «—» no son IDs.
2. Generar el contrato inicial con el script indicado abajo. Es una especificación pendiente, no una observación.
3. Registrar variantes, prompts, unidades, WCS/OCS, tolerancias, selección, capas bloqueadas, cancelación, undo y errores.
4. Obtener documentación pública versionada y casos analíticos independientes. Si hay un CAD externo autorizado, usar dibujos sintéticos propios y registrar versión, entrada, salida y fecha. No atribuir compatibilidad AutoCAD al propio prototipo.
5. Guardar la especificación en `requirements/specs/<ID>.json`, citar evidencia y enlazar Issue, código, pruebas y versión. Revisar exclusiones 3D antes de implementar.

Aceptación: evidencia identificable, variantes descritas, al menos un caso normal, uno degenerado y uno de cancelación. Incertidumbres explícitas. No extraer código ni evadir licencias.

## Automatización

Desde la raíz del repo:

```powershell
python .agents/skills/cad-reverse-engineering/scripts/observe.py --id ACAD-0002 --output build/cases/line.json
python -m unittest discover -s tests -p test_workflow.py -v
```

Los helpers delegan en tools/cad_workflow.py. Reportes en build/ son evidencia de ejecución, no autorización ni prueba de compatibilidad externa. Documentar resultados en docs/STATUS.md y docs/SKILLS.md.
