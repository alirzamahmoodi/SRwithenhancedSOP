# audio_transcriber.spec
# -*- mode: python -*-

block_cipher = None

a = Analysis(
    ['main.py'],  # main.py is your entry script; audio_transcriber.py is imported from here
    pathex=[],    # Optionally, add your project directory here, e.g., [r'C:\path\to\project']
    binaries=[],
    # Include config.yaml as a data file so it is placed next to the executable.
    # This way you can modify it after the build.
    datas=[('config.yaml', '.')],  
    hiddenimports=[],  # If any packages are not auto-detected, list them here
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='audio_transcriber',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True  # Set to False if you want a windowed application (on Windows)
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
