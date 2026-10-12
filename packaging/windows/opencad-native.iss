#ifndef PackageDir
  #error PackageDir is required
#endif
#ifndef OutputPath
  #error OutputPath is required
#endif
[Setup]
AppId=OPEN-CAD-2D-QCAD-A1
AppName=OPEN CAD 2D QCAD A1 Experimental
AppVersion=0.1.0
DefaultDirName={localappdata}\OPEN-CAD-2D-QCAD-A1
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir={#OutputPath}
OutputBaseFilename=OPEN-CAD-2D-QCAD-A1-Setup
LicenseFile=..\..\LICENSE
UninstallDisplayIcon={app}\OPEN-CAD-2D.exe
Compression=lzma2
SolidCompression=yes
DisableProgramGroupPage=yes
[Files]
Source: "{#PackageDir}\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs
[Icons]
Name: "{userprograms}\OPEN CAD 2D QCAD A1"; Filename: "{app}\OPEN-CAD-2D.exe"
; No associations, administrator privileges, network installs or user-data deletion.
