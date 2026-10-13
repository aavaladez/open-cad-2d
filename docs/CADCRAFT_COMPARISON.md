# Comparación por requisitos y experimentos

Fecha 2026-10-13. Comparación del pin CADCraft e707ab4 con Open CAD 2848034.
**Hay 472 filas conservadas, cero requisitos con aceptación completa en CADCraft
y cero completos en Open CAD. Esto no significa que los programas no funcionen.**
Significa que nuestra metodología exige todas las variantes y evidencia por fila.

## Metodología de cobertura

La fuente es el Excel original de SHA-256 `7fa08654ca249eac3f04b6a900af491e19baaa105ed5bb93503943f8230bf8b0`.
Sus 422 filas AutoCAD y 50 Civil 3D/Map se mantienen en
[cadcraft_coverage.csv](../requirements/cadcraft_coverage.csv); las 8 notas originales
se conservan en el catálogo del pin Open CAD y no se cuentan como comandos. ID
estable ACAD/GEO y, adicionalmente, clave hoja+número de fila. Source_cells conserva
las celdas originales, duplicados, grupos y nombres «—»; no se ejecutan como código.

Se cotejó coverage.json, catálogo y contratos existentes. El CSV mantiene estado
original Open CAD, backend, variante, implementación, tests, Issue, revisión,
hash de spec y opciones pendientes. Specs antiguos pueden conservar estado histórico
prototype_partial: el estado de integración se toma de coverage.json, sin borrar
esa discrepancia temporal. No se cambia el catálogo ni se regenera COMMAND_MATRIX
porque no cambiaron sus entradas ni implementaciones.

Regla de los cinco estados solicitados:

| Estado | Evidencia mínima y límite |
| --- | --- |
| Implementado y verificado en CADCraft | Todas las partes y variantes de la fila, errores/cancelación/undo/capas/Z relevantes aceptados en el mismo pin; ninguna fila alcanza esto |
| Parcialmente implementado | Caso funcional propio ejecutado con resultado limitado o brecha reproducida; case IDs enlazan al detalle, incluido fallo de una variante |
| Declarado en documentación, sin prueba | Documentación/contrato API y fuente/registro/alias o función equivalente localizados, sin aceptación funcional específica de la fila; puede haber tests internos, pero no se les atribuye el contrato completo |
| No implementado | No se encontró equivalente integrado de la función en las rutas revisadas; también se aplica a brechas explícitas/stubs; no afirma imposibilidad futura |
| No aplicable al alcance CAD 2D | Exclusión previa del catálogo, conservada con motivo; no se inventan nuevas exclusiones para mejorar cifras |

Registrar un nombre sólo permite localizar fuente. APIs equivalentes se señalan
como tales: properties.set no acredita CHANGE/CHPROP ni sus prompts; layerstate.list
no acredita toda LAYERSTATE; una parte de una celda agrupada no acredita la fila.
Variables almacenadas no demuestran sus efectos. Alias se resuelven desde la fuente
real, sin eliminar prefijos '-' a ciegas. Las 50 funciones geoespaciales, incluso
sin nombre, se evaluaron por función/ruta y no tienen equivalente integrado encontrado.
3DPOLY permanece requisito 2D con Z; no se excluye por su nombre.

| Clasificación de filas | CADCraft | Open CAD |
| --- | ---: | ---: |
| Completo y verificado | 0 | 0 |
| Parcial | 24 | 25 |
| Declarado/localizado sin aceptación de fila | 211 | 0 |
| No implementado en la integración revisada | 176 | 386 |
| Excluido del alcance 2D | 61 | 61 |
| Total | 472 | 472 |

No son porcentajes de compatibilidad ni ranking de calidad. Open CAD cuenta
**24 qcad_partial y un prototype_partial (DIST)**; la columna backend distingue
el último. Pending puede tener fuente QCAD encontrada y aun así carecer de integración.
El CSV no equipara el QCAD upstream completo con el Open CAD instalado actual.
Un comando no probado de CADCraft puede ser más capaz que uno parcial de Open CAD;
su estado refleja evidencia disponible, no orden de mérito.

## Casos equivalentes ejecutados

Inputs sintéticos propios y expectativas analíticas, tolerancia absoluta 1e-9 en
coordenadas/medidas pequeñas. El lector de ambos DXF es ezdxf 1.4.3; en Open CAD el
writer final es híbrido CE/ezdxf, por lo que no es un segundo motor independiente
del último writer; sí hay reapertura QCAD. CADCraft tiene parser/writer propios.
DWG usa acadrust y reabre por ese mismo bridge: **sin lector DWG independiente**.

