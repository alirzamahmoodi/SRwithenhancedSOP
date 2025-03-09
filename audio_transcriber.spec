# audio_transcriber.spec
# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from PyInstaller.utils.hooks import collect_submodules

# Optionally collect hidden imports if needed
hidden_imports = collect_submodules('oracledb') + ['win32']

block_cipher = None

datas = [
    ('config.yaml', '.'),  # include config.yaml in the root of the bundle
    ('icon.ico', '.')      # include icon.ico in the root of the bundle
]

a = Analysis(
    ['service.py'],  # note: now using service.py as the entry point
    pathex=['d:\\SRwithenhancedSOP'],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='audio_transcriber',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # set to False so no console window appears
    icon='icon.ico'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='audio_transcriber'
)