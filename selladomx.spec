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

# Hidden imports that PyInstaller might miss
hidden_imports = [
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    'pyhanko',
    'pyhanko.pdf_utils',
    'pyhanko.sign',
    'pyhanko.sign.signers',
    'pyhanko.sign.fields',
    'pyhanko.sign.timestamps',
    'pyhanko.sign.validation',
    'pyhanko_certvalidator',
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
    datas=pyhanko_datas + pyhanko_certvalidator_datas,
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
    name='SelladoMX',
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
    icon='assets/icon.ico' if sys.platform == 'win32' else 'assets/icon.icns' if sys.platform == 'darwin' else 'assets/icon-linux.png',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SelladoMX',
)

# macOS app bundle
if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='SelladoMX.app',
        icon='assets/icon.icns',
        bundle_identifier='mx.sellado.client',
        info_plist={
            'NSPrincipalClass': 'NSApplication',
            'NSHighResolutionCapable': 'True',
            'CFBundleName': 'SelladoMX',
            'CFBundleDisplayName': 'SelladoMX',
            'CFBundleVersion': '0.1.0',
            'CFBundleShortVersionString': '0.1.0',
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
