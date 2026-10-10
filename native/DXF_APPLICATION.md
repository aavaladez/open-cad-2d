# DXF de aplicación QCAD — subconjunto conservador

`QcadDocument.open_dxf/save_dxf` conectan UI, bus y LSP al mismo documento QCAD.
No amplían el modelo temporal. Abrir confirma en UI la sustitución del dibujo y
su historial; cancelar o fallar deja vivo el proceso/documento anterior. Los diálogos
de ruta/confirmación se sustituyen por respuestas deterministas en QtTest.

## Flujo y límites

1. ezdxf 1.4.3 inventaría el original sin escribirlo. Se rechaza cualquier reparación
   de entrada, datos fuera del subconjunto, XDATA, diccionarios de extensión, bloques,
   grupos y tablas/objetos personalizados detectados.
2. Importar en un proceso QCAD candidato. Restaurar CLAYER desde el inventario
   previamente validado; comparar geometría, capas y unidades contra el lector.
3. Exportar candidato y contrastar con ezdxf antes de sustituir el proceso activo.
   Mantener el objeto puente para que bus/UI/LSP sigan apuntando al mismo documento.
4. Guardar a temporal privado en el directorio de destino. Validar exportación CE,
   generar DXF R2010 canónico mediante ezdxf y validar de nuevo antes de os.replace.
   No reemplazar destino ante fallo. Guardar conserva undo/redo del documento.

Admitidos R2000/R2010, LINE XYZ y CIRCLE XY+Z con extrusión estándar, sin espesor,
color/linetype/lineweight BYLAYER, escala 1, capas CONTINUOUS con pesos válidos,
ACI/RGB, ON/OFF/LOCK, capa actual e INSUNITS. Máximo de entrada 20 MB; este límite
no sustituye el límite menor de snapshot ni acredita rendimiento de dibujos grandes.
Se normaliza mayúsculas de nombres de tabla; handles, versión y tablas estándar
vacías/de soporte se regeneran. No preserva todos sus parámetros: corpus profesional,
estilos avanzados, ARC/PLINE/textos/cotas/layouts/XDATA/OCS arbitrario siguen pendientes.
La advertencia previa informa estos límites. No declarar DXF general ni usar producción.

## Problemas reproducidos y tratamiento

- CLAYER: CE no restaura la capa actual y tenía desactivado su código DXF de salida.
  El adaptador restaura sólo después de validar; qcad-dxf-clayer.patch permite código
  8 y exporta la capa autoritativa. Pin/git apply --check/reverse --check obligatorios.
- OFF: writeLayer invertía el color y dxflib lo invertía de nuevo. El parche original
  qcad-dxf-layer-off.patch evita la primera inversión. Caso locked-off.dxf comprobado.
  Al reabrir, CE convertía además OFF en FROZEN; qcad-dxf-off-import.patch conserva
  las dos banderas separadas. Frozen permanece fuera del subconjunto admitido.
- Salida CE contiene owners inválidos en diccionarios estándar y un setting interno
  ColorSettings/BackgroundColor. La inspección admite únicamente código de auditoría
  ezdxf 202 con los mensajes estructurales identificados, exclusivamente para el
  archivo recién generado. No se admiten reparaciones de entrada ni de geometría.
  El archivo final se reconstruye desde el inventario contrastado en R2010, con
  defaults ezdxf, y debe pasar auditoría sin reparaciones. El informe identifica
  final_writer=ezdxf R2010 y native_audit_repairs; no ocultar el writer híbrido.

Esto mitiga la salida estructural para el subconjunto. La exportación CE aislada
no queda reparada globalmente; registrar esta deuda antes de ampliar metadatos.
No equiparar lectura independiente del writer QCAD con dos lectores independientes
del writer ezdxf final. La reapertura final sí se verifica en QCAD y se contrasta.

## Reproducción y resultados

```powershell
./tools/build_qcad.ps1
python tools/check_qcad_dxf.py --binary build/native/opencad-qcad-engine.exe --source .cache/upstream/qcad --qt .cache/qt/6.10.3/msvc2022_64 --output build/dxf-application
ctest --test-dir build/native --output-on-failure
```

El helper coloca su scratch en su directorio de evidencias para que los procesos
puedan compartirlo dentro del entorno restringido; no modifica protecciones.
24 comprobaciones por runtime Python 3.12/3.14: dos versiones, MOVE analítico XYZ,
undo/redo después de guardar, conservación del original, rechazo sin mutar activo,
capas nuevas/flags, UI abrir/cancelar/editar/guardar/reabrir y PNG inspeccionado.
46 tests de regresión por runtime (cinco nuevos de límites/atomicidad), aplicación
general 28 comprobaciones, CTest 5/5. Evidencias en docs/evidence/qcad-dxf*.

No instalada, sin AutoCAD ni lector externo adicional. A1 permanece 0/6.
Fuentes públicas: [API QCAD](https://qcad.org/doc/qcad/latest/developer/class_r_document_interface.html),
[capas ezdxf](https://ezdxf.readthedocs.io/en/stable/tables/layer_table_entry.html),
[atributos gráficos](https://ezdxf.readthedocs.io/en/stable/tutorials/common_graphical_attributes.html).
El comportamiento del pin auditado y sus pruebas prevalece sobre documentación latest.
