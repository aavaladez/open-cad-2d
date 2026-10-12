# Cotas 2D en el documento QCAD — subconjunto A1

Código GPL-3.0-or-later, módulo dimensions.cpp y RDimStyleProxyBasic de QCAD CE
del pin auditado. Se inicializan RDimensionEntity y RDimLinearEntity antes de sus
tipos concretos. No usar plugins comerciales ni representar cotas como LINE/TEXT
explosionadas del modelo: son entidades DIMENSION autoritativas con ID/historial.

## Contratos del Excel y operación

- ACAD-0176 `DIMLINEAR inicio fin posición [grados]`, alias DLI. Horizontal por
  defecto; vertical 90°, otras direcciones explícitas. RDimRotatedEntity, medida
  proyectada sobre la dirección elegida. Ribbon horizontal/vertical por tres clicks.
- ACAD-0177 `DIMALIGNED inicio fin posición`, alias DAL. RDimAlignedEntity con
  medida del segmento planar. Ribbon: dos extremos y posición de la línea de cota.
- ACAD-0179 `DIMRADIUS centro punto-de-radio`, alias DRA; o
  `DIMRADIUS ENTITY id pick`, con CIRCLE/ARC leído y proyección del chord en QCAD.
  RDimRadialEntity, medida radial y etiqueta automática R. Ribbon selecciona curva.
- Puntos XYZ finitos y con Z común; rechazar medida no positiva/no planar. Mantener
  Z en definición, extremos/chord, MOVE/COPY/ROTATE/SCALE y DXF. Texto simple Unicode
  BMP hasta 256 caracteres, sustitución <> de medida; rechazar controles/formato rico.
- Propiedades: extremos/definición/ángulo, chord y texto según tipo; capa común.
  Validar clones como lote, una transacción por edición/creación, undo/redo y rollback.
  El panel muestra sólo filas aplicables. Selección geométrica nativa de trazos/flechas,
  ventana/cruce; selección sobre glifos de texto, grips y asociación automática pendientes.
- Líneas/flechas y posición/ángulo de etiqueta provienen del renderizador CE abierto.
  Qt pinta esas vistas; escala/rotación/centrado de etiqueta y recursos gráficos propios.
  Glyphs Qt y métricas CE pueden diferir: fonts, DPI y tipografía avanzada pendientes.

Estas cotas pertenecen al documento y persisten como DIMENSION. No son todavía
restricciones asociativas: editar una geometría fuente no actualiza automáticamente
la cota que la midió. No afirmar DIMASSOC/relaciones paramétricas. COMMAND LSP de
estas tres operaciones sigue pendiente en esta entrega; se conserva corpus anterior.
Otros estilos/tolerancias/posiciones manuales de texto/texto rico y opciones del
catálogo quedan pendientes. Los tres comandos qcad_partial, cero completos.

## Historial y conservación

RTransaction calcula diferencias de propiedades. Los setters CE de coordenadas
de etiqueta cambian su modo a posición manual al reproducir undo/redo; registrar
coordenadas calculadas provocó flags 128 no solicitados tras deshacer. Para cotas
automáticas, el adaptador excluye sólo esas tres coordenadas derivadas del diff y
mantiene las propiedades autoritativas. El renderizador recalcula la etiqueta.
Pruebas comparan entidad/medida/gráficos tras undo/redo y guardado. No se desactivan
permisos ni comprobaciones de geometría para evitar el fallo.

QCAD/dxflib perdían Z de definición y extremos/chord. Parche .cpp acotado
qcad-dxf-dimension-z.patch corrige esos campos sin cambiar ABI. dxflib es
GPL-2.0-or-later según su cabecera, compatible con GPL-3.0-or-later usado aquí.
La conversión de ángulos la hace ya dxflib: conservarla, con vertical 90° verificada.

CE exporta datos de definición, pero omite bloques gráficos obligatorios. El lector
de salida propia agrega placeholders únicamente en memoria para que audit no
elimine esas DIMENSION antes de leer/contrastar sus datos; nunca los guarda.
Registrar la carencia como opencad-ce-dimension-cache en native_audit_repairs.
El writer final híbrido crea DIMENSION y bloques *D con LINE/SOLID/TEXT desde
las formas/etiquetas nativas verificadas, y pasa audit sin reparaciones. No se
amplía la lista de errores audit ignorados ni se permite reparar entradas del usuario.
El writer CE aislado sigue incompleto. Fuente y archivo de destino se conservan
ante rechazo; guardar no modifica historial.

Sólo preset Standard declarado en qcad_dimensions_io.py, extrusión estándar,
texto automático y atributos BYLAYER. Tablas/handles/caches derivados se regeneran,
según aviso UI. Admitir sólo bloques gráficos anónimos exclusivos, tipos/atributos
acotados, sin contenido no representable. Antes de promover una apertura, comparar
el cache del original con render CE del candidato: modificaciones de texto,
rotación o geometría en el bloque se rechazan, no se eliminan silenciosamente.

CE Qt6 interpreta strings char* como UTF8 incluso en R2000 legado. El flujo de
apertura convierte con ezdxf el subconjunto ya preflighted a R2010 UTF8 temporal,
compara semántica, carga y mantiene ruta original; nunca reescribe el original.
El reporte identifica input_normalization. R2010 se importa directamente.
QCAD escribe escapes Unicode con hex minúscula, que ezdxf1.4.3 no decodifica;
normalizar sólo cuatro dígitos hex válidos antes de decodificar. No aceptar otros
códigos de control; Unicode no BMP y codepages/corpus amplios siguen pendientes.

## Evidencia y reproducción

Baseline independiente: (0,0,7)→(30,40,7) mide 50 alineada, 30 horizontal, 40
vertical; radio (80,20,11)→(90,20,11) mide 10. Cambiar extremo a(60,80,7)
mide100; COPY+(3,4,5), ROTATE+90° y SCALE2 retienen Z y medidas esperadas.
Native IDs, texto/<>/UTF8, capa bloqueada, errores/redo y fixtures R2000/R2010.

```powershell
./tools/build_qcad.ps1
python tools/check_qcad_dimensions.py --binary build/native/opencad-qcad-engine.exe --source .cache/upstream/qcad --qt .cache/qt/6.10.3/msvc2022_64 --output build/qcad-dimensions
ctest --test-dir build/native --output-on-failure
```

58 comprobaciones funcionales por runtime Python3.12/3.14; casos QtTest de los
cuatro botones Ribbon, consola/panel/Escape, DXF conservado, cachés inválidos
rechazados y originales intactos. Regresión51/51 por runtime; CTest10/10.
Reportes/hashes/captura en docs/evidence/qcad-dimensions*. No ejecución AutoCAD,
comparación de tipografía externa ni instalación Windows. A1 continúa0/6.

Fuentes públicas consultadas2026-10-12:
[DIMLINEAR](https://help.autodesk.com/cloudhelp/2025/ENU/AutoCAD-Core/files/GUID-E908848F-4621-43D2-B377-FD3FBC2B8848.htm),
[cotas AutoCAD](https://help.autodesk.com/cloudhelp/2015/ENU/AutoCAD-Core/files/GUID-9810D35D-E975-49E2-88EA-51FE4ACC92DB.htm),
[DIMENSION/blocks](https://ezdxf.readthedocs.io/en/stable/dxfentities/dimension.html).
API real RDimStyleProxyBasic, RDim*Data/Entity y RDxfImporter/Exporter del pin;
encoding.py de ezdxf1.4.3 contrastada localmente. No copiar recursos Autodesk.
