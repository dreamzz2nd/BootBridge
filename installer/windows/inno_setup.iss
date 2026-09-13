; BootBridge Inno Setup Script
; Compiles a professional native Windows .exe Setup Wizard installer
; Output: dist/BootBridge-v1.0.0-Windows-Setup.exe

#define MyAppName "BootBridge"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "dreamzz2nd"
#define MyAppURL "https://github.com/dreamzz2nd/BootBridge"
#define MyAppExeName "bootbridge.bat"

[Setup]
; Basic Application Identity
AppId={{D6E570A2-9981-4FE8-9A25-F7B6B92C44B1}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
LicenseFile=..\..\LICENSE
; Visuals & Output
OutputDir=..\..\dist
OutputBaseFilename=BootBridge-v{#MyAppVersion}-Windows-Setup
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayIcon={app}\assets\bootbridge.png

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Copy all application root files
Source: "..\..\bootbridge.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\setup_wizard.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\gui_installer.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\bootbridge_installer.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\README.id.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\LICENSE"; DestDir: "{app}"; Flags: ignoreversion

; Copy subdirectories
Source: "..\..\core\*"; DestDir: "{app}\core"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\..\ui\*"; DestDir: "{app}\ui"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\..\assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\..\desktop\*"; DestDir: "{app}\desktop"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\bootbridge.bat"; IconFilename: "{app}\assets\bootbridge.png"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\bootbridge.bat"; IconFilename: "{app}\assets\bootbridge.png"; Tasks: desktopicon

[Run]
Filename: "{app}\bootbridge.bat"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: shellexec postinstall nowait skipifsilent
