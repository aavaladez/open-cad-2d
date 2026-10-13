# Auditoría extraordinaria de CADCraft — 2026-10-13

**Recomendación: continuar con QCAD Community como documento autoritativo de Open CAD.**
CADCraft merece investigación como proveedor de módulos independientes y automatización,
pero no sustituye hoy las garantías XYZ, rollback LSP y rechazo conservador de archivos
de nuestra integración. No se migró código, no se fusionó ningún PR y no se aprobó A1.
La recomendación híbrida futura está acotada en [opciones](CADCRAFT_MIGRATION_OPTIONS.md).

## Identidad y límites del trabajo

| Objeto | Identidad |
| --- | --- |
| CADCraft analizado y CLI compilada | [`e707ab4d7cc10102e550ad4c5bcecef1084a9baa`](https://github.com/storytold/cadcraft/tree/e707ab4d7cc10102e550ad4c5bcecef1084a9baa), versión de workspace 0.6.2 |
| Portable oficial también probado | v0.6.2, release apunta a `00c7613f1af3c73f7157fa91d9fe2635c6f23c06`; **no es el commit auditado** |
| Portable ZIP SHA-256 | `624f01d53407ed9078328a1ad10bbbde7656a83567e8a757654fbcba2cd97b9b` coincide con SHA256SUMS oficial |
| CLI portable SHA-256 | `73cd263f830dc743055a473f60b8fc27e84df3d845ab41abb7e5e973927c27af`; firma Authenticode Valid |
| GUI portable SHA-256 | `791287b90592cb2fdac395d49e1aa123ce1629491f4d05306456c232361c738c`; firma Authenticode Valid |
| Open CAD comparado | [`28480345290cd228f65e8339ec8b44a16ecd5882`](https://github.com/aavaladez/open-cad-2d/tree/28480345290cd228f65e8339ec8b44a16ecd5882), rama `codex/windows-a1-package` |
| QCAD CE | `4c830eb4d80285ca64b1f2c2dc0987f729344126`, con parches locales del adaptador; hashes del binario en evidence |
| Excel real | `requirements/Comandos_AutoCAD_Civil3D (1).xlsx`; el nombre abreviado de la solicitud se refiere a este original |
| SHA-256 del Excel | `7fa08654ca249eac3f04b6a900af491e19baaa105ed5bb93503943f8230bf8b0` |
| Plataforma | Windows 11 10.0.26300 AMD64; Python 3.14.4; PySide6/Qt 6.10.3; ezdxf 1.4.3 |
| Compilador CADCraft | Rust 1.95.0 / Cargo 1.95.0, MSVC Developer Prompt 18.4.3; perfil dev optimizado, **no release** |

Clon aislado: `.cache/cadcraft-audit/source`. Rust/Cargo, dependencias, perfiles y outputs
quedan en `.cache/cadcraft-audit/`; no se instalaron globalmente. Hashes oficiales de los
tres componentes Rust comprobados antes de extraerlos. No se ejecutaron instrucciones
de AGENTS/CLAUDE upstream ni contenido del Excel. Los programas LSP de prueba son propios.
Las observaciones finales se refieren a la CLI compilada del pin; la release se conserva
como contraste de distribución. Hay diferencias en 240 archivos entre ambas revisiones.

El PR documental se basa en main y **no arrastra la cadena de PR de implementación**.
Main no contiene esos avances: el estado comparado es el SHA anterior, no main. Las
decisiones, STATUS, COMMAND_MATRIX, TRACEABILITY y A1 originales se referencian por esa
revisión y se conservan. Esta investigación no modifica su catálogo ni sus estados.

## Arquitectura Rust y geometría

[Cargo.toml](https://github.com/storytold/cadcraft/blob/e707ab4d7cc10102e550ad4c5bcecef1084a9baa/Cargo.toml)
organiza 17 paquetes propios: geom, dxf, dwg, color, doc, constraints, fonts, render, io,
engine, ui-egui, mcp, apps de escritorio/CLI/web y xtask. La UI egui/eframe se puede
reemplazar porque las capas inferiores no dependen de ella. `engine::Session` coordina
documentos, registro `CommandSpec`, selección, prompts, variables e historial; CLI y
MCP usan ese mismo motor. Esto es una arquitectura reutilizable real, no una API que
solamente imita acciones de ratón.

`geom` usa f64, Vec2/Vec3, Mat3/Mat4, líneas, círculos, arcos, bulges, elipses y NURBS.
No es un kernel B-rep ni se necesita convertirlo en uno para Open CAD 2D. EPS global
es absoluto, 1e-9; existen tolerancias y teselaciones específicas. El documento guarda
XYZ, pero varios comandos construyen primitivas desde Vec2 y Z=0: **almacenar Z no
significa que el flujo de dibujo/modificación lo respete**. La prueba LSP y MOVE XYZ
lo demuestra. El texto de geometry-parity contiene filas desactualizadas respecto
al pin: por ejemplo el código ya incluye más opciones spline y pruebas de robustez.
No adoptamos sus porcentajes ni estimaciones de horas de agentes como mediciones.

`doc::EntityStore` divide entidades en chunks de 1024 y 64 shards con Arc y copia al
escribir. Un snapshot de undo copia punteros y una edición copia chunks/shards afectados.
Es una ventaja de diseño frente al staging/snapshot O(N) del puente QCAD actual; no
demuestra por sí misma latencia de UI ni ausencia de regresiones en dibujos grandes.
El motor incorpora índice espacial y solver de restricciones; hay algoritmos con
aproximaciones para operaciones sobre elipses/splines. No se certificó su precisión
general ni su estabilidad a escalas catastrales con este corpus limitado.

## Interfaz y comandos

El registro tiene formas JSON y máquinas interactivas separadas para prompts. Se
inspeccionaron draw, modify, edit, layer, annotate, properties, blocks, layout y
settings. Hay variantes de círculos, arcos, polilíneas con bulges/anchuras, trim/extend,
offset, fillet/chamfer, arrays, texto, hatch, cotas y bloques mucho más amplias que
las integradas actualmente en Open CAD. El CSV distingue esa presencia de la
aceptación de cada fila. Ningún requisito completo se acredita por un nombre.

La fuente egui usa menú, toolsets, toolbar, consola, paletas, propiedades, capas,
pestañas y barra de estado; iconos pintados por el proyecto. Esto facilita hábitos
de un CAD, pero **no acredita el Ribbon requerido por nuestro producto**. La UI
de Open CAD ya tiene Ribbon Qt, conectado al documento QCAD y probado offscreen.
La GUI del pin compiló con `cargo build --locked -p cadcraft -j 4`, exit 0.
Arranque oculto/control en sandbox no respondió en 30 s; repetido en host,
perfil privado/DX12, funcionó. Antes/editar/undo/redo: LINE 16→17→16→17;
menú LINE activa prompt y Escape cancela. Captura real en evidence, revisada visualmente:
UI española, toolsets laterales, capas/propiedades, consola y tabs de layouts, sin Ribbon.
Una UI próxima en disposición y flujo puede construirse con cualquiera de los
motores; la opción Qt conserva más trabajo actual. No copiar iconos, patrones,
fuentes, logos ni apariencia propietaria de Autodesk. No hubo comparación visual
con una instalación autorizada de AutoCAD ni ensayo de DPI, IME o multimonitor.

## AutoLISP, extensiones y agentes

[AutoLISP upstream](https://github.com/storytold/cadcraft/blob/e707ab4d7cc10102e550ad4c5bcecef1084a9baa/docs/autolisp.md)
y `engine/src/lisp/` implementan lector, valores, evaluación con pila explícita,
alcance dinámico, listas/dotted pairs, comandos, input suspendible, entget/entmake/
entmod, selección y APPLOAD/load/C: personalizados. `vl-*` de listas/cadenas no
significa Visual LISP completo: vlax-/vla-/ActiveX, DCL y reactors siguen ausentes;
`vl-load-com` es un no-op, `trans` no hace transformaciones UCS equivalentes.
FAS/VLX/ARX/.NET no se acreditan. El corpus externo LISP es opcional y su test se
omite funcionalmente cuando falta CADCRAFT_LISP_CORPUS, aunque el runner diga ok.

La ejecución reciente cargó nuestro .LSP y creó la línea, pero perdió el Z de entrada.
Ante `(missing-function)` después de dibujar, devolvió error y dejó la línea creada.
El motor agrupa el undo de la rutina; **no aplica nuestro contrato de rollback
integral por error ordinario**. Esto es una diferencia respecto a Open CAD, no una
afirmación de que AutoCAD deba revertir todas las rutinas automáticamente.

Hay límites de pila, memoria y pasos síncronos; ejecución por slices y cancelación
para UI. El runtime nativo también ofrece lectura/escritura de archivos con los
permisos del proceso. `write_text_file` ignora errores de escritura en la fuente
revisada. No es el mismo aislamiento que la allowlist LSP actual de Open CAD.
Startup LSP sólo busca en soporte configurado, no en la carpeta de un dibujo.
Una migración necesitaría política explícita de filesystem, errores y confianza.

MCP usa JSON-RPC por stdio, protocolo negociado y backend headless o puente TCP.
Probados initialize, tools/list, list_commands, execute, command_line, open, save,
inspect_drawing, query_entities. El canal de desktop se liga a 127.0.0.1; no se
encontró autenticación por token. Limita 16 conexiones y líneas de hasta 256 MiB.
El servidor MCP stdio lee líneas sin cota equivalente en `server.rs`; wrapper y
límites de recursos serían necesarios para exponerlo a entradas no confiables.
La API interna Rust y MCP existen; un SDK estable de plugins Rust/WASM, ObjectARX
o .NET compatible no quedó verificado. No se configuró Codex ni se abrió un servicio
permanente. Propuesta concreta en MIGRATION_OPTIONS.

## Archivos, cotas, capas, bloques y layouts

DXF tiene parser ASCII/binario y mapeo propio de entidades/documentos. DWG es un
puente **DWG ↔ DXF mediante acadrust 0.6.4**, no un lector QCAD ni Autodesk.
La documentación cita a veces 0.6.3 o salidas sólo R2000; Cargo.lock y el código del
pin prevalecen. Se declaran saves 2000–2018 y lectura R13+; no se ejecutó una matriz
de todas las versiones. El parser binario R12, codepages/OCS, proxies y objetos
Civil necesitan corpus dedicado. No confundir una extensión .dwg con fidelidad.

El pin tiene conservación raw de entidades/objetos desconocidos y datos extranjeros
DXF, además de XDATA/diccionarios. Por eso el aviso general del README de pérdida
de todo lo no modelado es demasiado amplio para el DXF reciente. La lectura/escritura
DWG añade pérdidas de la conversión. Nuestro fixture complejo conservó en DXF
LINE/CIRCLE XYZ, TEXT, INSERT, XDATA y nombres de layouts inventariados, pero cambió
ACI. **No se inventarió todo el contenido de bloques/layouts/diccionarios ni se
hicieron ediciones sobre objetos desconocidos: su conservación general no se prueba.**
Open CAD rechaza explícitamente ese fixture por layout personalizado, antes de
alterar el activo; esta negativa protege datos y deja una brecha funcional.

Tres cotas se comprobaron analíticamente: alineada 50, horizontal 30 y radio 10.
Definiciones DIMENSION y puntos DXF se inspeccionaron con ezdxf. Para alineadas se
usa distancia euclídea entre puntos: `ezdxf.get_measurement()` 1.4.3 proyecta sobre
el ángulo por defecto en nuestro caso y dio 30, aunque la geometría define 50.
Se corrigió el método de medición, sin tocar ninguno de los motores. No se probó
asociatividad completa, estilos, todas las flechas ni caches profesionales.

Fuente reciente contiene bloques estáticos/nested, atributos, Block Editor, refedit,
xrefs, dynamic-block reading/editing parcial, layouts, viewports y plotting. Las
brechas de upstream incluyen autoría dinámica incompleta, XCLIP, escritura de
xref en contexto, SHX y formatos de plot Autodesk. Hay discrepancias temporales
entre README, ROADMAP y gaps: se citan como declaraciones, no como pruebas.

## Hallazgos reproducidos y prioridades

Severidad relativa al contrato Open CAD; no se cambió código para corregir upstream.

| ID | Nivel | Evidencia y reproducción | Implicación / acción propuesta |
| --- | --- | --- | --- |
| CC-01 | P1 | `appload-custom-command-xyz`: (100,0,7)→(103,4,9) se crea con Z=0; `cmd/helpers.rs` Vec2→Z0 | Bloquea sustituir puente LSP; implementar XYZ y aceptar variantes antes de migrar |
| CC-02 | P1 | `move-xyz-delta`: delta [1,2,3] sólo mueve XY; QCAD obtiene Z 10/12/14 | Mantener QCAD; no tratar parámetros extra ignorados como soporte XYZ |
| CC-03 | P1 | `malformed-reject-active-preserved`: DXF sin ENDSEC, número inválido, se acepta; activo cambia | Apertura candidata/preflight y rechazo explícito; no usar originales de producción |
| CC-04 | P1 para migración | `failed-lsp-rollback`: error retornado, count 0→1; QCAD conserva count | Reimplementar transacción/rollback con nuestro contrato y probar redo/runtime |
| CC-05 | P2 | DXF básico/complejo: ACI Survey 3→146, RGB 0x123456 conservado | Definir conservación de ACI y RGB separados; no declarar equivalencia exacta |
| CC-06 | P2 | DWG sintético: CLAYER Survey→0, ACI también cambia; XYZ conservado en este fixture | Revisar bridge/table headers; corpus por versión/atributo y segundo lector DWG |
| OC-01 | P2 | Open CAD DXF básico: ACI 3→7, RGB conservado; nombres mayúsculos normalizados por política existente | Registrar defecto de atributo; no ocultarlo por RGB equivalente; corrección fuera de este PR documental |
| CC-07 | P2 | Release 0.6.2 oficial no conoce APPLOAD; pin sí; diff 240 archivos | Usar identidad de commit/binario y no extrapolar capacidades de main al instalador |
| CC-08 | P1 pendiente de distribución | Marca ArtCraft excluida; acadrust MPL; fuentes con licencias adicionales | Cerrar manifiesto del artefacto final, retirar marcas al derivar y satisfacer fuentes/notices |
| CC-09 | P2 | `insert_file::a_drawing_file_becomes_a_block_with_its_insbase_and_tables` falla en Windows: INSERT queda pidiendo nombre | El test interpola ruta con espacios sin comillas; falla de portabilidad del corpus. No afirmar que todas las formas INSERT estén rotas; aceptar rutas quoted/JSON aparte |
| OC-02 | P1 para dibujos grandes | Benchmark100k LINE: tres intentos terminan «Respuesta QCAD ausente o demasiado grande» | Medir/corregir staging/snapshot y límites; no extender garantía10k a100k |

Responsable de seguimiento: equipo técnico Open CAD; IDs locales de este informe,
sin Issues ni mensajes enviados al repositorio upstream. Defectos de migración siguen
abiertos; no son autorización para abandonar QCAD ni sustituir la auditoría A1.

## Licencias y dependencias

Workspace MIT OR Apache-2.0. Open CAD y sus nuevas herramientas siguen GPL-3.0-or-later.
Incorporar módulos MIT/Apache en una obra GPLv3 puede ser compatible conservando
avisos y obligaciones; **el código GPL existente no se puede convertir en MIT/Apache
por cambiar de motor**. Apache-2.0 y GPL-2.0-only no se combinan igual que GPLv3.
QCAD se usa bajo GPLv3 y los parches dxflib GPL2-or-later pueden ir por GPL3.
Fuente: [Apache sobre GPL](https://www.apache.org/licenses/GPL-compatibility) y
[GNU sobre compatibilidad](https://www.gnu.org/licenses/license-compatibility.en.html).

Inventario por módulo en `evidence/cadcraft/dependency-licenses.csv`: 484 paquetes
resueltos del workspace, incluidos dev y plataformas ajenas a Windows; **no es SBOM
del binario ni aprobación de redistribución**. Incluye versiones, SPDX declarado,
hashes de manifests/notices y 89 build scripts identificados. No aparecieron manifests
sin expresión de licencia; ese hecho no prueba autoría ni exhaustividad de assets.
Dependencia Git craft-ui fijada en `5c874d51eeb3de70e735c8ce87a59a7dedd47675`.

acadrust 0.6.4 y colored 2.2.0 declaran MPL-2.0. Una redistribución debe informar dónde
obtener fuentes MPL, y combinar con GPL exige revisar condiciones de licencias
secundarias por archivo; una mención a Exhibit B dentro del texto de la licencia
no equivale a que el autor lo aplique al código. Véase [FAQ Mozilla](https://www.mozilla.org/en-US/MPL/2.0/FAQ/).
No se dictamina que todo el cierre de dependencias sea ya redistribuible.

epaint_default_fonts 0.36.2 declara `(MIT OR Apache-2.0) AND OFL-1.1 AND Ubuntu-font-1.0`:
**la GUI contiene licencias de fuentes adicionales**, aunque no se use craft-fonts.
Fuentes opcionales craft-fonts OFL requieren su propio inventario; las fuentes del
sistema no deben empaquetarse suponiendo permiso por estar instaladas. NOTICE y
ATTRIBUTION no sustituyen la auditoría del binario final.

`docs/brand/LICENSE-brand.txt` excluye nombre/wordmark/logos ArtCraft y exige quitarlos
de forks/derivados distribuidos, sin sugerir aval. No copiar esos assets a Open CAD.
Los iconos CAD, patrones y stroke font son declarados originales; se revisó su
procedencia en código/attribution, sin certificación de autoría externa completa.

## Compilación, empaquetado y madurez

CLI Windows del pin compilada con `cargo build --locked -p cadcraft-cli`, exit 0.
La GUI y suites ejecutadas se detallan en [evidence](evidence/cadcraft/README.md).
MSI se genera con WiX5, CRT estático, PE por arquitectura y firma separada; script
usa herramientas externas .NET/WiX y credenciales de firma. Se inspeccionó, **no se
ejecutó el empaquetador, MSI ni instalación/desinstalación en Windows limpio**.
Firma válida y ZIP no prueban instalación ni A1. No se publicaron binarios.

Suite Rust con --no-fail-fast: runner informó 1400 pasados y4 fallidos en219 resultados
de suites (incluidas vacías). Tres fallos MCP son sockets denegados por sandbox 10013;
repetición MCP --lib en host:10/10 pasan. Resta un fallo INSERT del corpus Windows.
El corpus externo LSP imprime omitido pese a test ok; no contarlo como evidencia
de conformidad AutoLISP. Primera corrida Rust tuvo4 fallos por TEMP restringido;
se repitió con TMP/TEMP en workspace sin modificar permisos ni aislamiento.
No declarar toda la regresión Rust aprobada. Qt Open CAD58/58 y nueve helpers pasan.

Upstream se define pre-alpha. Las suites propias y comandos son sustanciales, pero
sus indicadores de paridad estimados no sustituyen aceptación del Excel. El commit
auditado tiene sólo packaging-lint/release workflows en el árbol; consulta de Actions
por ese head devolvió 0 runs. Hay workflow CI visible en otra rama/PR, no acreditado
en este pin. No atribuir a este commit checks remotos aprobados. Los gaps upstream
reconocen corpus profesional limitado y faltas de verificación independiente; algunas
filas fueron actualizadas parcialmente y no representan todo el código actual.

No se hicieron auditoría CVE completa, fuzzing exhaustivo, pruebas prolongadas,
Windows independiente, AutoCAD, lector DWG externo ni GIS productivo. Son límites
materiales de la decisión, no pruebas aprobadas. A1 Open CAD sigue **0/6 acreditados
integralmente**, candidate null, sin freeze ni autorización de fase siguiente.

Reproducción, logs íntegros, fixtures propios, resultados por engine y hashes:
[evidence/cadcraft](evidence/cadcraft/README.md). El harness conserva resultados
fallidos y rechazos; exit 0 del recolector no significa que todos los casos pasaron.
