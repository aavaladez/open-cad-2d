# AutoLISP: alcance real

La entrada A1 exige carga LSP y comandos personalizados ejecutados sobre el mismo
documento QCAD de la candidata, con errores/rollback funcionalmente verificados.
Los tests del subconjunto temporal no acreditan este criterio. Aplicar AUDIT_GATE.md
y detener funciones nuevas al verificar los seis puntos del director.

Runtime original en `src/opencad/lisp.py`. Archivos .LSP UTF-8/UTF-8-BOM mediante
diálogo y API LispRuntime.load. Evaluación desde la consola; comandos `C:nombre`
definidos por DEFUN invocables desde el CommandBus.

| Funciones | Estado |
| --- | --- |
| quote, setq, defun, if, progn | Subconjunto implementado; tests locales |
| +, -, *, /, = | Aritmética básica; sin promoción/rangos exactos AutoLISP |
| list, car, cdr, cons, length | Listas propias; sin dotted pairs |
| command, princ | Bridge acotado al prototipo, salida de texto almacenada |
| entget, entmod, entmake, ssget, getpoint, getvar/setvar | Pendiente |
| load desde código LISP, archivos/red, reactors, DCL, Visual LISP/vlax/COM | No implementado |
| FAS, VLX, ARX, .NET, VBA | No compatible; no cargar binarios propietarios |

Ejemplo propio: `examples/rectangle.lsp` crea 4 líneas y un círculo, con Z=2.
Todo el script corresponde a una transacción undoable; en fallo revierte geometría,
variables, funciones y salida. COMMAND sólo permite LINE/CIRCLE/MOVE/ERASE/LAYER/DIST.
Sin eval/exec de Python, shell ni llamadas de red.

## Diferencias declaradas

DEFUN crea entorno local por llamada. SETQ dentro de función no modifica globals
como lo haría AutoLISP en todos sus casos; falta el modelo dinámico completo.
COMMAND recibe argumentos completos, no conversa con prompts/getpoint. No admite
todas las opciones de cada comando, selección sets, nombres DXF ni diálogos DCL.
Datos de entrada de archivo sólo UTF-8. Los escapes usan cadenas JSON, no todos los
escapes AutoLISP. Números Python; no equivalencia bit a bit.

Tamaño ≤100000 caracteres en run y ≤100000 bytes en load, profundidad ≤80,
presupuesto 10000 evaluaciones por ejecución. No afirmar sandbox de OS ni permitir
nuevas capacidades a través de aliases. Pruebas de recursión, sintaxis, rollback y
rechazo de capacidades en tests/test_lisp.py.

No se ha ejecutado este corpus en AutoCAD. Compatibilidad externa pendiente.
