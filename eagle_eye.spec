# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

from PyInstaller.building.api import COLLECT, EXE, PYZ
from PyInstaller.building.build_main import Analysis

# bulk auto add all data files in the src/gui/resources directory
data_files = []
project_path = Path(SPECPATH)
resources_path = project_path / 'src' / 'gui' / 'resources'
assert resources_path.exists(), f'{resources_path} does not exist'

for root, dirs, files in resources_path.walk(on_error=print):
    truncated_root = root.relative_to(project_path)
    for file in files:
        data_files.append(
            (str(truncated_root / file), str(truncated_root))
        )

a = Analysis(
    ['eagle_eye.py'],
    pathex=[],
    binaries=[],
    datas=data_files,
    hiddenimports=[],
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
    name='eagle_eye',
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
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='eagle_eye',
)
