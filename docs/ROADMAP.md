# Plan ejecutable

No hay fecha prometida de paridad profesional. Cada etapa tiene dependencia y
aceptación verificable. Priorizar corrección y conservación sobre cantidad de botones.

| Etapa | Trabajo | Dependencia | Salida / aceptación |
| --- | --- | --- | --- |
| M0 | Auditoría, Excel, gobierno, skills, prototipo | Archivos y repositorios públicos | Matriz de 472 filas, fuentes fijadas, pruebas y PR; sin comandos del Excel completados |
| M1 | Toolchain Qt6/C++ y build QCAD CE fijado; inventario licencias | M0 | Build repetible Windows, smoke documento/transacción/Z/DXF, logs y CI de upstream |
| M2 | Adaptador de motor y CommandBus; alias/selección/undo | M1 | Reproducir contratos LINE/CIRCLE/LAYER/MOVE; mismos resultados analíticos con QCAD |
| M3 | UI original: Ribbon, consola, propiedades editables, capas, OSNAP/ORTHO, pestañas | M2 | QtTest/teclado, estados/cancelación, DPI/accesibilidad; múltiples documentos y autosave |
| M4 | Geometría y anotación | M2/M3 | PLINE/ARC, recorte/extensión/offset, bloques/texto/cotas/hatch por variantes del Excel |
| M5 | LSP expandido, editor, macros/extensiones | M2; subconjunto ya probado en M0 | entget/entmod/ssget/getpoint/envs/errores y corpus LSP; diferencias documentadas |
| M6 | DXF completo y corpus externo; DWG lectura abierta | M2/M4 y auditoría biblioteca | Versiones/capas/bloques/layouts/Z/XDATA, pérdidas explícitas y motor externo |
| M7 | Presentaciones, plot/PDF, instalador y release | M3/M4/M6 | Escalas, viewports, fuentes correspondientes, install/uninstall y archivo firmado si disponible |
| M8 | GIS/topografía/terreno 2D+Z | Motor base y formatos | EPSG/reproyección, SHP/GeoTIFF/LandXML, COGO/TIN/curvas/parcelas por contratos |

## Próxima iteración prioritaria

1. Revisar PR inicial: CI del prototipo aprobada en las tres plataformas y portable
   Windows arrancado en el runner. Mantener M0 sin comandos completos acreditados.
2. Continuar M1: toolchain aislado y build CE local ya aprobados, con smoke C++
   de geometría/Z. Acreditar documento/transacciones/DXF, SBOM y build remoto.
3. Completar contratos de LINE y CIRCLE, incluyendo variantes ausentes, y llevar
   fixtures al backend QCAD antes de ampliar el motor temporal.
4. Expandir capacidades por Issues pequeños: selección, OSNAP, PLINE/ARC,
   recorte/offset, texto/cotas y persistencia. Cada PR actualiza matriz y status.

Roles de las skills: reverse-engineering → command-cloner o UI/LSP/interop →
regression-testing. No se crea un nuevo repositorio ni se reinicia el proyecto.

Avance posterior M1/M2: documento QCAD y adaptador experimental UI/bus/LSP
probados; native/DOCUMENT.md y native/ADAPTER.md. Siguiente PR: importación DXF
temporal con preflight conservador y contraste independiente antes de reemplazar
el documento, guardado/reapertura sin pérdidas del subconjunto admitido. Después,
propiedades editables/selección/comandos esenciales y acotación, recuperación y
empaquetado/instalación funcional. Mantener variantes del Excel trazables y parciales.

Ciclo DXF posterior comprobado en fixtures R2000/R2010 y UI, limitado a LINE/CIRCLE,
con writer híbrido documentado. Siguiente prioridad M3/M4: propiedades editables,
selección y acotación; mantener ampliación de corpus/entidades y recuperación antes
de preparar instalador A1. La CI nativa limpia sigue necesaria en cada PR.

2026-10-12: CI de #13/#14 comprobada; propiedades/selección integradas y verificadas
en el subconjunto LINE/CIRCLE, con persistencia. Siguiente módulo A1: geometría y
modificación esenciales/acotación, con ampliación conjunta de representaciones UI
y conservación DXF. Instalación Windows en runner limpio sigue obligatoria; no
sustituirla por pruebas del portable temporal. Evidencia de desarrollo aún parcial.

