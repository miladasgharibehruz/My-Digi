# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas=[]; binaries=[]; hiddenimports=[]
for pkg in ['webview']:
    try:
        d,b,h=collect_all(pkg); datas += d; binaries += b; hiddenimports += h
    except Exception:
        pass

a = Analysis(['My_Digi(1).py'], pathex=['.'], binaries=binaries, datas=datas, hiddenimports=hiddenimports, hookspath=[], hooksconfig={}, runtime_hooks=[], excludes=[], noarchive=False)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, a.binaries, a.datas, [], name='My Digi', debug=False, bootloader_ignore_signals=False, strip=False, upx=True, console=False, icon='My Digi.ico')
