# Interoperabilidad

Para A1, demostrar abrir/editar/guardar/reabrir DXF en la candidata, conservación
semántica del corpus y contraste con segundo motor, según AUDIT_GATE.md. El
roundtrip ezdxf→ezdxf temporal no acredita integración QCAD ni ausencia general
de pérdidas. Verificados los seis criterios, congelar y PAUSAR tras la auditoría.

DXF del prototipo: ezdxf 1.4.3, exportación R2010. Subconjunto de entidades LINE
XYZ y CIRCLE centro XYZ en plano XY, capa actual, capas visibles/bloqueadas/color RGB
e INSUNITS. Guardado temporal y sustitución final. Sin requisito de AutoCAD instalado.

Importación rechaza entidades distintas, bloques definidos/presentaciones con
contenido, XDATA/extension dictionaries detectados, linetypes/lineweights por entidad,
truecolor por entidad, espesor, OCS de círculos no XY y ciertos atributos de capa.
No se garantiza conservación general del resto de metadatos DXF, tablas o objetos;
no usar el prototipo para editar archivos de producción. Se regeneran handles/IDs
y estructura DXF. Frozen layers y estilos avanzados aún no implementados.

Los tests prueban Z, unidades, capas y errores del subconjunto. Lectura directa
ezdxf/audit verifica salida del writer sin el mapeo OPEN CAD, pero comparte backend.
Roundtrip no demuestra interoperabilidad con otro motor. Lectura en QCAD, LibreCAD
o AutoCAD aún pendiente. Agregar corpus por versión antes de ampliar afirmaciones.

DWG no implementado: sufijo rechazado. QCAD ofrece DWG opcional mediante plugin
propietario; no incorporado. LibreCAD 3 tiene opción experimental de lectura abierta
desactivada por defecto; no se probó. Evaluar biblioteca abierta con licencia/corpus,
conservación de objetos proxy y advertencias por versión. Escritura independiente
requiere pruebas propias, no se deduce de lectura.
