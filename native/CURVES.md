# ARC y PLINE sobre el documento QCAD

Subconjunto A1, GPL-3.0-or-later. Conserva arquitectura/commits de PR #13–#16.
Contratos del Excel: ACAD-0008 ARC y ACAD-0003 PLINE, sin ampliar el catálogo.
No hay funciones nuevas en el modelo temporal: qcad_views.py sólo proyecta el
documento nativo en dataclasses inmutables para pintar y presentar propiedades.

## Contratos y límites

- `ARC p-inicio p-intermedio p-fin`: RArc::createFrom3Points, XY con Z planar.
  El lugar geométrico horario se canonicaliza a ángulos antihorarios DXF; no se
  conserva un atributo de recorrido inicial/final horario. Selección sigue el
  arco, no su círculo soporte. Puntos colineales/coincidentes/no planares se rechazan.
- `ARC CENTER centro radio grados-inicio grados-fin`: radio positivo y ángulos
  normalizados; incluye cruce por 0°. Ángulos coincidentes/círculo completo se
  rechazan. Sintaxis propia documentada; no afirmar prompts AutoCAD idénticos.
- `PLINE p p [p ...] [C|CLOSE]`: una RPolylineEntity, segmentos rectos sin anchura,
  Z planar, abierta o cerrada con al menos tres vértices. No es una cadena de LINE.
  Vértices sucesivos/segmento de cierre degenerados se rechazan.
- Ribbon ARC por tres clicks. PLINE reúne puntos sin confirmar; Finalizar/Enter
  confirma abierta, Cerrar/CLOSE cerrada; Escape descarta el lote. Una transacción
  por entidad, mismo bus que la consola, aliases A/PL configurables.
- Propiedades ARC centro/radio/ángulos; PLINE vértices XYZ/elevación/cierre; capa
  común. Vértices se aplican antes de elevación explícita, independientemente del
  orden JSON. Clones validados, selección XY punto/ventana/cruce y transformaciones
  QCAD MOVE/COPY/ROTATE/SCALE/ERASE; bloqueo/errores no mutan documento ni redo.

Pendientes ARC: otras combinaciones centro/extremo/ángulo, cuerda, dirección,
continuación, coordenadas relativas y precisión interactiva/OSNAP. Pendientes
PLINE: segmentos de arco/bulge, anchura constante/variable, Undo de vértice y opciones
de continuación. COMMAND LSP para ARC/PLINE sigue bloqueado en esta iteración;
el corpus anterior de rutinas propias debe continuar pasando. Ambos qcad_partial.

## Conservación DXF

Preflight admite ARC y LWPOLYLINE recta de anchura cero R2000/R2010, extrusión
estándar, atributos BYLAYER y las capas/unidades del subconjunto previo. Bulges,
anchuras (incluido el vértice final), PLINEGEN y POLYLINE heredada/3D se rechazan.
No hay degradación silenciosa a segmentos LINE. Writer final sigue CE/ezdxf híbrido
R2010; aplicar límites de DXF_APPLICATION.md. Entradas originales no se reescriben.

El pin QCAD perdía ARC.center.z y elevación LWPOLYLINE al importar/exportar.
`qcad-dxf-arc-polyline-z.patch` cambia sólo .cpp: centro Z del arco y elevación
del primer vértice guardada en la polilínea; salida LWPOLYLINE grupo 38, sólo R2000.
No cambia tamaño/ABI del importador. Un primer experimento con miembro adicional
falló por asignación inline en un consumidor compilado con la cabecera anterior;
se descartó y la regresión documental se repitió. RPolylineData activa PLINEGEN
por defecto; el adaptador lo desactiva explícitamente para su contrato sin linetypes.
Estos hallazgos no acreditan corrección general de DXF, OCS ni POLYLINE 3D.

## Reproducir

```powershell
./tools/build_qcad.ps1
python tools/check_qcad_curves.py --binary build/native/opencad-qcad-engine.exe --source .cache/upstream/qcad --qt .cache/qt/6.10.3/msvc2022_64 --output build/qcad-curves
ctest --test-dir build/native --output-on-failure
```

Baseline analítico: arco centro (0,0,7), radio 5, semicircunferencia superior;
inferior por puntos en sentido horario; arco centro (20,0,11) de 350° a 30°;
PLINE (30,0,13)→(40,0,13)→(40,10,13). COPY +(3,4,5), ROTATE +90° sobre origen,
SCALE 2 con Z intacta, propiedades, capas, rechazo/redo y fixtures propios en dos
versiones. ezdxf inspecciona archivos del writer CE; luego QCAD reabre el writer
final ezdxf. No son dos lectores externos distintos del writer final.
QtTest ejercita botones, clicks, Escape, consola y paneles; PNG se inspecciona.
Diálogos de archivo se prueban en la suite DXF anterior. No instalación ni AutoCAD.

Fuentes públicas consultadas 2026-10-12 (el código del pin prevalece):
[ARC](https://help.autodesk.com/cloudhelp/2022/ENU/AutoCAD-Core/files/GUID-30ECFD30-A1D6-4D60-9DD1-B487603F6772.htm),
[LWPOLYLINE DXF](https://help.autodesk.com/cloudhelp/2015/ENU/AutoCAD-DXF/files/GUID-748FC305-F3F2-4F74-825A-61F04D757A50.htm),
[QCAD RPolylineData](https://qcad.org/doc/qcad/latest/developer/class_r_polyline_data.html),
[ezdxf LWPolyline](https://ezdxf.readthedocs.io/en/stable/dxfentities/lwpolyline.html).

Actualización LSP posterior: COMMAND ARC/PLINE habilitado para estas entradas
completas con allowlist nativa explícita; plan_a1.lsp y LISP_ESSENTIAL.md. Variantes
geométricas restantes y prompts/selección ENAME siguen pendientes. No A1 instalada.
