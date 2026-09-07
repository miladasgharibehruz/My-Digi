$ErrorActionPreference = 'Stop'
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if (Test-Path build) { Remove-Item build -Recurse -Force }
if (Test-Path dist) { Remove-Item dist -Recurse -Force }
if (Test-Path installer) { Remove-Item installer -Recurse -Force }
python -m PyInstaller --noconfirm --clean MyDigi.spec
python -m PyInstaller --noconfirm --clean MyDigiUpdater.spec
& "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe" MyDigi.iss
Write-Host "Installer: installer\My Digi.exe"
