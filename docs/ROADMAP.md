# Plan ejecutable

No hay fecha prometida de paridad profesional. Cada etapa tiene dependencia y
aceptación verificable. Priorizar corrección y conservación sobre cantidad de botones.

| Etapa | Trabajo | Dependencia | Salida / aceptación |
| --- | --- | --- | --- |
| M0 | Auditoría, Excel, gobierno, skills, prototipo | Archivos y repositorios públicos | Matriz de 472 filas, fuentes fijadas, pruebas y PR; sin comandos del Excel completados |
| M1 | Toolchain Qt6/C++ y build QCAD CE fijado; inventario licencias | M0 | Build repetible Windows, smoke documento/transacción/Z/DXF, logs y CI de upstream |
| M2 | Adaptador de motor y CommandBus; alias/selección/undo | M1 | Reproducir contratos LINE/CIRCLE/LAYER/MOVE; mismos resultados analíticos con QCAD |
| M3 | UI original: Ribbon, consola, propiedades editables, capas, OSNAP/ORTHO, pestañas | M2 | QtTest/teclado, estados/cancelación, DPI/accesibilidad; múltiples documentos y autosave |
| M4 | Geometría y anotación | M2/M3 | PLINE/ARC, recorte/extensión/offset, bloques/texto/cotas/hatch por variantes del Excel |
| M5 | LSP expandido, editor, macros/extensiones | M2; subconjunto ya probado en M0 | entget/entmod/ssget/getpoint/envs/errores y corpus LSP; diferencias documentadas |
| M6 | DXF completo y corpus externo; DWG lectura abierta | M2/M4 y auditoría biblioteca | Versiones/capas/bloques/layouts/Z/XDATA, pérdidas explícitas y motor externo |
| M7 | Presentaciones, plot/PDF, instalador y release | M3/M4/M6 | Escalas, viewports, fuentes correspondientes, install/uninstall y archivo firmado si disponible |
| M8 | GIS/topografía/terreno 2D+Z | Motor base y formatos | EPSG/reproyección, SHP/GeoTIFF/LandXML, COGO/TIN/curvas/parcelas por contratos |

## Próxima iteración prioritaria

1. Validar PR inicial/CI y resolver fallos por plataforma.
2. Preparar toolchain C++/Qt6 en directorio aislado; reproducir QCAD CE sin componentes
   comerciales y registrar SBOM. Compilación de upstream aún no demostrada.
3. Completar contratos de LINE y CIRCLE, incluyendo variantes ausentes, y llevar
   fixtures al backend QCAD antes de ampliar el motor temporal.
4. Expandir capacidades por Issues pequeños: selección, OSNAP, PLINE/ARC,
   recorte/offset, texto/cotas y persistencia. Cada PR actualiza matriz y status.

Roles de las skills: reverse-engineering → command-cloner o UI/LSP/interop →
regression-testing. No se crea un nuevo repositorio ni se reinicia el proyecto.

