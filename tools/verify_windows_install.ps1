param([Parameter(Mandatory)][string]$Installer,[Parameter(Mandatory)][string]$Output,
      [switch]$IndependentEnvironment)
$ErrorActionPreference='Stop'
$cadOutput=[IO.Path]::GetFullPath($Output)
if (Test-Path -LiteralPath $cadOutput) {throw 'Choose a new output directory; do not overwrite evidence'}
New-Item -ItemType Directory -Path $cadOutput | Out-Null
$cadInstaller=(Resolve-Path -LiteralPath $Installer).Path
$cadInstall=Join-Path $cadOutput 'installed'
$cadArgs=@('/VERYSILENT','/SP-','/SUPPRESSMSGBOXES','/NORESTART',('/DIR="'+$cadInstall+'"'),('/LOG="'+(Join-Path $cadOutput 'install.log')+'"'))
$cadSetup=Start-Process -FilePath $cadInstaller -ArgumentList $cadArgs -WindowStyle Hidden -Wait -PassThru
if ($cadSetup.ExitCode -ne 0) {throw "Install exit code $($cadSetup.ExitCode)"}
$cadExe=Join-Path $cadInstall 'OPEN-CAD-2D.exe'
if (-not (Test-Path -LiteralPath $cadExe)) {throw 'Installed application absent'}
# Process-local restriction detects missing bundled dependencies. It does not
# turn a development host or a hosted image with tools into clean Windows.
$cadOldPath=$env:PATH; $cadOldPython=$env:PYTHONPATH; $cadOldQt=$env:QT_PLUGIN_PATH
try {
    $env:PATH=Join-Path $env:WINDIR 'System32'; $env:PYTHONPATH=''; $env:QT_PLUGIN_PATH=''
    $env:QT_QPA_PLATFORM='offscreen'
    $cadTests=Join-Path $cadOutput 'functional'
    $cadApp=Start-Process -FilePath $cadExe -ArgumentList @('--acceptance-check',('"'+$cadTests+'"')) -WorkingDirectory $cadOutput -WindowStyle Hidden -Wait -PassThru
    if ($cadApp.ExitCode -ne 0) {throw "Installed functional check exit code $($cadApp.ExitCode); inspect startup-error.log"}
    $cadReport=Get-Content -Raw -LiteralPath (Join-Path $cadTests 'packaged-report.json') | ConvertFrom-Json
    if (-not $cadReport.passed) {throw 'Installed regression did not pass'}
} finally {$env:PATH=$cadOldPath; $env:PYTHONPATH=$cadOldPython; $env:QT_PLUGIN_PATH=$cadOldQt}
$cadUninstall=Join-Path $cadInstall 'unins000.exe'
$cadApplicationHash=(Get-FileHash -LiteralPath $cadExe).Hash
$cadBuildIdentity=Get-Content -Raw -LiteralPath (Join-Path $cadInstall '_internal/build-identity.json') | ConvertFrom-Json
$cadUserDrawing=Join-Path $cadTests 'recovery/original.dxf'
$cadUserHash=(Get-FileHash -LiteralPath $cadUserDrawing).Hash
$cadRemoval=Start-Process -FilePath $cadUninstall -ArgumentList @('/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART') -WindowStyle Hidden -Wait -PassThru
if ($cadRemoval.ExitCode -ne 0 -or (Test-Path -LiteralPath $cadExe)) {throw 'Uninstall failed'}
if ((Get-FileHash -LiteralPath $cadUserDrawing).Hash -ne $cadUserHash) {throw 'Uninstall changed user drawing outside installation'}
$cadRecord=@{kind='installed_functional_regression';platform=[Environment]::OSVersion.VersionString;
    installer_sha256=(Get-FileHash -LiteralPath $cadInstaller).Hash;install_exit_code=$cadSetup.ExitCode;
    application_exit_code=$cadApp.ExitCode;uninstall_exit_code=$cadRemoval.ExitCode;
    application_sha256=$cadApplicationHash;build_identity=$cadBuildIdentity;user_drawing_preserved=$true;
    clean_environment_verified=$false;independent_environment_requested=[bool]$IndependentEnvironment;
    method='offscreen fixtures and deterministic dialogs';path_restricted_to_system32=$true;
    limitation='Flag does not verify clean environment. Attach VM/image identity, provision log and independent desktop observation.'}
$cadRecord | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $cadOutput 'installation.json') -Encoding utf8
