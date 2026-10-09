# Licencias del prototipo

Fuente original OPEN CAD: GPL-3.0-or-later, texto en LICENSE.

| Componente | Licencia declarada | Uso |
| --- | --- | --- |
| PySide6 / Shiboken6 | LGPL-3.0/GPL o comercial; se usa ruta abierta | Qt Widgets/Core/Gui |
| Qt6 | Licencias por módulo, LGPL/GPL; sólo módulos esenciales usados | Interfaz; bibliotecas dinámicas |
| ezdxf | MIT | DXF |
| NumPy | BSD-3-Clause y avisos de componentes incluidos | Dependencia de ezdxf |
| pyparsing | MIT | Dependencia de ezdxf |
| fontTools | MIT | Dependencia de ezdxf |
| Python | PSF y avisos incorporados | Runtime del portable |
| PyInstaller | GPL con excepción para bundling | Herramienta de construcción |

Los textos disponibles se recogen en `packaging/licenses` y en el portable.
La metadata de los wheels declara LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only,
aunque sus dist-info sólo aportan un aviso comercial alternativo. Se añade el
[texto LGPL de PySide v6.10.3](https://github.com/pyside/pyside-setup/blob/v6.10.3/LICENSES/LGPL-3.0-only.txt)
y GPL en `packaging/licenses/qt-for-python`; no se usa la alternativa comercial.
Qt/PySide permanecen bibliotecas dinámicas reemplazables del directorio `_internal`;
no imponer restricciones de ingeniería inversa que contradigan LGPL. Fuentes de
dependencias en sus repositorios/distribuciones oficiales. Antes de release público
final, producir SBOM, comprobar la totalidad del binario y entregar las fuentes
correspondientes que exijan las licencias. Portable inicial experimental, sin firma.

QCAD y LibreCAD3 sólo auditados y no incluidos en el portable; consultar AUDIT.md
antes de redistribuir una build nativa. No se incorpora ningún recurso de Autodesk.
Fuentes del sistema se usan para render local sin copiarse en la entrega.