COPY/ROTATE/SCALE posteriores verificados para LINE/CIRCLE en QCAD y DXF. Mantener
prioridad de dibujo ARC/PLINE y acotación, con representaciones/conservación conjunta;
TRIM/EXTEND/OFFSET y pruebas de instalación siguen pendientes para A1. No iniciar
módulos GIS/presentaciones avanzadas ni otros comandos antes del punto de control.

ARC/PLINE posteriores integrados con selección, propiedades, transformaciones y
DXF para el subconjunto recto/planar documentado. PR #13–#16 tienen CI general y
nativa aprobada; sus dependencias se conservan. Siguiente secuencia A1: TRIM/EXTEND
con límites geométricos/selección, OFFSET con lado/distancia verificados, acotación
lineal/alineada/radio en documento y DXF, consolidación LSP/recuperación, después
empaquetado nativo/instalación/desinstalación en Windows limpio. No ampliar catálogo.
Las variantes faltantes se registran sin bloquear desarrollo de capacidades A1;
ninguna se declara completa ni ningún criterio A1 se acredita con evidencia parcial.

TRIM/EXTEND LINE con límites finitos y OFFSET LINE/CIRCLE/ARC posteriores verificados
en UI/Qt y DXF. Mantener sus variantes avanzadas pendientes. Próxima prioridad A1:
acotación lineal/alineada/radio nativa editable y persistente; consolidar LSP y
recuperación, preparar paquete nativo e instalador y pruebas funcionales limpias.

Cotas posteriores DIMLINEAR/DIMALIGNED/DIMRADIUS integradas con propiedades,
historial, Z y DXF para preset Standard acotado; no asociación paramétrica ni paridad
de estilos. Siguiente módulo A1: consolidar programas LSP sobre comandos existentes,
recuperación, paquete QCAD/Qt nativo e instalación/ejecución/desinstalación limpia.
Probar la misma candidata en los seis criterios antes de congelar y auditar.

Bridge LSP posterior sobre capacidades esenciales consolidadas y corpus propio
comprobados. Próximo trabajo A1: recuperación tras fallo/cierre, paquete nativo
QCAD/Qt y validación install/run/reopen/uninstall en Windows limpio. Los requisitos
restantes del catálogo no son prioridad antes del punto de control y auditoría.

## Punto de control A1 — primera auditoría integral obligatoria

Decisión del director 2026-10-09, prioritaria sobre continuidad automática.
Mantener M1→M2→M3 y los subconjuntos necesarios de M4/M5/M6/M7 para verificar los
seis criterios de [AUDIT_GATE.md](AUDIT_GATE.md). Adelantar instalación Windows
funcional desde M7; presentaciones/plot avanzados, DWG y M8 siguen en el roadmap,
pero no condicionan A1. No esperar a completar las 472 entradas.

Al verificarse los seis criterios: detener funciones nuevas, congelar candidata,
regresión y compatibilidad, auditoría integral y registro de defectos/correcciones.
Mantener la congelación durante correcciones y repetir pruebas afectadas. PAUSAR
con informe reproducible. La siguiente fase requiere cero defectos bloqueantes
y aprobación explícita del director. Una regresión no elimina la congelación.

2026-10-12, recuperación posterior: copias privadas del documento confirmado y
restauración QCAD con historia/LSP reiniciados, comprobadas durante caída del hijo.
native/RECOVERY.md. No ampliar comandos secundarios: siguiente entrega es paquete
nativo Windows, dependencias/fuentes/licencias y pruebas de instalar/usar/desinstalar
en entorno limpio identificado. A1 sigue parcial y sin candidata congelada.

2026-10-12, paquete posterior: instalador compilado y aplicación instalada probada
en el desarrollador (342 comprobaciones, desinstalación/original intacto). Detener
ampliaciones: resolver acceso Windows limpio independiente, revisar distribución
y construir/reproducir desde commit estable. WINDOWS_A1_INSTALLATION.md describe
exactamente la aceptación pendiente. Ningún criterio integral ni freeze acreditado.
