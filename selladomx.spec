# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for SelladoMX
Configures packaging for macOS, Windows, and Linux
"""

import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect all pyhanko data files
pyhanko_datas = collect_data_files('pyhanko')
pyhanko_certvalidator_datas = collect_data_files('pyhanko_certvalidator')

# Collect QML files (for QML UI mode)
from pathlib import Path
qml_src = Path('src/selladomx/ui/qml')
qml_datas = []
if qml_src.exists():
    # Collect all QML files recursively
    for qml_file in qml_src.rglob('*.qml'):
        rel_path = qml_file.relative_to('src/selladomx/ui/qml')
        dest_dir = f'selladomx/ui/qml/{rel_path.parent}'
        qml_datas.append((str(qml_file), dest_dir))

    # Also collect qmldir files
    for qmldir_file in qml_src.rglob('qmldir'):
        rel_path = qmldir_file.relative_to('src/selladomx/ui/qml')
        dest_dir = f'selladomx/ui/qml/{rel_path.parent}'
        qml_datas.append((str(qmldir_file), dest_dir))

# Hidden imports that PyInstaller might miss
hidden_imports = [
    # Qt Core
    'PySide6.QtCore',
    'PySide6.QtGui',

    # Qt Quick/QML
    'PySide6.QtQml',
    'PySide6.QtQuick',
    'PySide6.QtQuickControls2',
    'PySide6.QtQuickLayouts',
    'PySide6.QtQuickTemplates2',

    # PDF signing
    'pyhanko',
    'pyhanko.pdf_utils',
    'pyhanko.sign',
    'pyhanko.sign.signers',
    'pyhanko.sign.fields',
    'pyhanko.sign.timestamps',
    'pyhanko.sign.validation',
    'pyhanko_certvalidator',

    # Other dependencies
    'cryptography',
    'requests',
    'qrcode',
    'PIL',
]

# Additional submodules
hidden_imports += collect_submodules('pyhanko')
hidden_imports += collect_submodules('pyhanko_certvalidator')

a = Analysis(
    ['run.py'],
    pathex=['src'],  # Add src to path so selladomx can be imported
    binaries=[],
    datas=pyhanko_datas + pyhanko_certvalidator_datas + qml_datas + [
        ('assets/selladomx.png', 'assets'),
    ],
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'IPython',
        'jupyter',
    ],
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
    name='selladomx',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window for GUI app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/selladomx.ico' if sys.platform == 'win32' else 'assets/selladomx.icns' if sys.platform == 'darwin' else 'assets/selladomx.png',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='selladomx',
)

# macOS app bundle
if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='SelladoMX.app',
        icon='assets/selladomx.icns',
        bundle_identifier='mx.sellado.client',
        info_plist={
            'NSPrincipalClass': 'NSApplication',
            'NSHighResolutionCapable': 'True',
            'CFBundleName': 'SelladoMX',
            'CFBundleDisplayName': 'SelladoMX',
            'CFBundleVersion': '0.2.0',
            'CFBundleShortVersionString': '0.2.0',
            'LSMinimumSystemVersion': '10.13',
            'NSRequiresAquaSystemAppearance': 'False',
            # URL scheme handler for magic links
            'CFBundleURLTypes': [
                {
                    'CFBundleURLName': 'mx.sellado.client',
                    'CFBundleURLSchemes': ['selladomx'],
                }
            ],
        },
    )
