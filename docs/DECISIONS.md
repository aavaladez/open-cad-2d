# Decisiones técnicas

| ID | Fecha | Decisión y evidencia | Consecuencia / revisión |
| --- | --- | --- | --- |
| ADR-001 | 2026-10-09 | Preservar íntegramente Excel con IDs hoja/fila y SHA-256 | 472 entradas y 8 notas; exclusiones 3D visibles; regeneración determinista |
| ADR-002 | 2026-10-09 | QCAD CE como base seleccionada tras auditoría comparativa | Fijar commit; aceptar sólo tras spike compilado de documento, undo y DXF; LC3 alternativa |
| ADR-003 | 2026-10-09 | Qt6/C++ como destino, Python/PySide6 temporal por ausencia de toolchain | Prototipo permite pruebas hoy; no declarar QCAD integrado ni mantener segundo motor profesional |
| ADR-004 | 2026-10-09 | GPL-3.0-or-later para fuente original OPEN CAD | Revisar por módulo y avisos; sin plugins comerciales ni activos Autodesk |
| ADR-005 | 2026-10-09 | DXF acotado LINE/CIRCLE y ezdxf para prototipo | Z/capas/INSUNITS probados; bloquear entidades/atributos detectados fuera del subconjunto; DWG pendiente |
| ADR-006 | 2026-10-09 | AutoLISP por intérprete explícito y puente CommandBus | Tamaño/profundidad/pasos acotados; funciones faltantes fallan; sin COM/red/shell |
| ADR-007 | 2026-10-09 | Seis skills versionadas con helpers y tests | Inicialización sin sobrescribir skills previas; no generan evidencia ficticia |
| ADR-008 | 2026-10-09 | Repo público aavaladez/open-cad-2d y rama codex/initial-audit | Autorización del director para elegir/crear repo; cambios por PR, no merge automático |

Las decisiones de implementación son revisables con resultados. Ninguna añade
gastos, disminuye protecciones o modifica los requisitos por preferencia del agente.

## ADR-009 — Spike nativo comprobado y parche mínimo

2026-10-09: Qt 6.10.3/MSVC aislados, cuatro flags -L de QCAD sustituidos por
target_link_directories entrecomillado; pin y aplicación idempotente verificados.
Build CE y fixture geométrico C++ aprobados. QCAD Qt6 requiere qcadjsapi/qtjsapi
adicionales para ECMAScript; auditados, sin integrar. El build no acredita comandos
ni adaptador documental. Mantener M1 parcial y PR independiente sobre M0.

## ADR-010 — Primera auditoría integral y detención obligatoria

2026-10-09, decisión explícita del director. A1 requiere seis demostraciones
funcionales: QCAD documental/persistente, UI, comandos esenciales/acotación,
LSP/comandos propios, ciclo DXF conservador e instalación Windows probada.
No exige completar el catálogo de 472 entradas. Reutilizar las seis skills y
añadir cad-audit-gate. Criterios/evidencias en AUDIT_GATE.md.

Al cumplir los seis: detener funciones nuevas y congelar candidata; regresión,
compatibilidad y auditoría de arquitectura/código/UI/rendimiento/estabilidad/LSP/
DXF/deuda/licencias/dependencias/seguridad. Registrar severidad y correcciones,
resolver bloqueantes, generar informe y PAUSAR. Ninguna aprobación técnica
automática sustituye aprobación del usuario para la siguiente fase. Regla
prioritaria sobre instrucciones previas de continuar después del punto de control.

## ADR-011 — Documento QCAD probado antes del adaptador de aplicación

2026-10-09: fixture original RDocument/RDocumentInterface y plugin DXF CE con
registro explícito, sin descubrimiento/carga de plugins comerciales. Documento
real DXF R2000 producido por ezdxf, edición transaccional y contraste independiente
de salida. Mantener QCAD como documento autoritativo; no ampliar el motor temporal.