| Caso | Open CAD / QCAD | CADCraft del pin |
| --- | --- | --- |
| LINE (0,0)→(3,4); CIRCLE centro (10,10), radio2 | Pasa | Pasa |
| Selección ventana, propiedad capa, MOVE XY, undo y redo | Pasa | Pasa vía MCP/JSON; panel UI no acreditado por esto |
| COPY delta (1,2), ROTATE90, SCALE2 | Pasan expectativas analíticas | Pasan las mismas expectativas |
| ERASE + undo | Pasa | Pasa |
| TRIM LINE con límite x=1.5, EXTEND hasta x=6 | Pasa | Pasa en modo standard; otras opciones no probadas |
| OFFSET LINE distancia5 hacia (-4,3) | Pasa | Pasa |
| ARC centro/radio5, 0–90; PLINE tres vértices cerrada | Pasa | Pasa en XY |
| DIMALIGNED50 / DIMLINEAR30 / DIMRADIUS10 | Pasa | Pasa; no certifica todos los DIM* |
| Carga .LSP propio + C:AUDITCAD con XYZ | Pasa XYZ 7/9 | Carga/ejecución sí; Z pasa a0: falla variante |
| Error LSP tras dibujar; rollback esperado por Open CAD | Pasa | Retiene línea; falla nuestro contrato |
| DXF R2010 básico, abrir/guardar/reabrir | Geometría XYZ/RGB/unidades/capa actual conservadas; ACI3→7 | Geometría XYZ/RGB/unidades/capa actual conservadas; ACI3→146 |
| DXF complejo con blockref, TEXT, bulge, XDATA y layout | Rechazado explícitamente, fuera del subconjunto | Inventario limitado conservado excepto ACI; no prueba conservación interna completa de bloques/layouts |
| MOVE delta (1,2,3) sobre XYZ leído | Pasa con Z10/12/14 | Sólo XY: falla Z solicitado |
| DXF truncado, sin ENDSEC y número inválido | Rechaza; activo conservado | Acepta y cambia activo: falla |
| Dibujo con 10,002 entidades (10,001 LINE + CIRCLE) | Abre y consulta | Abre y consulta |
| DWG sintético guardar/reabrir→DXF | No disponible; **no verificado** | XYZ conservado; CLAYER→0, ACI cambia: falla equivalencia exacta |

Los DXF preservados son copias, nunca originales sobrescritos. Nombres de capa se
comparan en mayúsculas porque QCAD documenta esa normalización; ACI y RGB **se
comparan separados**, sin normalizar away sus diferencias. Handles/tablas de soporte
regeneradas no forman parte de la equivalencia declarada. No inferir soporte de
entidades que no se inventariaron.

## Pruebas locales adicionales y omisiones

Se repitió `python -m unittest discover -s tests -v` con QT_QPA_PLATFORM=offscreen
y dependencias privadas ya existentes: **58/58 aprobadas**. La primera ejecución
sin PYTHONPATH de dependencias falló importando ezdxf/PySide; se conserva el log.
El runner de pruebas también imprime el caso sintético de gate 6/6 y un subprocess
«NO TESTS RAN»: son negativos de sus tests, **no el estado real A1 ni la suite principal**.

Nueve helpers QCAD repetidos, exit 0: application, dxf, editing, transforms, curves,
cutting, dimensions, lisp_essential y recovery. Los reportes son aplicación local
parcial; no convierten instalación de desarrollo en Windows limpio. Los fixtures
de aplicación existentes se ejercitaron además de los nuevos casos comparativos.
Suite Rust, GUI y resultados de ejecución quedan desglosados en evidence/README.

No ejecutados: AutoCAD black-box, todas las variantes de 472 filas, corpus profesional
autorizado, DWG independiente, todas las versiones/binary/codepages, proxy Civil,
GIS, geodesia, DCL/COM, instalación MSI/Windows limpio, soak/crash fuzzing, DPI/IME.
No se etiqueta como aprobado un workflow existente ni un corpus opcional omitido.

## Rendimiento

La prueba equivalente mide **abrir y consultar** el mismo DXF de 10,002 entidades
en cada proceso, con time.perf_counter; el resultado exacto está en results.json.
Es una ejecución por motor, sin warmup normalizado, medición de memoria máxima,
estadística de colas ni múltiples GPUs. CADCraft usa perfil dev
optimizado y MCP headless; QCAD usa el puente real con preflight, copias candidatas,
validación y snapshots JSON. **No es un benchmark equivalente de kernels ni de FPS**.

Se amplió con fixtures LINE XYZ de 1k/10k/100k y **tres procesos nuevos por motor/tamaño**,
sin warmup, time.perf_counter y comprobación de count. Benchmark/results.json:

| LINE | CADCraft CLI info, mediana s | Puente Open CAD QCAD, mediana s | Resultado |
| --- | ---: | ---: | --- |
| 1.000 | 0.016 | 1.968 | Ambos 3/3 abren y cuentan |
| 10.000 | 0.072 | 6.228 | Ambos 3/3 abren y cuentan |
| 100.000 | 0.721 | 18.603 hasta error | CADCraft 3/3; QCAD 0/3, error registrado |

Los tiempos incluyen arranque nuevo. QCAD además abre candidato, hace preflight/
contraste y obtiene vistas; CADCraft info no cumple esas mismas garantías. No
comparar kernels mediante cociente ni considerar mediana de error como operación
completada. No se midió pico de memoria, save/render/undo de 100k ni 1M de entidades.
El fallo100k es una limitación real del puente integrado que impide recomendar
QCAD sin abordar rendimiento, aun conservándolo como base.

La CLI responde mucho antes en este caso; el mecanismo COW y queries paginadas son
prometedores. El coste del preflight/bridge QCAD y su límite de snapshot4MB/timeout15s
son deuda que merece medirse aparte. No se publica un factor de velocidad ni se
extrapola a dibujos profesionales. Un dibujo de 10k no demuestra escalabilidad
general; la decisión de migrar necesitaría 1k/10k/100k/1M, al menos cinco repeticiones,
mediana/p95, memoria, import/edit/undo/save/render, mismas garantías de validación y
corpus de entidades mixtas con georreferencia.

El portable oficial se ejecutó aparte: carece de APPLOAD. Sus resultados no se
mezclan con la matriz del pin reciente. Que ambas revisiones digan versión0.6.2
es precisamente una razón para fijar commit y hash del ejecutable.
