$ErrorActionPreference = 'Stop'
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if (Test-Path build) { Remove-Item build -Recurse -Force }
if (Test-Path dist) { Remove-Item dist -Recurse -Force }
if (Test-Path installer) { Remove-Item installer -Recurse -Force }
python -m PyInstaller --noconfirm --clean MyDigi.spec
python -m PyInstaller --noconfirm --clean MyDigiUpdater.spec
$updater = "dist\My Digi Updater.exe"
if (-not (Test-Path -LiteralPath $updater)) { throw "Updater build failed." }
New-Item -ItemType Directory -Path "dist\My Digi Updater" -Force | Out-Null
Move-Item -LiteralPath $updater -Destination "dist\My Digi Updater\My Digi Updater.exe" -Force
& "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe" MyDigi.iss
Write-Host "Installer: installer\My-Digi-Setup.exe"
