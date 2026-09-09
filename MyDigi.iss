#define MyDigiVersion "2.0.9"
[Setup]
AppId={{B6D2E5D1-8E44-4D73-9A52-6F1F0F5E20A1}
AppName=My Digi
AppVersion={#MyDigiVersion}
VersionInfoVersion={#MyDigiVersion}.0
VersionInfoDescription=My Digi - مدیریت هوشمند فروش در دیجی‌کالا
VersionInfoProductName=My Digi
VersionInfoProductVersion={#MyDigiVersion}.0
AppPublisher=My Digi
DefaultDirName={autopf}\My Digi
DefaultGroupName=My Digi
OutputDir=installer
OutputBaseFilename=My-Digi-Setup
SetupIconFile=My Digi.ico
UninstallDisplayIcon={app}\My Digi.exe
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=admin
RestartApplications=no
DisableProgramGroupPage=yes
[Tasks]
Name: "desktopicon"; Description: "ایجاد میانبر My Digi روی دسکتاپ"; GroupDescription: "میانبرها:"
[Files]
Source: "dist\My Digi.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\My Digi Updater\My Digi Updater.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "update_config.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "My Digi.ico"; DestDir: "{app}"; Flags: ignoreversion
[Icons]
Name: "{group}\My Digi"; Filename: "{app}\My Digi.exe"; IconFilename: "{app}\My Digi.ico"; AppUserModelID: "Mabouth.MyDigi"
Name: "{autodesktop}\My Digi"; Filename: "{app}\My Digi.exe"; IconFilename: "{app}\My Digi.ico"; AppUserModelID: "Mabouth.MyDigi"; Tasks: desktopicon
[Run]
Filename: "{app}\My Digi.exe"; Description: "اجرای My Digi"; Flags: nowait postinstall skipifsilent
[UninstallDelete]
Type: filesandordirs; Name: "{app}"
