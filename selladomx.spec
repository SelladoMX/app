# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for SelladoMX
Configures packaging for macOS, Windows, and Linux
"""

import ast
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None


def read_app_version():
    tree = ast.parse(open('src/selladomx/__init__.py', encoding='utf-8').read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            getattr(target, 'id', None) == '__version__' for target in node.targets
        ):
            return ast.literal_eval(node.value)
    raise SystemExit('__version__ not found in src/selladomx/__init__.py')


APP_VERSION = read_app_version()

# Version resource for the Windows exe; unsigned exes without one look more
# suspicious to antivirus heuristics.
windows_version_info = None
if sys.platform == 'win32':
    from PyInstaller.utils.win32.versioninfo import (
        FixedFileInfo, StringFileInfo, StringStruct, StringTable,
        VarFileInfo, VarStruct, VSVersionInfo,
    )

    version_tuple = tuple(int(part) for part in APP_VERSION.split('.')) + (0,)
    windows_version_info = VSVersionInfo(
        ffi=FixedFileInfo(filevers=version_tuple, prodvers=version_tuple),
        kids=[
            StringFileInfo([
                StringTable('080A04B0', [
                    StringStruct('CompanyName', 'SelladoMX'),
                    StringStruct('FileDescription', 'SelladoMX'),
                    StringStruct('FileVersion', APP_VERSION),
                    StringStruct('InternalName', 'selladomx'),
                    StringStruct('LegalCopyright', 'Licencia MIT'),
                    StringStruct('OriginalFilename', 'selladomx.exe'),
                    StringStruct('ProductName', 'SelladoMX'),
                    StringStruct('ProductVersion', APP_VERSION),
                ]),
            ]),
            VarFileInfo([VarStruct('Translation', [0x080A, 1200])]),
        ],
    )

pyhanko_datas = collect_data_files('pyhanko')
pyhanko_certvalidator_datas = collect_data_files('pyhanko_certvalidator')

from pathlib import Path
qml_src = Path('src/selladomx/ui/qml')
qml_datas = []
if qml_src.exists():
    for qml_file in qml_src.rglob('*.qml'):
        rel_path = qml_file.relative_to('src/selladomx/ui/qml')
        dest_dir = f'selladomx/ui/qml/{rel_path.parent}'
        qml_datas.append((str(qml_file), dest_dir))

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
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version=windows_version_info,
    icon='assets/selladomx.ico' if sys.platform == 'win32' else 'assets/selladomx.icns' if sys.platform == 'darwin' else 'assets/selladomx.png',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
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
            'CFBundleVersion': APP_VERSION,
            'CFBundleShortVersionString': APP_VERSION,
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
