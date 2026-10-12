param([string]$Destination='.cache/inno-reviewed/compiler')
$ErrorActionPreference='Stop'
$cadExpected='9C73C3BAE7ED48D44112A0F48E66742C00090BDB5BEF71D9D3C056C66E97B732'
$cadTarget=[IO.Path]::GetFullPath($Destination)
$cadParent=Split-Path $cadTarget -Parent
New-Item -ItemType Directory -Force -Path $cadParent | Out-Null
$cadDownload=Join-Path $cadParent 'innosetup-6.7.3.exe'
if (-not (Test-Path -LiteralPath $cadDownload)) {
    Invoke-WebRequest -Uri 'https://github.com/jrsoftware/issrc/releases/download/is-6_7_3/innosetup-6.7.3.exe' -OutFile $cadDownload
}
if ((Get-FileHash -LiteralPath $cadDownload).Hash -ne $cadExpected) {throw 'Inno SHA256 mismatch'}
$cadSignature=Get-AuthenticodeSignature -LiteralPath $cadDownload
if ($cadSignature.Status -ne 'Valid' -or $cadSignature.SignerCertificate.Subject -notmatch 'O=Pyrsys B.V.') {throw 'Inno publisher signature mismatch'}
if (-not (Test-Path -LiteralPath (Join-Path $cadTarget 'ISCC.exe'))) {
    $cadProcess=Start-Process -FilePath $cadDownload -ArgumentList @('/VERYSILENT','/CURRENTUSER','/SP-','/NORESTART','/NOICONS',('/DIR="'+$cadTarget+'"'),'/MERGETASKS=!fileassoc') -WindowStyle Hidden -Wait -PassThru
    if ($cadProcess.ExitCode -ne 0) {throw 'Inno compiler preparation failed'}
}
Write-Output (Join-Path $cadTarget 'ISCC.exe')
