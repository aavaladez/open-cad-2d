# Recuperación del documento confirmado — desarrollo A1

QCAD C++ sigue siendo autoritativo. Cada respuesta declara `transaction_active`;
Python conserva la última respuesta confirmada separada del staging. Una caída
del hijo oculta cambios sin commit. Un commit sin respuesta no se presume exitoso.

La UI genera un DXF privado después de 1,5 segundos sin cambios y al cerrar.
RecoveryStore reutiliza el writer conservador, compara inventario y gráficos
dimensionales, publica el manifest JSON atómicamente después del DXF y su SHA-256.
Retiene dos generaciones por instancia/sesión y sólo elimina sus propios archivos
con rutas comprobadas. Conserva sesiones anteriores para recuperación manual;
falta política de caducidad entre sesiones. Nunca elimina originales/desconocidos.

Windows: `%LOCALAPPDATA%/OPEN-CAD-2D/recovery`. `OPENCAD_RECOVERY_DIR` permite pruebas
privadas; los helpers usan build/. Los respaldos contienen datos sin cifrado y
heredan permisos del directorio del usuario. No se ejecuta contenido del manifest.

Ribbon → Archivo y extensiones → Restaurar respaldo: con hijo fallido se preserva
la copia confirmada en memoria; con proceso vivo se elige manifest propio. Se pide
confirmación para sustituir el dibujo y reiniciar undo/redo, selección y estado LSP.
Cancelar conserva el dibujo. Se validan raíz, tamaño, formato, pin, UUID, hash e
inventario. Sólo se promueve un candidato QCAD después del contraste independiente.
La ruta original es informativa y no se escribe/abre automáticamente. El recuperado
queda sin destino de guardado; debe guardarse una copia explícita.

## Reproducción

```powershell
python tools/check_qcad_recovery.py --binary build/native/opencad-qcad-engine.exe --source .cache/upstream/qcad --qt .cache/qt/6.10.3/msvc2022_64 --output build/native/recovery-acceptance
python -m unittest discover -s tests -v
.cache/python/cmake/data/bin/ctest.exe --test-dir build/native --output-on-failure
```

2026-10-12 Windows, Python3.12/3.14, Qt6.10.3: 21 comprobaciones funcionales por
runtime, 58 tests por runtime (cinco nuevos límites de almacenamiento), CTest12/12.
El helper termina sólo su hijo QCAD durante staging y desde UI, restaura y
edita/guarda/reabre; original intacto, hash/path inválidos rechazados. Captura
offscreen inspeccionada. Evidencias: docs/evidence/qcad-recovery*.

No implementa RECOVER de reparación general del Excel ni aumenta cobertura. No
restaura historial/LSP ni datos fuera del subconjunto DXF. Una caída del proceso
principal puede perder los últimos1,5segundos; no acredita corte eléctrico, disco
averiado ni Windows instalado limpio. A1 permanece parcial.
