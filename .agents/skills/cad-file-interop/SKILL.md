---
name: cad-file-interop
description: Verificar conservación semántica al importar/exportar DXF y evaluar DWG progresivamente sin dependencia comercial obligatoria.
---

# cad-file-interop

Trabajar sobre el repositorio vigente y sus decisiones. Leer AGENTS.md, docs/PRODUCT.md y docs/STATUS.md. Usar documentación pública y experimentos autorizados. No copiar recursos propietarios de Autodesk. No modificar protecciones ni ampliar permisos.

## Procedimiento y aceptación

1. Leer docs/INTEROP.md. Registrar hash, origen, versión, unidades, WCS/OCS, Z, bloques/layouts, XDATA y entidades desconocidas de fixtures permitidos.
2. Inventariar atributos antes de editar. El prototipo debe rechazar datos fuera del subconjunto o preservarlos explícitamente; nunca descartar en silencio.
3. Escribir a temporal y reemplazar sólo tras éxito. Nunca sobrescribir el fixture original durante una prueba; abortar corrupción sin alterar documento.
4. Ejecutar helper y comparar semántica, no bytes. El reporte debe identificar que roundtrip usa el mismo backend ezdxf.
5. Verificar salida con segundo motor disponible y registrar versión. Si falta, marcar pendiente. Para DWG auditar biblioteca/corpus abiertos y objetos proxy; lectura no acredita escritura.

Aceptación: geometría y atributos conservados en variantes declaradas, rechazo de pérdidas y rollback comprobados. No incorporar plugins propietarios ni declarar compatibilidad externa por autorreferencia.

## Automatización

Desde la raíz del repo:

```powershell
python .agents/skills/cad-file-interop/scripts/roundtrip.py build/smoke/smoke.dxf build/interop/output.dxf --report build/interop/report.json
python -m unittest discover -s tests -p test_interop.py -v
```

Los helpers delegan en tools/cad_workflow.py. Reportes en build/ son evidencia de ejecución, no autorización ni prueba de compatibilidad externa. Documentar resultados en docs/STATUS.md y docs/SKILLS.md.
