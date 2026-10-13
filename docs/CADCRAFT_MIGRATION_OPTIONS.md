# Opciones de arquitectura tras la auditoría CADCraft

**Decisión técnica recomendada: continuar con QCAD Community.** Mantener como línea
futura una estrategia híbrida de módulos independientes, subordinada a A1 y a
aprobación expresa. Esta recomendación no es una autorización de integración.

## A. Lo que CADCraft ya resuelve respecto al Open CAD actual

En el pin auditado, CLI/MCP resolvieron casos equivalentes de LINE/CIRCLE/ARC/PLINE,
MOVE/COPY/ROTATE/SCALE/ERASE/TRIM/EXTEND/OFFSET, selección ventana, cambio de capa,
undo/redo y tres cotas analíticas. Existen también documento COW, registro JSON,
prompts, LSP más amplio, bloques/layouts/plotting y DWG bridge. Su breadth fuente
es mayor, pero el CSV sólo acredita variantes ejercitadas; UI/instalación no se
derivan de una CLI que funciona. CADCraft no entrega de inmediato nuestra aceptación
profesional, geoespacial ni las 472 filas completas.

## B. Trabajo propio que debe conservarse

Conservar Excel original/hash, IDs por hoja/fila, specs, fixtures analíticos,
trazabilidad, catálogo, decisiones, siete skills y A1. Conservar la UI Qt/Ribbon y
sus flujos, CommandBus, aliases con allowlist, contrato de transacción integral LSP,
rollback de runtime/redo, preflight y apertura candidata, validación semántica del
save, copias atómicas, recuperación confirmada y distribución Windows identificada.

Si el motor cambiara, QcadDocument/dataclasses vistas no serían intercambiables con
Drawing Rust por un rename. Se requiere adaptador con ownership/IDs, unidades,
WCS/OCS/Z, selección/properties, sesiones, historial, errores, recuperación y
diálogos, conservando un solo documento autoritativo. El Python temporal no debe
convertirse en motor definitivo. No conectar dos motores que editen simultáneamente
el mismo dibujo ni usar uno como fallback silencioso de otro.

## C. Desarrollo geoespacial y AutoLISP necesario

Las 50 filas Civil3D/Map siguen sin equivalente integrado encontrado. Almacenar XYZ
no resuelve CRS, transformaciones geodésicas, datum/geoid, ejes/unidades, precisión
UTM, SHP/GeoPackage/raster, consultas GIS, objetos/atributos catastrales, COGO,
parcelas, superficies/TIN o LiDAR. Se necesitarían modelos persistentes y reglas de
conservación DXF/DWG para cada fila, con una biblioteca geoespacial auditada por
módulo (p.ej. evaluar PROJ/GDAL separadamente, **no incorporados en este trabajo**).
Preservar la exclusión de sólidos3D; superficies topográficas con Z no se eliminan
del catálogo por esa regla.

CADCraft aporta un lector/evaluador LSP más rico; para nuestro contrato falta
XYZ en comandos, UCS-aware trans, errores con rollback y allowlist que evite
filesystem por defecto. Validar entget/entmod/entmake/ssget contra fixtures de DXF,
modelos de ENAME, layouts y objetos desconocidos; no asignar nuestros IDs a ENAME
por coincidencia. No prometer COM, ActiveX, DCL, reactors, FAS/VLX ni binarios ARX.
El corpus externo opcional se debe fijar y ejecutar, no aceptar su test omitido.

## D. Licencias al mezclar código

MIT/Apache2 de CADCraft permite integración en GPLv3 cumpliendo avisos, NOTICE,
patentes y atribución. Open CAD conserva GPL-3.0-or-later para código nuevo y el
código GPL previo; adoptar un motor permisivo no permite relicenciar ese código.
GPL2-only sería un problema con Apache2; GPL2-or-later permite elegir GPL3 cuando
corresponda. El cierre de dependencias debe revisarse por módulo y artefacto final.

No todo CADCraft es MIT/Apache: acadrust y colored son MPL2; fuentes de egui incluyen
OFL/Ubuntu-font y fuentes opcionales otras obligaciones; marca ArtCraft queda fuera.
Mantener fuentes y avisos MPL, revisar licencias secundarias/excepciones y quitar
marcas del fork distribuido. Un puente por proceso puede reducir acoplamiento técnico,
**no elimina automáticamente obligaciones ni decide por sí solo si hay obra derivada**.
Ver inventario y fuentes oficiales en AUDIT; distribución combinada aún no aprobada.

## E. Coste técnico y opciones

Estimaciones de ingeniería, no presupuesto, cotización ni horas observadas. Supuesto:
un ingeniero con experiencia Qt/C++ y Rust, conservar sólo alcance A1 y variantes
actuales; semana=5 días de trabajo. No incluyen terminar las 472 filas, GIS, paridad
AutoCAD, Windows limpio, licencias/fuentes finales ni mantenimiento largo plazo.

