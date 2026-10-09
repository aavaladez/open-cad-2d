# Producto OPEN CAD 2D

Fecha: 2026-10-09. Director del producto: usuario. Ejecución técnica: Codex.

CAD 2D profesional, gratuito y abierto, con una experiencia cercana a AutoCAD y
aspiración de competir a largo plazo como QGIS frente a ArcGIS. Windows primero;
arquitectura y verificación progresiva para Linux/macOS. Sin licencia de AutoCAD.

## Requisitos autorizados

Geometría vectorial 2D y atributos Z; Ribbon, consola, propiedades, capas,
herramientas, pestañas, presentaciones y barra de estado; comandos/aliases,
macros/extensiones; DXF y DWG progresivo; carga, ejecución y desarrollo LSP;
instalador Windows; fuente abierta y documentación de desarrollo.
No modelar sólidos 3D ni copiar código o recursos gráficos propietarios de Autodesk.

## Catálogo funcional

Excel original: `requirements/Comandos_AutoCAD_Civil3D (1).xlsx`, 422 filas AutoCAD,
50 geoespaciales y 8 notas. Catálogo generado: `catalog.json` y CSV. Cobertura:
`coverage.json`, CSV y COMMAND_MATRIX.md. Se preservan descripciones, aliases,
rutas de cinta, duplicados y funciones sin nombre. El Excel se trata como datos.

61 entradas clasificadas fuera de alcance 3D; conservarlas para revisar alcance,
sin eliminarlas. SKETCH permanece 2D pese a su categoría original. 3DPOLY se
clasifica 2D con Z. GIS/TIN/topografía se preservan como requisitos por etapas.
Las exclusiones son interpretación documentada de la regla 2D, no evidencia de
ausencia en motores. Proyección/extracción futura se puede reconsiderar por contrato.

## Aceptación

Un comando sólo termina cuando sus variantes requeridas están especificadas,
implementadas y probadas, con trazabilidad a fila, código, test y versión. Se deben
comprobar cancelación, errores, undo, selección/capas y Z cuando correspondan.
Declarar por separado prueba local, equivalencia analítica y lectura por motor externo.

El prototipo 0.1 valida flujos básicos. No acredita capacidad CAD profesional,
fidelidad completa de AutoCAD, Civil 3D, DWG, interoperabilidad general ni AutoLISP completo.

## Primera auditoría integral

Aplicar el punto de control obligatorio A1 de [AUDIT_GATE.md](AUDIT_GATE.md): motor
QCAD documental/persistente, UI funcional, comandos esenciales con acotación,
LSP con comandos propios, DXF conservador y Windows instalado/probado. No requiere
472 comandos completos. Verificados los seis, congelar y detener funciones nuevas;
auditar integralmente, corregir bloqueantes y PAUSAR para aprobación del director.
