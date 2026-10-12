# Distribución Windows A1 — validación sin simular entorno limpio

El paquete nativo reutiliza `build/native/opencad-qcad-engine.exe` del PR #21 y sus
dependencias. No recompila QCAD ni amplía comandos. PyInstaller incorpora la UI,
runtime Python, DLLs nativas resueltas mediante tablas PE, Qt6 SDK separado y
qoffscreen para el hijo QCAD. En modo nativo no hay fallback al motor temporal.
Qt plugin paths se fijan sólo para el hijo para no heredar plugins del padre PySide.

`packaging/opencad-native.spec` y `packaging/windows/opencad-native.iss` conservan
las recetas del prototipo. Inno Setup6.7.3 se obtiene de la revisión oficial, con
SHA256 publicado por GitHub y Authenticode válido Pyrsys B.V. antes de ejecutarse.
El compilador se prepara en caché, sin asociaciones, privilegios elevados ni cambios
de protección. No hay pago obligatorio ni compra. Licencia revisada del tag exacto:
https://github.com/jrsoftware/issrc/blob/is-6_7_3/license.txt

Instalación por usuario; sin asociaciones de DXF, servicios o red. Desinstalación
conserva dibujos/respaldos. Incluye avisos, SBOM Qt, fuentes QCAD con modificaciones
y snapshot de OPEN CAD. Revisión íntegra de fuentes correspondientes/licencias de
todo el binario pendiente antes de redistribución pública. La CI publica evidencias,
no el instalador ni una release. Binarios experimentales locales sin firma.

## Compilar reutilizando el motor existente

Usar Python3.12 con dependencias del proyecto, PyInstaller6.16.0 y pefile2023.2.7.
`--crt` apunta al directorio x64 Microsoft.VC*.CRT del toolchain que hizo el build;
no usar DLLs de procedencia desconocida. Elegir staging que todavía no exista.

```powershell
python tools/package_qcad_windows.py --crt 'RUTA/VC/Redist/MSVC/VERSION/x64/Microsoft.VC145.CRT' --output build/windows-package
$compiler=./tools/prepare_inno.ps1
& $compiler ('/DPackageDir='+$PWD+'/build/windows-package/dist/OPEN-CAD-2D-Native') ('/DOutputPath='+$PWD+'/build/windows-package/installer') packaging/windows/opencad-native.iss
./tools/verify_windows_install.ps1 -Installer ./build/windows-package/installer/OPEN-CAD-2D-QCAD-A1-Setup.exe -Output ($PWD.Path+'/build/installed-evidence')
```

El verificador instala en su carpeta de salida, ejecuta los nueve helpers funcionales
existentes desde el ejecutable congelado, guarda reportes/capturas/DXF y desinstala.
PATH limitado a System32 y PYTHONPATH vacío sólo para el proceso de prueba; no modifica
el sistema. El flag IndependentEnvironment no acredita limpieza. Los reports antiguos
mantienen sus etiquetas conservadoras; el reporte exterior identifica ejecución del
paquete instalado. Un fallo deja la instalación y sus logs para diagnóstico.

## Bloqueo real y procedimiento que falta

El host de desarrollo Windows11 tiene Python/MSVC/SDK Qt. No hay WindowsSandbox.exe,
cmdlets Get-VM/Get-VMHost ni otro host Windows conectado. Restringir PATH o utilizar
un runner hospedado con herramientas preinstaladas no equivale a Windows limpio.
Hace falta acceso a una VM/equipo Windows10/11 nuevo, independiente del desarrollo,
o un runner dedicado restaurado desde una imagen limpia identificada. No habilitar
virtualización ni cambiar aislamiento/protecciones para sustituir este acceso.

1. Registrar proveedor de imagen, versión/build de Windows, identidad de máquina,
   usuario sin admin y log de provisionamiento; confirmar ausencia de Python, Qt,
   QCAD, SDKs y OPEN CAD. No montar el checkout/.cache ni SDKs del desarrollador.
2. Copiar sólo instalador verificado, verify_windows_install.ps1, LSP propio y
   corpus DXF autorizado, anotando hashes. Verificar identidad commit/source snapshot
   y hash del instalador/ejecutable/motor; un build dirty no será candidata A1.
3. Ejecutar el verificador anterior con salida nueva; conservar install.log,
   installation.json, nueve reportes/capturas y archivos DXF resultantes.
4. Reinstalar y abrir normalmente OPEN-CAD-2D.exe. Observar en escritorio real:
   Ribbon/consola, capas/propiedades, selección/cancelación, LINE/CIRCLE/ARC/PLINE,
   MOVE/COPY/ROTATE/SCALE/ERASE/TRIM/EXTEND/OFFSET y las tres cotas, undo/redo y Z.
5. Cargar examples/plan_a1.lsp y ejecutar PLANO_A1; verificar edición en el mismo
   documento, error/rollback y límites. Abrir/editar/guardar/reiniciar/reabrir DXF,
   cotejar entidades/geometría/atributos/cotas con el lector independiente ezdxf.
6. Interrumpir únicamente el hijo QCAD de esa instancia, restaurar el respaldo desde
   Ribbon y guardar una copia. Comprobar original intacto y reinicio explícito LSP/undo.
7. Registrar observaciones/capturas, medidas y hashes por cada caso de AUDIT_GATE.md;
   desinstalar y verificar dibujos/respaldos intactos. Evaluar DPI/foco/rutas Unicode.

Hasta recibir/reproducir estas pruebas: criterios parciales, sin freeze ni auditoría
de entrada completa. No atribuir limpieza a las comprobaciones locales o a un flag.