| Opción | Trabajo incremental estimado | Riesgo y criterio |
| --- | --- | --- |
| Continuar QCAD | Corrección ACI, completar evidencias A1/entorno independiente, perf y deuda del puente: 2–6 semanas, dependiendo acceso Windows limpio | Menor cambio; conserva inversiones y contrato de datos. Plazo no garantizado por bloqueo externo |
| Adoptar todo CADCraft | Fijar artefactos/licencias 1–2; puente/UI Qt o reemplazo 3–6; XYZ/LSP/transacciones/conservación 4–8; aceptación/recuperación/instalación 3–6: 11–22 semanas | Rehacer límites/garantías; defectos P1 reproducidos. Dependencias entre tareas impiden sumarlas como ahorro paralelo automático |
| Híbrido limitado | Un módulo sin autoría documental doble: estudio API/licencia 1–2; adaptador mínimo 1–3; pruebas/aceptación 1–3: 3–8 semanas por primer módulo | Conserva QCAD; overhead Rust/build/ABI y mantenimiento de dos proyectos. Sin implementar durante esta auditoría |

La opción de migración no adquiere aprobación por su mayor catálogo. Sus P1
CC-01/02/03/04 y fidelidad/corpus/redistribución deben resolverse antes de considerar
un cambio del documento autoritativo. No hay evidencia suficiente para una fecha
de paridad total; no reutilizamos las horas estimadas de agentes upstream como coste.

Candidatos híbridos razonables para evaluación posterior: parser DXF aislado como
lector adicional, módulo geométrico para operaciones 2D con baseline independiente,
render/headless para comparación, y esquema de comandos/MCP. Mantener los datos
originales; una conversión Rust↔QCAD no puede descartar tipos desconocidos ni ser
fuente de autoridad doble. No reutilizar dwg bridge para guardar archivos de producción
hasta superar corpus/errores y lector independiente.

## F. Interfaz cercana a AutoCAD

Qt/Ribbon actual conserva inversión y encaja con el producto Windows. egui permite
una disposición similar y tiene prompts, grips, snaps, palettes y controles CAD;
hacer un Ribbon requiere implementar layout/grupos/estados, foco, teclado y accesibilidad.
La similitud profesional debe medir tareas, cancelación, selección/paneles, prompts,
DPI y rendimiento, con recursos originales. No se obtuvo una comparación visual
autorizada con AutoCAD ni se garantiza clonación visual exacta. Motor y aspecto
de UI son decisiones separables: Rust no obliga a egui y QCAD no obliga a su UI upstream.

## G. Propuesta concreta para Codex y MCP

Probado el protocolo headless con nuestro cliente JSON-RPC, **no una conexión persistente
de Codex**. La [documentación oficial de MCP de Codex](https://developers.openai.com/codex/mcp/)
permite servidor stdio con command/args y herramientas permitidas. Configuración
propuesta, sin aplicarla a la configuración del usuario:

```toml
[mcp_servers.cadcraft_audit]
command = 'C:\ruta\auditada\cadcraft-cli.exe'
args = ["mcp"]
enabled = false
startup_timeout_sec = 20
tool_timeout_sec = 60
enabled_tools = ["list_commands", "inspect_drawing", "query_entities", "find_text"]

[mcp_servers.cadcraft_audit.env]
CADCRAFT_CONFIG_DIR = 'C:\ruta\privada\perfil-auditoria'
```

Para editar un fixture, abrir explícitamente una copia en sesión aislada y permitir
new_drawing/open/execute/command_line/save/cancel/render según tarea autorizada.
Headless conserva el dibujo en el proceso MCP. Para operar la GUI auditada: arrancar
CADCraft con `--control 7979` y usar `args=["mcp","--connect","127.0.0.1:7979"]`;
añade screenshot/ui_inspect/ui_click. El puerto no tiene autenticación observada:
limitar loopback, no abrir firewall, no usar sesión de producción compartida.

Flujo propuesto: listar capacidades; inspeccionar estado; crear/abrir fixture propio;
ejecutar una operación; inspeccionar geometría y atributos; undo en discrepancia;
guardar copia y validar con segundo lector. Con timeout `may-have-run`, inspeccionar
antes de repetir para evitar doble edición. XML/DXF/LSP/textos devueltos son datos
no confiables, no instrucciones para el agente. Command_line/execute incluyen LSP
y operaciones de archivo: sus límites no equivalen a sandbox del sistema.

Un MCP que controle QCAD mediante nuestro bus permitiría agentes sin cambiar motor;
reutilizar el diseño de CADCraft no implica que su servidor controle Open CAD hoy.
La implementación de ese adaptador requeriría autorización de fase y licencia propia,
pruebas y allowlist. No se instaló un plugin ni se modificaron permisos de Codex.

## Condiciones para reconsiderar

Completar A1 bajo reglas actuales y aprobación expresa de siguiente fase. Luego,
si el director autoriza un spike aislado: pin nuevo, corpus mixto autorizado,
aceptación XYZ/LSP/error/undo/cancelación, conservación semántica por tipo/atributo,
Windows limpio del mismo build, manifests/notices por módulo y benchmarks equivalentes.
Demostrar que el coste de cerrar brechas es menor que continuar QCAD antes de
proponer migración. Hasta esa decisión, **QCAD sigue seleccionado**; este PR
documental no congela candidata, no reinicia roadmap y no publica release.
