---
name: cad-regression-testing
description: Ejecutar regresión CAD trazable y comparaciones con tolerancias declaradas, separando pruebas locales, referencias independientes y verificaciones omitidas.
---

# cad-regression-testing

Trabajar sobre el repositorio vigente y sus decisiones. Leer AGENTS.md, docs/PRODUCT.md y docs/STATUS.md. Usar documentación pública y experimentos autorizados. No copiar recursos propietarios de Autodesk. No modificar protecciones ni ampliar permisos.

## Procedimiento y aceptación

1. Revisar requisitos, contrato y tests afectados. Definir invariantes y tolerancias según escala/unidades; no relajarlas para ocultar fallos.
2. Ejecutar helper. Salida no cero indica fallo; conservar plataforma, comando, salida y resultado en reporte.
3. Comparar JSON con `python tools/cad_workflow.py compare baseline.json actual.json --atol 1e-9 --report build/comparison.json`. Cada archivo incluye origin, version y result. Baseline usa analytic/public_documentation/external_engine y evidence no vacío. Mantener orden o normalizar explícitamente.
4. Agregar casos negativos, degenerados, límites, undo y rollback. Ejecutar Qt offscreen si cambia interacción. Baseline nunca se genera desde el código probado.
5. Registrar tests omitidos, comparaciones externas ausentes y CI pendiente en STATUS. Actualizar requisito→código→test→versión antes de cerrar Issue/PR.

Aceptación: pruebas pertinentes aprobadas, diferencias investigadas, reporte reproducible, parciales identificados. El propio comparador debe detectar diferencias y rechazar referencias sin procedencia.

## Automatización

Desde la raíz del repo:

```powershell
python .agents/skills/cad-regression-testing/scripts/regress.py --report build/regression.json
python -m unittest discover -s tests -p test_workflow.py -v
```

Los helpers delegan en tools/cad_workflow.py. Reportes en build/ son evidencia de ejecución, no autorización ni prueba de compatibilidad externa. Documentar resultados en docs/STATUS.md y docs/SKILLS.md.
