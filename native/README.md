# Integración nativa pendiente

QCAD CE seleccionado: `4c830eb4d80285ca64b1f2c2dc0987f729344126`.
El CMake raíz permite compilar el checkout auditado con Qt 6 mediante
`OPENCAD_BUILD_QCAD=ON`, pero no integra aún OPEN CAD con RDocument.
No hay un segundo motor C++ propio ni un adaptador ficticio.

Siguiente entregable: build CE reproducible, fixture de línea/círculo/Z y transacción
con RDocument/RDocumentInterface, operación undoable, lector DXF y reporte de
conservación. Después implementar un plugin de interfaz original mediante
RPluginInterface y portar los contratos del prototipo al backend real.

```powershell
cmake -S . -B build/native -DOPENCAD_BUILD_QCAD=ON -DOPENCAD_QCAD_SOURCE=.cache/upstream/qcad
cmake --build build/native --config Release
```

Requiere compilador C++, Qt 6 de desarrollo y dependencias del commit auditado.
No ejecutado en esta entrega. La opción no descarga SDKs ni plugins comerciales.
