# Verificación documental QCAD CE

2026-10-09. Avance M1, Issues #2/#5; no aceptación integral A1.

Fixture original sobre QCAD GPL, pin 4c830eb4d80285ca64b1f2c2dc0987f729344126,
Qt 6.10.3, MSVC x64, Release y ezdxf 1.4.3. No usa AutoCAD ni recursos propietarios.
Consultar M1.md para toolchain/fetch. Reproducción:

```powershell
./tools/build_qcad.ps1
ctest --test-dir build/native --output-on-failure
python tools/check_qcad_document.py --binary build/native/qcad-document-smoke.exe --source .cache/upstream/qcad --qt .cache/qt/6.10.3/msvc2022_64 --output build/native/document-acceptance
```

Cada ejecución crea un directorio nuevo: input/output DXF, stdout JSON, stderr y
reporte con hashes del ejecutable, DLLs QCAD/plugin y parche. No sobrescribe entradas.
Compara geometría contra coordenadas originales y salida con segundo motor ezdxf.
La CI publica esas evidencias y CTest; su resultado actual debe consultarse antes
de declarar un build limpio remoto aprobado.

Caso: dos entidades en Survey (ACI 3), INSUNITS=4; LINE (0,0,7)→(3,4,7) y CIRCLE
(10,20,9), radio 3. Añadir LINE (20,0,5)→(23,4,5), conteos 2→3→2→3. Mover a
(10,2,5)→(13,6,5), undo/redo con mismos puntos. Guardar DXF R2000 y reabrir en
documento distinto. Verificar geometrías, radio, capas, unidades y atributos BYLAYER.
Tolerancia geométrica 1e-9; nombres DXF sin distinción de mayúsculas.

## Fallo reproducido y corrección

La CE fijada importó Z=0 para LINE/CIRCLE y exportó CIRCLE con Z=0. El contraste
independiente falló antes del parche, aunque las operaciones transaccionales pasaron.
Parche de cuatro líneas conserva data.z1/z2/cz y escribe center.z. Sólo extrusión
estándar; no acredita OCS arbitrario, ARC/polilíneas/textos/cotas/atributos complejos.
Evidencias anteriores y posteriores versionadas en docs/evidence, incluidos sus DXF.
La diferencia ByLayer/BYLAYER era de representación, no una pérdida semántica.

La construcción inicial del fixture falló por dos errores propios: documento en
pila pese a que RDocumentInterface lo destruye (detectado al salir); literal char*
resuelto al overload bool de RAddObjectOperation, que desactivó undo. Corregidos
con propiedad de memoria acorde al código público y QStringLiteral/firma explícita.
El driver vuelve a comprobar salida de proceso, conteos y geometría. La configuración
raíz ahora usa Release, al igual que upstream; un intento Debug produjo C1902 de PDB.

## Resultado y siguiente paso

Local Windows: build final y 3/3 suites CTest aprobadas, incluyendo 41 tests Python,
geometría QCAD y ciclo documental contrastado. Sin GUI instalada, LSP sobre QCAD ni
aplicación integrada: A1 sigue 0/6. El siguiente cambio debe extraer el adaptador
documental probado y conectar la UI y comandos al mismo documento QCAD. Importar en
un documento temporal: RDocumentInterface::importFile limpia el destino antes de
validar el archivo; una importación fallida no debe vaciar el dibujo activo.
