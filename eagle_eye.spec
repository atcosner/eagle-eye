# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

from PyInstaller.building.api import COLLECT, EXE, PYZ
from PyInstaller.building.build_main import Analysis

PROJECT_PATH = Path(SPECPATH)
DATA_FILES: list[tuple[str, str]] = []


def add_files(
        top_level_path: Path,
        directory: Path,
        excluded_extensions: list[str] | None = None,
) -> list[tuple[str, str]]:
    data_files = []
    for root, dirs, files in directory.walk(on_error=print):
        truncated_root = root.relative_to(top_level_path)
        for file in files:
            # check for an excluded extension
            if excluded_extensions is not None:
                if Path(file).suffix in excluded_extensions:
                    continue

            data_files.append(
                (str(truncated_root / file), str(truncated_root))
            )

    return data_files


# bulk auto add all data files in the src/gui/resources directory
resources_path = PROJECT_PATH / 'src' / 'gui' / 'resources'
assert resources_path.exists(), f'{resources_path} does not exist'
DATA_FILES.extend(add_files(PROJECT_PATH, resources_path))


# add files (that are not .py) in the examples directory
examples_path = PROJECT_PATH / 'src' / 'examples'
assert examples_path.exists(), f'{examples_path} does not exist'
DATA_FILES.extend(add_files(PROJECT_PATH, examples_path, excluded_extensions=['.py', '.pyc']))


a = Analysis(
    ['eagle_eye.py'],
    pathex=[],
    binaries=[],
    datas=DATA_FILES,
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
    a.binaries,
    a.datas,
    name='Eagle Eye',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=[str(resources_path / 'eagle_eye.ico')],
)
