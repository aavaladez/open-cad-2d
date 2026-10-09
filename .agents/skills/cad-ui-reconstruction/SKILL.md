---
name: cad-ui-reconstruction
description: Reconstruir flujos CAD de escritorio Qt con Ribbon, consola, paneles y canvas originales, verificando interacción, foco y cancelación.
---

# cad-ui-reconstruction

Trabajar sobre el repositorio vigente y sus decisiones. Leer AGENTS.md, docs/PRODUCT.md y docs/STATUS.md. Usar documentación pública y experimentos autorizados. No copiar recursos propietarios de Autodesk. No modificar protecciones ni ampliar permisos.

## Procedimiento y aceptación

1. Relacionar controles con IDs del Excel y capacidades reales. Consultar docs/ARCHITECTURE.md y docs/WINDOWS_TESTS.md.
2. Especificar reposo, primer punto, preview, confirmación, error y cancelación, con foco, teclado y transformación pantalla/WCS.
3. Crear Ribbon, consola, propiedades, capas, pestañas y barra de estado con recursos originales. No sustituir el producto por una web ni usar iconos o marcas visuales propietarias.
4. Conectar controles al mismo CommandBus. Mostrar funciones pendientes claramente, sin simular éxito. Preservar Z.
5. Ejecutar helper offscreen y revisar visualmente PNG. Ejecutar QtTest para interacción. Registrar por separado pruebas reales de DPI, monitores, IME, teclado y accesibilidad en Windows.

Aceptación: sin recortes ni controles engañosos, Escape coherente, estado y propiedades sincronizados. Una captura no demuestra por sí sola interacción ni semejanza profesional completa.

## Automatización

Desde la raíz del repo:

```powershell
python .agents/skills/cad-ui-reconstruction/scripts/check_ui.py --output build/ui-check
python -m unittest discover -s tests -p test_ui.py -v
```

Los helpers delegan en tools/cad_workflow.py. Reportes en build/ son evidencia de ejecución, no autorización ni prueba de compatibilidad externa. Documentar resultados en docs/STATUS.md y docs/SKILLS.md.
