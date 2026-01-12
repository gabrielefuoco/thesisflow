# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('C:\\Users\\gabri\\AppData\\Local\\Programs\\Python\\Python311\\Lib\\site-packages\\customtkinter', 'customtkinter/'), ('C:\\Users\\gabri\\APP\\thesisflow\\bin', 'bin/'), ('C:\\Users\\gabri\\APP\\thesisflow\\templates', 'templates/'), ('C:\\Users\\gabri\\APP\\thesisflow\\assets', 'assets/'), ('C:\\Users\\gabri\\AppData\\Local\\Programs\\Python\\Python311\\tcl\\tcl8.6', 'tcl/'), ('C:\\Users\\gabri\\AppData\\Local\\Programs\\Python\\Python311\\tcl\\tk8.6', 'tk/')]
binaries = []
hiddenimports = []
tmp_ret = collect_all('src')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['C:\\Users\\gabri\\APP\\thesisflow\\run.py'],
    pathex=['C:\\Users\\gabri\\APP\\thesisflow'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ThesisFlow',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ThesisFlow',
)
