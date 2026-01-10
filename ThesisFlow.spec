# thesisflow.spec
# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_all
import os
import customtkinter
import sys
from pathlib import Path

# 1. Raccogli dati e binari di CustomTkinter (gestisce temi e json)
datas = []
binaries = []
hiddenimports = []

# Raccogli tutto ciò che serve a CustomTkinter e src
tmp_ret = collect_all('customtkinter')
datas += tmp_ret[0]
binaries += tmp_ret[1]
hiddenimports += tmp_ret[2]

# Raccogli il tuo pacchetto src
tmp_ret_src = collect_all('src')
datas += tmp_ret_src[0]
hiddenimports += tmp_ret_src[2]

# 2. Aggiungi le tue cartelle risorse (bin, templates)
# Sintassi: (percorso_origine, percorso_destinazione)
# We need absolute paths for safety
project_root = os.getcwd()

datas += [
    (os.path.join(project_root, 'bin'), 'bin'),
    (os.path.join(project_root, 'templates'), 'templates'),
    (os.path.join(project_root, 'assets'), 'assets'),
    (os.path.join(project_root, 'locales'), 'locales'),
    (os.path.join(project_root, 'src'), 'src')  # Inclusione esplicita del codice sorgente se serve riflessione
]

block_cipher = None

a = Analysis(
    ['run.py'],  # Punto di ingresso
    pathex=[project_root],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=['hooks'],  # Usa il tuo hook esistente se serve
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

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
    console=False,  # <--- IMPORTANTE: Impostato a False per il deploy
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ThesisFlow',
)
