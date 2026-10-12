# AutoLISP sobre comandos esenciales existentes

El runtime conserva parser/evaluador, límites y transacción exterior. El bus declara
una allowlist inmutable explícita, separada del catálogo configurable; aliases se
resuelven antes de comprobarla. QcadCommandBus incorpora sólo comandos ya
implementados y no interactivos: ARC/PLINE/COPY/ROTATE/SCALE/TRIM/EXTEND/OFFSET/
DIMLINEAR/DIMALIGNED/DIMRADIUS, además de LINE/CIRCLE/MOVE/ERASE/LAYER/DIST.
CommandBus temporal mantiene sólo su subconjunto real. COMMAND siempre devuelve NIL.

No se habilitan OPEN/SAVE/APPLOAD, UNDO/REDO dentro de LSP, red, shell, COM ni
plugins; una definición o alias no amplía capacidades. Límites previos:100000
caracteres/bytes, profundidad80,10000 evaluaciones. Error revierte todo el script,
variables, funciones y salida, preservando redo del documento QCAD.

`examples/plan_a1.lsp` es fuente propia GPL-3.0-or-later: carga sólo definiciones.
PLANO_A1 crea siete entidades nativas con Z7: LINE/CIRCLE/ARC/PLINE y tres cotas.
Medidas40/50/10, ARC centro(60,0,7) radio10, PLINE40×30 cerrada. Todo se confirma
en una transacción y persiste en DXF. cad_ajustar recibe IDs del bridge de geometrías
ya existentes: TRIM x6, EXTEND x10, OFFSET y2, COPY+(0,5,3), ROTATE90°/SCALE2;
el objetivo queda(0,0,7)→(0,20,17). No usar IDs temporales como API de AutoLISP.

Datos numéricos del bridge no son ENAME y no hay ssget/entget/getpoint todavía.
COMMAND recibe entradas completas; no reproduce prompts/opciones AutoCAD. Las
variantes pendientes de cada comando permanecen pendientes. Tampoco equivalencia
de scope dinámico/formatos numéricos/Visual LISP. Sin AutoCAD ejecutado ni A1 instalada.

## Reproducción y evidencia

```powershell
./tools/build_qcad.ps1
python tools/check_qcad_lisp_essential.py --binary build/native/opencad-qcad-engine.exe --source .cache/upstream/qcad --qt .cache/qt/6.10.3/msvc2022_64 --output build/qcad-lisp-essential
ctest --test-dir build/native --output-on-failure
```

34 comprobaciones por runtime Python3.12/3.14: carga de definiciones, creación y
modificación analíticas, undo/redo por lote, rollback/estado, capas bloqueadas,
COMMAND NIL/aliases, capacidades rechazadas, botón Cargar LSP, comando propio en
consola, original inalterado, guardado/reapertura DXF y PNG inspeccionado.
Diálogo de ruta sustituido por selección determinista; ejecución posterior real.
Regresión53/53 por runtime, CTest11/11, incluyendo suites CAD/DXF previas.
Evidencias en docs/evidence/qcad-lisp-essential*. Requisito por comando sigue parcial.