La prueba reprodujo pérdida de Z en importación LINE/CIRCLE y exportación CIRCLE.
Parche GPL original de cuatro líneas, pin y git apply --check/reverse --check.
Aceptación local del subconjunto aprobada; no acredita DXF general, OCS arbitrario
ni A1. RDocumentInterface posee/destruye RDocument; éste posee storage/index.
Usar QStringLiteral en texto de operaciones para evitar resolución al overload bool
(la llamada con literal char* eligió atributos actuales y desactivó undo).

Compilar fixture y upstream en Release para coincidir en runtime. Declarar todos
los productos importados y dependencias de los parches; repetir el build incremental
upstream para no comprobar un plugin antiguo después de editar fuentes.

## ADR-012 — UI existente sobre documento QCAD autoritativo

2026-10-09: conservar UI/CommandBus/LSP y conectar un proceso C++ QCAD por pipes.
La integración funcional local prueba que las ediciones provienen del documento
nativo; las dataclasses Python son vistas descartables, no un segundo motor.
Staging clona objetos QCAD y confirma una sola RTransaction por comando/script;
rollback conserva historial redo y estado de capas. Las comprobaciones funcionales
usan geometría analítica, QtTest y rutinas LSP originales.

Proceso local con dispatch explícito, sin red ni plugins descubiertos. Pin/protocolo
verificados; fallo del motor explícito sin fallback. DXF UI deshabilitado hasta
validación conservadora. Uso Windows de desarrollo, sin autosave ni instalación;
O(N), timeout y límites de mensajes documentados en native/ADAPTER.md. Revisar
rendimiento/recuperación antes de A1. Continúa aceptación parcial y cero completos.

## ADR-013 — DXF conservador y writer híbrido comprobado

2026-10-09: preflight ezdxf y proceso QCAD candidato impiden descartar dibujo
activo tras error. Sustituir sólo después de contrastar importación y exportación;
confirmación UI explícita del reemplazo/historial. Guardar temporal en el filesystem
del destino, contrastar inventario y reemplazar atómicamente. Conservar undo/redo.

Reproducidas pérdidas CLAYER/OFF; parches GPL mínimos al pin. La salida CE aislada
también necesita reparación de owners en diccionarios estándar. Admitir sólo las
reparaciones estructurales identificadas en salida propia, contrastar semántica y
escribir R2010 canónico ezdxf con auditoría sin reparaciones. Nunca reparar entradas
silenciosamente ni proclamar writer CE globalmente corregido. Los defaults/handles
se regeneran; no admitir metadatos personalizados detectados. Documentar deuda,
dos backends y límites en DXF_APPLICATION.md antes de ampliar corpus/formato.

## ADR-014 — Propiedades y selección en el adaptador existente

2026-10-12: consultar selección con formas QCAD proyectadas en XY; conservar XYZ
autoritativo. Editar propiedades mediante clones/staging, validando todas las entidades
antes de reemplazar objetos y confirmar una transacción. UI sólo presenta valores y
mantiene IDs de selección; sin segundo motor. Aplicación explícita y undo/redo.
Crear Defpoints al inicializar dibujos nuevos evita diferencias con exportación CE.
Native/EDITING.md registra contratos, límites y pruebas; no añadir comandos fuera
de las prioridades A1 ni declarar paridad/criterios completos por evidencia parcial.

## ADR-015 — Transformaciones 2D con Z conservada

2026-10-12: COPY por desplazamiento XYZ y ROTATE/SCALE en XY con Z sin escalar/girar,
según alcance 2D del producto. Usar primitivas QCAD sobre clones y validar todos los
resultados antes del commit. Nuevas entidades mediante API pública, sin modificar
IDs protegidos. Registro de comandos sólo en QcadCommandBus; el prototipo temporal
y la lista COMMAND LSP no anuncian funciones ausentes. TRANSFORMS.md registra variantes
pendientes y baseline analítico; no atribuir equivalencia 3D ni opciones completas.

