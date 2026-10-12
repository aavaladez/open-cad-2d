# Modificación geométrica QCAD — TRIM, EXTEND y OFFSET

Módulo GPL-3.0-or-later `geometry_ops.cpp` usa formas/intersecciones/offsets públicos
QCAD del pin vigente. CadSession valida selección/permisos, presenta resultados
en staging y confirma una RTransaction. Conserva la arquitectura y cadena de PR
#13–#17; no modifica el motor Python temporal ni promete variantes completas.

## Contratos

- `TRIM limites-ID[,ID] objetivo-ID pick-XYZ [tolerancia-pick]`: objetivo LINE,
  límites finitos LINE/CIRCLE/ARC/PLINE recta en XY. QCAD calcula intersecciones;
  quitar el intervalo que contiene el pick, conservando los demás. Si se retira
  un tramo interior, mantener ID del primer tramo y crear un segundo LINE con
  los atributos originales. Una transacción/undo para la división completa.
- `EXTEND limites-ID[,ID] objetivo-ID pick-XYZ [tolerancia-pick]`: objetivo LINE;
  pick en la mitad del extremo a alargar. Elegir la intersección más próxima fuera
  de ese extremo, sobre límite finito. No convertir límites en líneas infinitas.
- Tolerancia geométrica absoluta 1e-9; tolerancia de pick separada (consola 1e-6,
  UI ocho píxeles convertidos a unidades). Ésta no relaja exactitud de intersección.
  Picks sobre corte, centro ambiguo EXTEND, fuera del objetivo o sin intersección
  utilizable se rechazan sin mutar dibujo/redo. Parámetro XY interpola/prolonga Z
  sobre la línea XYZ original; Z del límite no cambia el Z del objetivo.
- `OFFSET ID distancia punto-del-lado`: distancia positiva, LINE/CIRCLE/ARC.
  QCAD getOffsetShapes genera paralela/concentrica, conserva fuente y crea ID nuevo
  en su misma capa. Lado evaluado en XY, independientemente de Z del pick. Retener Z
  original de extremos/centro y ángulos ARC. Rechazar radio cero/negativo y lado
  ambiguo en soporte; el punto del lado puede estar fuera del segmento/arco finito.
- Ribbon: seleccionar límites existentes y pulsar Recortar/Alargar; click del
  objetivo confirma una edición, Escape termina conservando selección. Desfase
  pide distancia, selecciona entidad y recibe punto del lado; Escape cancela.
  Entrada de distancia/rutas se controla en QtTest con mocks deterministas,
  sin afirmar prueba manual del diálogo nativo. Consola usa el mismo bus.
- Capas bloqueadas impiden editar/crear copia del objetivo. Límites bloqueados
  pueden consultarse: la operación no los modifica. ID desconocido/propio como
  límite se rechaza. Se conserva historial en guardado DXF y error.

Pendientes explícitos: objetivos ARC/CIRCLE/PLINE para TRIM/EXTEND, límites
imaginarios/Edge/Project, Quick/fence/crossing como flujo de herramienta, lote de
objetivos, conmutación Shift, OFFSET PLINE y uniones, Through/Multiple/Erase/Layer,
precisión/OSNAP y COMMAND LSP de estos tres comandos. Todos qcad_partial. No usar
corpus limitado como demostración de precisión robusta en dibujos de cualquier escala.

## Baselines y reproducción

LINE (0,0,7)→(10,0,17), corte x=6: retenido hasta (6,0,13); CIRCLE centro
(5,0), radio2: tramo interior retirado entre x3 y x7, Z10/Z14. Límite ARC superior
centro(5,0), radio2 contra y1: cortes x=5±√3. Límite inferior no se inventa desde
su círculo soporte. EXTEND (0,10,7)→(4,10,11) a x8: Z15, a x−3: Z4; entre
x8/x12 elegir x8. OFFSET LINE y20 a distancia2/3: y22/y17 conservando Z7/Z17;
CIRCLE/ARC radio5: radios3/7, mismos centros Z y ángulos. Son expectativas analíticas
propias, no generadas por el código probado. Se guardan/reabren en QCAD y ezdxf.

```powershell
./tools/build_qcad.ps1
python tools/check_qcad_cutting.py --binary build/native/opencad-qcad-engine.exe --source .cache/upstream/qcad --qt .cache/qt/6.10.3/msvc2022_64 --output build/qcad-cutting
ctest --test-dir build/native --output-on-failure
```

55 comprobaciones funcionales por runtime Python3.12/3.14; baselines, variantes,
errores, undo/redo, bloqueo, límites de curvas/polilíneas, UI y DXF. Reportes/hashes
en docs/evidence/qcad-cutting*, captura revisada. No AutoCAD ni Windows instalado;
la candidata A1 sigue ausente. Acotación y empaquetado son los siguientes módulos.

Fuentes públicas consultadas 2026-10-12:
[TRIM](https://help.autodesk.com/cloudhelp/2020/ENU/AutoCAD-Core/files/GUID-B1A185EF-07C6-4C53-A76F-05ADE11F5C32.htm),
[EXTEND](https://help.autodesk.com/cloudhelp/2020/ENU/AutoCAD-Core/files/GUID-89DD7B0F-F4F1-410D-9A3A-5847CA5F8744.htm),
[OFFSET](https://help.autodesk.com/cloudhelp/2021/ENU/AutoCAD-Core/files/GUID-C0E4246D-C420-42BD-A6FC-8B1852EFD005.htm).
API exacta contrastada en src/core/math/RShape.cpp, RLine/RArc/RCircle del pin QCAD.
