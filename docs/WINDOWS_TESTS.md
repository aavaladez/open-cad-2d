# Verificación Windows pendiente

A1 requiere instalación Windows y pruebas funcionales sobre la aplicación
instalada, según AUDIT_GATE.md. Receta, portable o tests internos no bastan.
Verificados los seis puntos, congelar, auditar y PAUSAR hasta resolución de
bloqueantes y aprobación explícita del director para la siguiente fase.

Ejecutado: Python 3.14, PySide6 6.10.3, Qt offscreen/QtTest, geometría y DXF
del subconjunto. La captura requiere cargar una fuente ya presente en Windows
porque offscreen no enumeró las fuentes del sistema. No se distribuye Arial.

Antes de release, registrar ejecución real en Windows 10/11 limpio:

- Arranque del portable sin Python instalado; dependencias/licencias incluidas.
- Teclado español, coma decimal, rutas Unicode, archivos bloqueados y cancelación.
- Escalado 100/150/200%, dos monitores y foco entre Ribbon/consola/canvas.
- LINE/CIRCLE por clicks, Escape, undo/redo, selección y capas bloqueadas.
- DXF generado abierto en segundo CAD y corpus externo con unidades/Z.
- Instalador Inno Setup, instalación sin admin, ejecución y desinstalación.
- Accesibilidad, recuperación tras cierre inesperado y grandes dibujos (pendientes).

Estas verificaciones no están aprobadas por haber pasado el modo offscreen.
