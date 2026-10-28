; Inno Setup script for the Windows installer. Compile from the repo root after
; the PyInstaller build:
;   ISCC.exe /DAppVersion=X.Y.Z installer\selladomx.iss
; Relative paths are resolved from this file's directory.
; Saved as UTF-8 with BOM so ISCC reads the Spanish strings correctly.

#ifndef AppVersion
  #error Pass the version with /DAppVersion=X.Y.Z
#endif

#define AppName "SelladoMX"
#define AppExeName "selladomx.exe"

[Setup]
; Never change AppId: upgrades and uninstall find the existing install by it,
; and platform_helpers.py reads the uninstall key derived from it.
AppId={{4285FAC5-53B6-436F-89B4-A58266D49505}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher=SelladoMX
AppPublisherURL=https://www.selladomx.com
AppSupportURL=https://www.selladomx.com
AppUpdatesURL=https://www.selladomx.com/#descarga
VersionInfoVersion={#AppVersion}
VersionInfoProductName={#AppName}
VersionInfoDescription=Instalador de {#AppName}
PrivilegesRequired=lowest
DefaultDirName={autopf}\{#AppName}
DisableProgramGroupPage=yes
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
WizardStyle=modern
SetupIconFile=..\assets\selladomx.ico
UninstallDisplayIcon={app}\{#AppExeName}
UninstallDisplayName={#AppName}
OutputDir=..\dist
OutputBaseFilename=SelladoMX-Windows-Setup
Compression=lzma2/max
SolidCompression=yes
; selladomx.exe holds this mutex while it runs (platform_helpers.py).
AppMutex=SelladoMXAppMutex
CloseApplications=yes
RestartApplications=no

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[CustomMessages]
spanish.RemoveUserData=¿Eliminar también tu configuración y token?%n%nSi eliges "No", se conservan para cuando vuelvas a instalar SelladoMX. Tus PDFs y tus archivos .cer y .key no se borran en ningún caso.

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[InstallDelete]
; Stale DLLs and Qt plugins from an older build must not be loaded by the new one.
Type: filesandordirs; Name: "{app}\_internal"

[Files]
Source: "..\dist\selladomx\*"; DestDir: "{app}"; Excludes: "README.txt"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Registry]
Root: HKCU; Subkey: "Software\Classes\selladomx"; ValueType: string; ValueName: ""; ValueData: "URL:SelladoMX Protocol"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\selladomx"; ValueType: string; ValueName: "URL Protocol"; ValueData: ""
Root: HKCU; Subkey: "Software\Classes\selladomx\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#AppExeName},0"
Root: HKCU; Subkey: "Software\Classes\selladomx\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#AppExeName}"" ""%1"""

[Run]
Filename: "{app}\{#AppExeName}"; Description: "{cm:LaunchProgram,{#AppName}}"; Flags: nowait postinstall skipifsilent

[Code]
var
  RemoveUserData: Boolean;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  LocalData: String;
begin
  { With /SUPPRESSMSGBOXES the prompt is skipped and the settings are kept. }
  if CurUninstallStep = usUninstall then
    RemoveUserData := SuppressibleMsgBox(CustomMessage('RemoveUserData'),
      mbConfirmation, MB_YESNO or MB_DEFBUTTON2, IDNO) = IDYES;

  if CurUninstallStep = usPostUninstall then
  begin
    { QSettings("SelladoMX", "SelladoMX") keeps the settings and the API token
      in HKCU\Software\SelladoMX\SelladoMX. }
    if RemoveUserData then
      RegDeleteKeyIncludingSubkeys(HKCU, 'Software\SelladoMX');

    { Logs and Qt's regenerable QML cache. RemoveDir only removes empty folders. }
    LocalData := ExpandConstant('{localappdata}\SelladoMX');
    DelTree(LocalData + '\logs', True, True, True);
    DelTree(LocalData + '\SelladoMX\cache', True, True, True);
    RemoveDir(LocalData + '\SelladoMX');
    RemoveDir(LocalData);
  end;
end;
