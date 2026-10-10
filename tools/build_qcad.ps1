param(
    [string]$QtPrefix = '.cache/qt/6.10.3/msvc2022_64',
    [string]$Source = '.cache/upstream/qcad',
    [switch]$ConfigureOnly
)
$ErrorActionPreference = 'Stop'
$cadRoot = Split-Path $PSScriptRoot -Parent
$cadQt = (Resolve-Path -LiteralPath (Join-Path $cadRoot $QtPrefix)).Path
$cadSource = (Resolve-Path -LiteralPath (Join-Path $cadRoot $Source)).Path
$cadCMake = Join-Path $cadRoot '.cache/python/cmake/data/bin/cmake.exe'
if (-not (Test-Path -LiteralPath $cadCMake)) { $cadCMake = (Get-Command cmake).Source }
$cadNinja = Join-Path $cadRoot '.cache/ninja-runtime/bin/ninja.exe'
if (-not (Test-Path -LiteralPath $cadNinja)) { $cadNinja = (Get-Command ninja).Source }
$cadVsWhere = Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio/Installer/vswhere.exe'
$cadVs = & $cadVsWhere -latest -products '*' -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
if (-not $cadVs) { throw 'MSVC x64 no encontrado; instalar toolchain abierto/configurado antes del spike.' }
$cadVCVars = Join-Path $cadVs 'VC/Auxiliary/Build/vcvars64.bat'
$cadBuild = Join-Path $cadRoot 'build/native'
New-Item -ItemType Directory -Force -Path $cadBuild | Out-Null
# Reject command metacharacters in paths before writing a local cmd wrapper.
foreach ($cadPath in @($cadRoot,$cadQt,$cadSource,$cadCMake,$cadNinja,$cadVCVars,$cadBuild)) {
    if ($cadPath -match '["%&|<>^!\r\n]') { throw 'Ruta no representable con seguridad en cmd.' }
}
$cadScript = Join-Path $cadBuild 'build-qcad.cmd'
$cadLines = @('@echo off', "call `"$cadVCVars`"", 'if errorlevel 1 exit /b %ERRORLEVEL%',
    "`"$cadCMake`" -S `"$cadRoot`" -B `"$cadBuild`" -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_MAKE_PROGRAM=`"$cadNinja`" -DOPENCAD_BUILD_QCAD=ON -DOPENCAD_QCAD_SOURCE=`"$cadSource`" -DCMAKE_PREFIX_PATH=`"$cadQt`"",
    'if errorlevel 1 exit /b %ERRORLEVEL%')
if (-not $ConfigureOnly) {
    $cadLines += "`"$cadCMake`" --build `"$cadBuild`" --target qcad-geometry-smoke qcad-document-smoke opencad-qcad-engine --parallel 4"
}
$cadLines += 'exit /b %ERRORLEVEL%'
Set-Content -LiteralPath $cadScript -Value $cadLines -Encoding ascii
& cmd.exe /d /c "call `"$cadScript`""
if ($LASTEXITCODE -ne 0) { throw "QCAD build/configure falló: $LASTEXITCODE" }
if (-not $ConfigureOnly) {
    & python (Join-Path $cadRoot 'tools/check_qcad_geometry.py') --binary (Join-Path $cadBuild 'qcad-geometry-smoke.exe') --source $cadSource --qt $cadQt --report (Join-Path $cadBuild 'geometry-report.json')
    if ($LASTEXITCODE -ne 0) { throw 'QCAD geometry acceptance failed.' }
    & python (Join-Path $cadRoot 'tools/check_qcad_document.py') --binary (Join-Path $cadBuild 'qcad-document-smoke.exe') --source $cadSource --qt $cadQt --output (Join-Path $cadBuild 'document-acceptance')
    if ($LASTEXITCODE -ne 0) { throw 'QCAD document/DXF acceptance failed.' }
}
