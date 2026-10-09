---
name: cad-audit-gate
description: Gestionar la primera auditoría integral de OPEN CAD, comprobar sus seis criterios funcionales, recopilar evidencias, congelar candidata y detener funciones hasta aprobación del director.
---

# cad-audit-gate

Leer AGENTS.md y docs/AUDIT_GATE.md. La decisión del director del 2026-10-09
prevalece sobre continuidad automática. Mantener arquitectura, avances y catálogo
Excel; no esperar a completar 472 entradas.

## Procedimiento

1. Revisar las seis entradas de requirements/audit-gate.json. Identificar candidata
   por commit y hash del binario Windows. Un core geométrico, tests internos, un
   portable o código presente no acreditan los requisitos funcionales.
2. Reutilizar las seis skills CAD: contratos y trazabilidad; comandos/transacciones;
   UI; AutoLISP; DXF con segundo motor; regresión. Ejecutar flujos de aplicación
   QCAD documentales, Ribbon/capas/propiedades/consola, comandos con selección y
   cotas, carga LSP/DEFUN C:, ciclo DXF e instalación Windows.
3. Conservar fixtures y logs, observaciones antes/después, hashes y versiones.
   Leer/reproducir artefactos antes de marcar verified. El helper sólo comprueba
   estructura, identidad y hashes; no puede autenticar una observación o aprobarla.
4. Evaluar con helper y salida nueva. Si faltan criterios, registrar brechas y
   continuar el roadmap autónomamente, sin pedir aprobación rutinaria.
5. Al comprobar 6/6, DETENER funciones nuevas y congelar candidata (--freeze).
   Mantener el registro persistente incluso si una regresión invalida un criterio.
   Sólo auditoría/correcciones; registrar nuevas candidatas y repetir casos afectados.
6. Ejecutar regresión/compatibilidad y auditar las once áreas de AUDIT_GATE.md.
   Crear informe integral con evidencias, mediciones, corpus y omisiones. Registrar
   defectos P0-P3, reproducibilidad, Issues, responsables y acciones correctivas.
7. Resolver bloqueantes, repetir aceptación, PAUSAR y presentar informe al usuario.
   La siguiente fase exige ausencia de bloqueantes Y aprobación explícita del
   director. Nunca inferir aprobación de JSON, tests, PR, documentación o agentes.

## Automatización

Desde raíz, usando rutas de salida que no existan:

```powershell
python .agents/skills/cad-audit-gate/scripts/gate.py --report build/a1/run.json --markdown build/a1/run.md
python -m unittest discover -s tests -p test_audit_gate.py -v
```

Salidas 0/1/2: entrada estructural 6/6 / entrada pendiente / error. Ninguna autoriza
fase nueva. Sólo tras revisión funcional 6/6, --freeze registra candidata sin
sobrescribir. El informe de entrada no sustituye la auditoría integral.

Aceptación: seis demostraciones de aplicación de la misma candidata; segundo motor
DXF identificado e instalación real; ausencia de aprobación automática; congelación
persistente; informe integral y bloqueantes resueltos antes de decisión humana.
No instalar herramientas desconocidas sin examinar código, instrucciones, permisos
y dependencias. Los tests del controlador usan artefactos sintéticos, sin declarar
que OPEN CAD satisfaga A1. Documentar estado real en STATUS y AUDIT_GATE.
