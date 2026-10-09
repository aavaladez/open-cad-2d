# Auditoría tecnológica

Esta auditoría de selección tecnológica no sustituye la primera auditoría integral
A1 ordenada por el director el 2026-10-09. Aplicar AUDIT_GATE.md: verificar los seis
requisitos funcionales, congelar candidata, detener funciones nuevas, auditar y
PAUSAR hasta resolver bloqueantes y obtener aprobación humana de la siguiente fase.

2026-10-09. Repositorios públicos descargados de GitHub con clone superficial.
La selección inicial se basó en lectura de fuentes local y navegación pública,
antes de compilar las bases. El spike posterior [M1](../native/M1.md) compiló QCAD
y probó geometría; LibreCAD 3 no compilado. SHA, fechas, hashes y registros en
`requirements/upstream-evidence.json`; reproducción con `tools/audit_upstream.py`.

| Dimensión | QCAD Community | LibreCAD 3 |
| --- | --- | --- |
| Commit auditado | 4c830eb4d80285ca64b1f2c2dc0987f729344126 (2026-10-07) | f972953aa3295543550a90f4c6ed1c4609124c59 (2026-09-21) |
| Licencia | GPLv3 con excepciones; verificar licencias de scripts/plugins | Aplicación GPLv3-or-later; lckernel BSD-3-Clause; persistence GPLv3-or-later |
| Núcleo | C++/Qt, documento/transacciones/índice espacial; historia larga | C++17, núcleo separado de toolkit, builders/operaciones/eventos |
| Build | CMake, opción BUILD_QT6=ON; también ramas Qt5 | CMake ≥3.28, Qt6, Boost/Eigen/Lua/GLEW/GLFW/FreeType; submódulos |
| Comandos auditados | 453 nombres/aliases registrados en Init.js | 23 nombres en acciones Lua |
| Extensión | RPluginInterface C++ y ECMAScript | Lua, Python opcional, API/eventos |
| DXF | RDxfImporter/Exporter y dxflib en CE | persistence/libdxfrw y tests de roundtrip |
| DWG | Plugin propietario opcional: excluido de OPEN CAD | Lectura experimental WITH_DWG_IMPORT=OFF por defecto; no escritura acreditada |
| AutoLISP | No encontrado como runtime nativo en módulos revisados | Lua/Python no equivalen a AutoLISP |
| Nueva UI | API/plugin y estructura Qt permiten diseñar shell original; integración pendiente | lcUI/lcUILua y separación de núcleo favorables; integración pendiente |

La madurez se infiere de estructura, amplitud de acciones y mecanismos existentes;
no de un benchmark ejecutado. LibreCAD 3 tiene cambios recientes y pruebas de
persistencia: no se descarta como abandonado. QCAD tiene mayor evidencia de
alcance funcional disponible, por eso se selecciona para el primer spike de motor.
La elección es revisable si build CE, corpus DXF o extensibilidad no pasan aceptación.
QCAD Qt6 requiere también qcadjsapi/qtjsapi para el handler ECMAScript; el build
principal y prueba geométrica no acreditan su UI ni los 453 registros de comandos.

## Evidencia primaria

- [QCAD README](https://github.com/qcad/qcad/blob/4c830eb4d80285ca64b1f2c2dc0987f729344126/README.md),
  [licencias](https://github.com/qcad/qcad/blob/4c830eb4d80285ca64b1f2c2dc0987f729344126/LICENSE.txt),
  [documento](https://github.com/qcad/qcad/blob/4c830eb4d80285ca64b1f2c2dc0987f729344126/src/core/RDocument.h),
  [plugins](https://github.com/qcad/qcad/blob/4c830eb4d80285ca64b1f2c2dc0987f729344126/src/core/RPluginInterface.h),
  [build](https://github.com/qcad/qcad/blob/4c830eb4d80285ca64b1f2c2dc0987f729344126/CMakeLists.txt).
- [LibreCAD3 README](https://github.com/LibreCAD/LibreCAD_3/blob/f972953aa3295543550a90f4c6ed1c4609124c59/README.md),
  [licencia global](https://github.com/LibreCAD/LibreCAD_3/blob/f972953aa3295543550a90f4c6ed1c4609124c59/LICENSE),
  [núcleo](https://github.com/LibreCAD/LibreCAD_3/blob/f972953aa3295543550a90f4c6ed1c4609124c59/lckernel/LICENSE),
  [build/DWG](https://github.com/LibreCAD/LibreCAD_3/blob/f972953aa3295543550a90f4c6ed1c4609124c59/CMakeLists.txt),
  [tests](https://github.com/LibreCAD/LibreCAD_3/blob/f972953aa3295543550a90f4c6ed1c4609124c59/unittest/CMakeLists.txt).

No se ha comparado rendimiento, exactitud topológica ni comportamiento en un
AutoCAD instalado. No calcular un porcentaje de cobertura desde nombres registrados.
Los enlaces por fila en COMMAND_MATRIX.md permiten iniciar la adaptación funcional.

## Licencias y distribución

Copyleft GPL compatible con un producto abierto y gratuito; no obliga a usar
AutoCAD. Distribuir fuentes correspondientes, avisos y licencias. QCAD distingue
licencias de fonts, iconos/documentación (CC-BY-3.0) y dependencias. OPEN CAD usa
recursos originales y no distribuye esos iconos. Auditar SBOM de cada build antes
de versión pública. La revisión identifica condiciones técnicas, no una autorización
para incorporar código con licencia distinta o un plugin comercial.
