#define AppName "LeoMoon QuickCrypt"
#define AppExeName "LeoMoon QuickCrypt.exe"
#define AppId "LeoMoon QuickCrypt"
#define AppProgId "LeoMoon.QuickCrypt.aes"

#ifndef AppVersion
  #error AppVersion must be passed with /DAppVersion.
#endif
#ifndef StageDir
  #error StageDir must be passed with /DStageDir.
#endif
#ifndef OutputDir
  #error OutputDir must be passed with /DOutputDir.
#endif
#ifndef AppArchitecture
  #error AppArchitecture must be passed with /DAppArchitecture.
#endif

[Setup]
AppId={#AppId}
AppName={#AppName}
AppVersion={#AppVersion}
VersionInfoVersion={#AppVersion}
AppPublisher=LeoMoon Studios
DefaultDirName={localappdata}\Programs\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
OutputDir={#OutputDir}
OutputBaseFilename=leomoon-quickcrypt-{#AppVersion}-windows-{#AppArchitecture}-setup
ArchitecturesAllowed={#AppArchitecture}
ArchitecturesInstallIn64BitMode={#AppArchitecture}
PrivilegesRequired=lowest
CloseApplications=yes
CloseApplicationsFilter={#AppExeName}
RestartApplications=no
ChangesAssociations=yes
Compression=lzma2/ultra64
SolidCompression=yes
UninstallDisplayIcon={app}\{#AppExeName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "{#StageDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Registry]
Root: HKCU; Subkey: "Software\Classes\.aes"; ValueType: string; ValueName: ""; ValueData: "{#AppProgId}"; Flags: uninsdeletevalue uninsdeletekeyifempty
Root: HKCU; Subkey: "Software\Classes\{#AppProgId}"; ValueType: string; ValueName: ""; ValueData: "AES Crypt File"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\{#AppProgId}\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#AppExeName},0"
Root: HKCU; Subkey: "Software\Classes\{#AppProgId}\shell\open"; ValueType: string; ValueName: ""; ValueData: "Decrypt with LeoMoon QuickCrypt"
Root: HKCU; Subkey: "Software\Classes\{#AppProgId}\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#AppExeName}"" -d ""%1"""
Root: HKCU; Subkey: "Software\Classes\*\shell\LeoMoonQuickCryptEncrypt"; ValueType: string; ValueName: ""; ValueData: "Encrypt with LeoMoon QuickCrypt"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\*\shell\LeoMoonQuickCryptEncrypt\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#AppExeName}"" -e ""%1"""
Root: HKCU; Subkey: "Software\Classes\{#AppProgId}\shell\LeoMoonQuickCryptDecrypt"; ValueType: string; ValueName: ""; ValueData: "Decrypt with LeoMoon QuickCrypt"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\{#AppProgId}\shell\LeoMoonQuickCryptDecrypt\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#AppExeName}"" -d ""%1"""

[Run]
Filename: "{app}\{#AppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(AppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
