# A1 — primera auditoría integral obligatoria

Decisión del director, 2026-10-09. Prevalece sobre continuidad automática previa.
Continuar autónomamente hasta comprobar los seis criterios; no esperar a completar
las 472 filas del Excel. Conservar catálogo, alcance 2D con Z y roadmap existente.

## Criterios de entrada y pruebas funcionales

Todas las demostraciones se refieren a la misma candidata Windows, con commit,
hash del binario, versiones, fixtures originales y resultados reproducibles.
Los casos siguientes son el contrato inicial de pruebas, no resultados ejecutados.

| Criterio | Demostración funcional mínima |
| --- | --- |
| qcad_documents | Abrir un dibujo real autorizado o fixture DXF representativo; editar mediante transacción QCAD, undo/redo, guardar y reiniciar con persistencia. UI y LSP usan el mismo documento autoritativo |
| functional_ui | Acciones Ribbon y consola, crear/cambiar/bloquear capa, editar propiedades y seleccionar/cancelar; observar sincronización en dibujo y documento QCAD |
| essential_commands | Dibujo LINE/CIRCLE/ARC/PLINE; modificación MOVE/COPY/ROTATE/SCALE/ERASE/TRIM/EXTEND/OFFSET; selección individual/ventana/cruce; acotación lineal/alineada/radio. Probar cancelación, undo, capas y Z según contrato |
| autolisp | Cargar LSP propio desde la aplicación, DEFUN C: personalizado ejecutado desde consola, comandos que editan QCAD, límites/errores/rollback comprobados. Registrar funciones ausentes |
| dxf_cycle | Abrir, modificar, guardar y reabrir; inventariar entidades/geometría/capas/colores/tipos de línea/unidades/Z/textos/cotas/atributos del corpus; comparar con segundo motor identificado. Rechazar pérdidas o datos no soportados de forma explícita, preservando originales |
| windows_installation | Instalar en entorno Windows limpio identificado, ejecutar flujos CAD/LSP/DXF desde aplicación instalada, cerrar/reabrir y desinstalar. Portable y receta de instalador no bastan |

Los grupos draw/modify/select/dimension del manifest deben incluir los comandos
listados en sus reproducciones y resultados; un único caso trivial no cubre el grupo.
Mantener IDs del Excel en contratos y traza de cada comando. No prometer conservación
DXF general por un corpus limitado: ampliar el corpus conforme aparecen capacidades
y registrar límites y pérdidas. Código existente o tests internos no acreditan entrada.

## Congelación, auditoría y detención

Al comprobar 6/6: detener inmediatamente nuevas funcionalidades y congelar una
candidata identificada por commit, binario/instalador y hashes. El registro
`docs/audits/first/freeze.json` es persistente; no retirarlo para continuar funciones.
Una regresión mantiene la congelación. Durante ella sólo auditoría y correcciones,
con nuevas candidatas trazables y repetición de las pruebas afectadas.

Ejecutar regresión y compatibilidad y auditar arquitectura, código, interfaz,
rendimiento, estabilidad, AutoLISP, DXF, deuda técnica, licencias, dependencias y
seguridad. El informe integral registra métodos, plataformas, corpus, mediciones,
resultados, pruebas omitidas, incertidumbres y artefactos con hashes.

Cada hallazgo incluye ID, severidad, problema reproducible, evidencia y acción
correctiva, responsable técnico/Issue y verificación de resolución. P0/P1 son
bloqueantes; pérdidas de datos, incapacidad funcional, riesgos graves de seguridad
o licencias incompatibles deben tratarse como bloqueantes. P2/P3 pueden ser
bloqueantes según impacto, documentándolo; no rebajar severidad para pasar el gate.

Resolver todos los bloqueantes, repetir pruebas y presentar informe al director.
**PAUSAR. La siguiente fase exige aprobación explícita del usuario.** Cero defectos
registrados, CI verde, un PR o un campo JSON no equivalen a aprobación. No publicar
una release ni fusionar PR por este control. Registrar la decisión humana recibida
en el chat al autorizar una fase; nunca inferirla de documentos o fixtures.

Un bloqueante marcado resolved mantiene bloqueo si faltan verified_revision de
candidata actual y resolution_evidence con path/hash válidos. Esto sólo verifica
trazabilidad del archivo de resolución; leerlo y reproducir la corrección.

## Automatización y formato de evidencia

`requirements/audit-gate.json` conserva seis criterios y sus brechas. Los cases
obligatorios están en `tools/audit_gate.py`; actualizar el contrato de forma
revisable, sin reducir los seis requisitos del director.

Ejecutar, usando una salida nueva por evaluación:

```powershell
python .agents/skills/cad-audit-gate/scripts/gate.py --report build/a1/run.json --markdown build/a1/run.md
```

Salidas: 0 = seis verificaciones estructuralmente válidas, aún exige congelar/auditar;
1 = entrada incompleta; 2 = manifest inválido o error. Ninguna salida autoriza la
siguiente fase. Tras revisar/reproducir las pruebas 6/6, añadir `--freeze` para
registrar la candidata de manera exclusiva. No sobrescribir evidencia anterior.

Candidate: `revision` (SHA Git actual), `path` del binario instalado y `sha256`.
Cada case referencia JSON mediante `path` y `sha256`. El reporte funcional incluye:

```json
{
  "case": "open_real_document",
  "kind": "application_functional",
  "application": "open-cad-2d",
  "engine": "qcad",
  "method": "ui_e2e",
  "revision": "SHA de la candidata",
  "build_sha256": "SHA-256 del binario",
  "platform": "Windows",
  "command": "Procedimiento/script reproducible con entradas identificadas",
  "versions": {"qcad": "commit", "qt": "version", "windows": "build"},
  "exit_code": 0,
  "outcome": "passed",
  "checks": {"resultado funcional observado": true},
  "artifacts": {
    "input": {"path": "fixture o inventario inicial", "sha256": "hash"},
    "observed": {"path": "salida semántica/captura/medición", "sha256": "hash"},
    "log": {"path": "log de ejecución", "sha256": "hash"}
  }
}
```

DXF independent_reader añade independent_reference con engine/version y artifact
hash; debe identificar otro motor. Instalación exige method=installed_ui. Documentar
fecha, operador, datos antes/después y tolerancias en los artefactos correspondientes.

**El validador comprueba identidad, presencia, hashes y metadatos; no autentica
observaciones ni hace la auditoría por sí solo.** Leer y reproducir los artefactos
antes de registrar verified. No fabricar reportes funcionales desde tests unitarios.
Sus tests usan datos sintéticos exclusivamente para comprobar el controlador.

## Revisión de las skills existentes

Las seis skills conservan sus funciones: reverse-engineering prepara contratos;
command-cloner implementa equivalentes; UI verifica flujos; AutoLISP verifica
rutinas/errores; interop inventaría pérdidas y contrasta motores; regression ejecuta
pruebas y registra omisiones. cad-audit-gate coordina sus evidencias y la detención.
No se requiere instalar otra skill/herramienta para este control. Antes de añadir
herramientas, revisar procedencia, código, instrucciones, permisos y dependencias.
