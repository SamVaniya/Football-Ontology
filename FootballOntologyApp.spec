# -*- mode: python ; coding: utf-8 -*-

import os
import owlready2
from PyInstaller.utils.hooks import collect_data_files

# Locate the path to the pellet directory
pellet_dir = os.path.join(os.path.dirname(owlready2.__file__), "pellet")

a = Analysis(
    ['OntologyGUI10.py'],
    pathex=[],
    binaries=[],
    datas=collect_data_files('owlready2', includes=['pellet/*']),
    hiddenimports=[
        'tkinter',
        'rdflib',
        'owlready2',
        'tkinter.font',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.scrolledtext',
        'tkinter.ttk',
        'io',
        'sys',
    ],
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
    [],
    name='OntologyGUI10',
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
)

