# Integración nativa pendiente

QCAD CE seleccionado: `4c830eb4d80285ca64b1f2c2dc0987f729344126`.
El CMake raíz permite compilar el checkout auditado con Qt 6 mediante
`OPENCAD_BUILD_QCAD=ON`, pero no integra aún OPEN CAD con RDocument.
Build CE local y smoke geométrico C++ aprobados; ver [M1](M1.md). No hay un segundo
motor C++ propio ni un adaptador documental ficticio.

Siguiente entregable: build CE reproducible, fixture de línea/círculo/Z y transacción
con RDocument/RDocumentInterface, operación undoable, lector DXF y reporte de
conservación. Después implementar un plugin de interfaz original mediante
RPluginInterface y portar los contratos del prototipo al backend real.

```powershell
./tools/build_qcad.ps1
ctest --test-dir build/native --output-on-failure
```

Requiere compilador C++, Qt 6 de desarrollo y dependencias del commit auditado.
La opción no descarga SDKs ni plugins comerciales. Qt6 ECMAScript necesita
qcadjsapi/qtjsapi adicionales; todavía no integrados. No declarar UI QCAD usable.
