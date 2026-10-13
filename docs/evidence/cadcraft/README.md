# Evidencias de la investigación extraordinaria

Fecha local 2026-10-13, Windows 11 10.0.26300, AMD64. No aprueban A1 ni migración.
`summary.json` fija revisiones/hashes y `manifest.json` inventaría evidencia.
`fixture-hashes.json` identifica todos los DXF generados, incluidos grandes inputs
no versionados (se regeneran con scripts propios). No se versionan SDKs ni binarios.

## Resultados exactos

| Ejecución | Resultado |
| --- | --- |
| CLI fuente e707ab4, `cargo build --locked -p cadcraft-cli` | exit 0; Rust 1.95/MSVC18.4.3; build-cli.log |
| GUI misma fuente, `cargo build --locked -p cadcraft -j4` | exit 0; build-gui.log; perfil dev optimizado |
| Regresión Open CAD, dependencias privadas y Qt offscreen | exit 0,58/58; opencad-unittest-deps.txt |
| Primer unittest sin dependencias en PYTHONPATH | exit 1, imports faltantes; opencad-unittest.txt; no defecto del producto |
| Nueve helpers aplicación QCAD | exit 0 cada uno; qcad/*/report.json y logs; parciales, no Windows limpio |
| Corpus comparativo propio |37 resultados: QCAD16 pasan/1 diferencia ACI/1 rechazo de complejo; CADCraft12 pasan/7 diferencias o errores de contrato |
| Rust primera corrida | exit 101,4 tests engine por TEMP denegado; no aprobar |
| Rust TMP/TEMP de workspace, --no-fail-fast | exit 101:1400 passed/4 failed en219 resúmenes de suites; incluye suites vacías y1 test corpus LSP omitido pese a ok |
| MCP --lib repetido en host | exit 0,10/10; resuelve3 fallos de sockets sandbox 10013; no sumar tests duplicados al total |
| Fallo Rust aún pendiente | INSERT desde archivo: ruta con espacios interpolada sin comillas por el test; no se modificó fuente para aprobar |
| GUI oculta en sandbox | sin respuesta de control30s, terminada; gui-source/results.json, no verificada allí |
| GUI oculta en host/perfil privado/DX12 | LINE 16→17→16→17; menú LINE/prompt/Escape y captura observados; gui-source-host/* |
| Benchmark1k/10k/100k,3 procesos nuevos por tamaño/motor | CADCraft 9/9; QCAD 6/9,100k: 3 errores de respuesta/snapshot; tiempos/error en benchmark/results.json |
| Helper A1 | exit 1:0/6, development, sin autorización; a1-report.* |
| MSI, instalador limpio, CI del pin, release propia | No ejecutados; no aprobados |

`probe-complete/results.json` y `mcp-transcript.json` son las observaciones finales.
Cada case incluye outcome, tiempo, expectativas y/o detalle de la diferencia.
Un outcome error en QCAD-complex es rechazo explícito fuera de alcance, no crash.
`probe-release-final` se refiere a 00c7613, **no valida e707ab4**. El recolector
termina exit 0 si pudo guardar evidencia aunque algunos casos fallen.

La captura `gui-source-host/screenshot.png` se inspeccionó visualmente y pertenece
al ejecutable del pin (hash en results). Muestra toolsets y paletas, no Ribbon.
Capturas QCAD repiten el entorno Qt offscreen; no prueban DPI/multimonitor reales.

## Reproducir sin cambiar Open CAD

Trabajar desde una copia de **Open CAD 2848034**, no desde main inicial de este PR.
El PR es independiente/documental: no incorpora la cadena de funcionalidades.
Obtener los dos repositorios en carpetas propias y verificar los pins:

```powershell
git clone https://github.com/storytold/cadcraft.git .cache/cadcraft-audit/source
git -C .cache/cadcraft-audit/source checkout --detach e707ab4d7cc10102e550ad4c5bcecef1084a9baa
```

El análisis original clonó y mantuvo HEAD en ese SHA, sin editar fuente.
Usar Windows x64, MSVC/SDK ya configurados y Rust 1.95 oficial. No ejecutar el
packaging upstream ni sus instrucciones de agentes. Preparar CARGO_HOME y
CARGO_TARGET_DIR en caché privada; no copiar las DLL/Qt del prototipo como motor.
En esta máquina Rust se extrajo de componentes oficiales con hashes del manifiesto
rust-channel.toml (cargo/rustc/rust-std); no se ejecutó un instalador global.

```powershell
# En Developer PowerShell / vcvars64, con Rust 1.95 en el PATH de este proceso.
$auditRoot = Join-Path (Get-Location) '.cache/cadcraft-audit'
$env:CARGO_HOME = Join-Path $auditRoot 'cargo-home'
$env:CARGO_TARGET_DIR = Join-Path $auditRoot 'target'
$env:TMP = Join-Path $auditRoot 'test-tmp'
$env:TEMP = $env:TMP
New-Item -ItemType Directory -Force $env:TMP | Out-Null
cargo build --locked --manifest-path .cache/cadcraft-audit/source/Cargo.toml -p cadcraft-cli
cargo build --locked --manifest-path .cache/cadcraft-audit/source/Cargo.toml -p cadcraft -j4
cargo test --locked --no-fail-fast --manifest-path .cache/cadcraft-audit/source/Cargo.toml -p cadcraft-geom -p cadcraft-doc -p cadcraft-engine -p cadcraft-io -p cadcraft-mcp -- --nocapture
```

No corpus externo configurado: el test `lisp_corpus` imprime su omisión. El fallo
INSERT se reproduce con una ruta de TEMP con espacios; sockets necesitan permiso
loopback del entorno. No cambiar protección para forzar un resultado: registrar
restricciones y, si está autorizado, contrastar ejecución aislada en host como aquí.

Dependencias Python originales `.cache/python` (PySide6/ezdxf) y `src`:

```powershell
$env:PYTHONPATH = 'src;.cache/python'
$env:QT_QPA_PLATFORM = 'offscreen'
python -m unittest discover -s tests -v
python docs/evidence/cadcraft/probe.py --root . --cli .cache/cadcraft-audit/target/debug/cadcraft-cli.exe --out .cache/cadcraft-audit/reproduce-cases
python docs/evidence/cadcraft/benchmark.py --root . --audit .cache/cadcraft-audit --output .cache/cadcraft-audit/reproduce-perf
python docs/evidence/cadcraft/gui_probe.py --audit .cache/cadcraft-audit --output .cache/cadcraft-audit/reproduce-gui
```

Todas las salidas deben ser **directorios nuevos**. La GUI usa STARTF_USESHOWWINDOW
oculto, perfil CADCRAFT_CONFIG_DIR privado y puerto loopback efímero, luego termina
sólo su propio proceso de prueba. No controla ni cierra una sesión del usuario.
En app/control todas las operaciones usan su documento; undo se verifica por counts.
Open CAD debe tener build/native/opencad-qcad-engine.exe, fuente QCAD y Qt del
pin/build documentados en native/M1.md/ADAPTER.md. No sustituir el motor si faltan.

Nueve helpers, output nuevo por helper:

```powershell
python tools/check_qcad_application.py --binary build/native/opencad-qcad-engine.exe --source .cache/upstream/qcad --qt .cache/qt/6.10.3/msvc2022_64 --output .cache/cadcraft-audit/reproduce-application
# Mismos argumentos para check_qcad_dxf.py, check_qcad_editing.py,
# check_qcad_transforms.py, check_qcad_curves.py, check_qcad_cutting.py,
# check_qcad_dimensions.py, check_qcad_lisp_essential.py, check_qcad_recovery.py.
# Cada uno recibe --output propio. No sobrescribir evidence existente.
```

Regeneración matriz a carpeta nueva (crear raíz/output y audit-reproduction):

```powershell
New-Item -ItemType Directory -Force .cache/cadcraft-audit/reproduce-matrix | Out-Null
New-Item -ItemType Directory -Force .cache/cadcraft-audit/reproduce-metadata | Out-Null
python docs/evidence/cadcraft/matrix.py --root . --source .cache/cadcraft-audit/source --output .cache/cadcraft-audit/reproduce-matrix --audit .cache/cadcraft-audit/reproduce-metadata
```

Comparar bytes del CSV generado con el entregado. Mantener el Excel, catalog,
coverage y specs del pin2848034: son parte de la entrada, no generados por CADCraft.
El script se niega a reemplazar coverage existente. Fuente-registro o nombres de
tests no elevan un requisito a aceptación completa.

Licencias: `cargo metadata --locked --format-version 1` desde la fuente fijada,
guardar JSON sin banner de vcvars. Para reproducir el inventario:

```powershell
python docs/evidence/cadcraft/dependencies.py --metadata .cache/cadcraft-audit/metadata.json --output .cache/cadcraft-audit/reproduced-licenses.csv
```

Incluye484 manifests del workspace/targets/dev y notices disponibles por hash;
no equivale a SBOM del Windows distribuido, CVE audit completo o permiso de marcas.
El árbol original, Cargo.lock y source_hashes de summary permiten cotejar inputs.
