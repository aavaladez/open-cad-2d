; Installer recipe: compiler/install/uninstall are not yet verified.
[Setup]
AppId=OPEN-CAD-2D-Prototype
AppName=OPEN CAD 2D Prototype
AppVersion=0.1.0
DefaultDirName={localappdata}\OPEN-CAD-2D-Prototype
PrivilegesRequired=lowest
OutputDir=..\..\dist
OutputBaseFilename=OPEN-CAD-2D-Setup-0.1.0
LicenseFile=..\..\LICENSE
UninstallDisplayIcon={app}\OPEN-CAD-2D.exe
[Files]
Source: "..\..\dist\OPEN-CAD-2D\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs
[Icons]
Name: "{group}\OPEN CAD 2D Prototype"; Filename: "{app}\OPEN-CAD-2D.exe"
