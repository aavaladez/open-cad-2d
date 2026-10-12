# Propiedades y selección QCAD — 2026-10-12

CadSession conserva el documento autoritativo. La UI no recalcula ni sustituye la
geometría para confirmar ediciones. QcadCommandBus.edit_properties usa el staging
transaccional existente; un lote completo se valida antes de sustituir sus clones.

LINE: extremos XYZ. CIRCLE: centro XYZ y radio positivo. Capa común de una selección
mixta. Bloqueos de origen/destino, ID inexistente, propiedad incompatible, valores
no finitos y geometría degenerada rechazan la edición. Undo/redo sincroniza formulario
y dibujo. Esc no confirma cambios de geometría pendientes; aplicar es explícito.
El formulario conserva 17 cifras significativas al representar valores para evitar
cuantizar coordenadas no editadas. Radio/color/lineweight de otras entidades pendientes.

Selección: consulta nativa de geometría QCAD proyectada en XY, sin alterar Z. Pick
individual, ventana de izquierda a derecha (contención), cruce de derecha a izquierda
(contención/intersección de la curva). Ventana dentro del círculo sin tocar su curva
no selecciona el círculo. Capas OFF/FROZEN omitidas; objetos bloqueados inspeccionables,
edición rechazada. La UI acumula selecciones, Shift retira, Ctrl alterna y Escape limpia
la selección en reposo. Estado de selección sólo en la UI; no modifica historial.

Mover selección usa punto base/destino y el mismo MOVE transaccional. Escape antes
del destino no cambia el documento. Falta selección por comandos/filtros/lazo/fence,
multidocumentos, propiedades avanzadas y otras entidades; no afirmar equivalencia total.

El fixture descubrió que CE añade Defpoints al exportar documentos nuevos. El adaptador
ahora crea esa capa estándar explícitamente al inicializar, fuera del historial de usuario,
para conservar inventario completo sin relajar el contraste DXF. Importación candidata
y writer híbrido de DXF_APPLICATION.md conservados.

## Reproducción y evidencia

```powershell
./tools/build_qcad.ps1
python tools/check_qcad_editing.py --binary build/native/opencad-qcad-engine.exe --source .cache/upstream/qcad --qt .cache/qt/6.10.3/msvc2022_64 --output build/editing
ctest --test-dir build/native --output-on-failure
```

30 comprobaciones funcionales en Windows/Python 3.12 y 3.14: selección XY/ventana/cruce,
curva frente a interior, cambios/capas/lotes, rechazos, undo/redo y rama redo tras error,
edición de propiedades con QtTest, acumulación/Shift, arrastre de ventana/cruce, MOVE
con ratón/cancelación, escritura y reapertura DXF. Archivo original creado por el helper;
sin AutoCAD ni recursos gráficos propietarios. Reportes/PNG en docs/evidence/qcad-editing*.
46 tests por runtime y CTest 6/6, incluido LSP personalizado y el ciclo DXF anteriores.
Esto es evidencia parcial de aplicación de desarrollo, no instalada ni aprobación A1.

Referencias públicas: [selección múltiple](https://help.autodesk.com/cloudhelp/2023/ENU/AutoCAD-Core/files/GUID-531FB60D-833B-4813-927A-42275CF6777D.htm),
[paleta de propiedades](https://help.autodesk.com/cloudhelp/2023/ENU/AutoCAD-Core/files/GUID-0AA644F1-1165-492F-A4D1-3EDA8598C644.htm),
[RBox](https://qcad.io/doc/qcad/latest/developer/class_r_box.html).
Estas fuentes definen expectativas; los resultados proceden de fixtures originales.