## ADR-016 — ARC y PLINE nativas y conservación conjunta

2026-10-12: RArc::createFrom3Points y RArcData para geometría de arco; una
RPolylineEntity por PLINE recta abierta/cerrada, Z planar. No extender el motor
temporal. Proyecciones inmutables en qcad_views.py, selección con formas nativas,
transformaciones del adaptador, edición validada de geometría/capa. ARC horario
se canonicaliza a DXF antihorario conservando lugar geométrico, no recorrido.
PLINE interactiva confirma todo el lote o lo descarta al cancelar. Vértices antes
de elevación explícita en propiedades; rechazar bulges/anchuras todavía ausentes.

Corregir ARC Z/LWPOLYLINE elevación en .cpp del pin, sin cambiar tamaño ABI del
importador. Experimento inicial de cabecera provocó fallo en consumidor inline
obsoleto y se descartó; fixture documental y CTest repetidos después. QCAD activa
PLINEGEN al construir datos: desactivar explícitamente en el subconjunto validado.
Sólo ampliar DXF cuando entidades/atributos y writer CE/final contrastan. Mantener
writer híbrido y sus límites. CURVES.md registra fuentes, contratos y evidencias.
No cerrar ARC/PLINE completos: variantes del Excel todavía pendientes, A1 0/6.

## ADR-017 — Límites finitos, selección y precisión separada

2026-10-12: extraer operaciones geométricas del adaptador a geometry_ops.cpp,
con formas QCAD públicas compartidas con selección. TRIM retira intervalo LINE
seleccionado entre cortes finitos, conserva ambas piezas si es interior y confirma
un lote; EXTEND elige límite más cercano más allá del extremo indicado. Proyección
XY e interpolación/extrapolación Z de la LINE original; no usar Z del límite como
Z resultante. Separar tolerancia de pick (píxeles/UI) de precisión de intersección
1e-9. Rechazar picks ambiguos y variantes ausentes; no inventar límites infinitos.

OFFSET usa getOffsetShapes LINE/CIRCLE/ARC y restaura Z retenida; lado XY, radio
no positivo rechazado. Nuevas IDs desde constructores públicos, fuente/capa intacta.
Límites bloqueados son consultables sin edición; objetivo bloqueado se rechaza.
CUTTING.md documenta contratos/pending y baselines independientes. No ampliar
el modelo temporal, sin equivalencia de todas las variantes ni aceptación A1.

## ADR-018 — Cotas nativas y cachés gráficos contrastados

2026-10-12: RDimRotated/Aligned/RadialEntity y RDimStyleProxyBasic GPL de CE;
documento autoritativo, datos XYZ/medida, propiedades/undo y rendering común a UI/DXF.
Separar datos dimensionales de su cache gráfico. Inicializar también propiedades
de clases base. Excluir coordenadas derivadas automáticas de etiqueta del diff
RTransaction para que undo/redo no convierta su posición en manual por efectos
de setters CE. Prueba reproduce fallo y compara render/medida/historial tras corregir.

Writer CE no tiene bloques obligatorios: retener datos de definición en inspección
independiente mediante placeholders sólo en memoria, registrados, nunca salida.
Writer final agrega DIMENSION/*D con formas/etiqueta nativas y audit sin reparaciones.
Preflight sólo admite el preset, contenidos acotados y cache coincidente con el
render candidato; no descartar anotaciones/cache personalizados detectados.
Parche Z en QCAD/dxflib sin ABI nueva, licencia GPL2-or-later compatible conGPL3.
R2000 Qt6 pierde texto codepage: transcodificar temporal ezdxf→R2010 UTF8 tras
preflight y equivalencia, retener ruta/original. Canonicalizar hex Unicode CE para
lector ezdxf; no admitir formato rico. DIMENSIONS.md registra hallazgos y límites.
No hay asociación paramétrica ni estilos avanzados; parcial, sin entrada A1 instalada.
