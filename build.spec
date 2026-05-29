# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

# Selenium 4+ usa imports lazy (webdriver.Chrome); PyInstaller não os detecta sozinho.
selenium_webdriver_imports = (
    collect_submodules('selenium.webdriver.chrome')
    + collect_submodules('selenium.webdriver.chromium')
    + collect_submodules('selenium.webdriver.remote')
    + [m for m in collect_submodules('selenium.webdriver.common') if '.devtools.' not in m]
    + collect_submodules('selenium.webdriver.support')
    + collect_submodules('selenium.common')
)

a = Analysis(
    ['app/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('icon.ico', '.'),
        ('ui', 'ui'),
        ('docs', 'docs')
    ],
    hiddenimports=[
        'pandas',
        'openpyxl',
        'numpy',
        'encodings.idna',
        'PyQt6.QtCore',
        'PyQt6.QtWidgets',
        'PyQt6.QtNetwork',
        'PyQt6.QtGui',
        'PyQt6.sip',
        'PyQt6.QtPrintSupport',
    ] + selenium_webdriver_imports + collect_submodules('webdriver_manager'),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PyQt5', 'PySide6', 'PySide2', 'tkinter', 'matplotlib', 'numpy.tests'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='auto_art_v2',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',
    version=None,
    uac_admin=False,
    uac_uiaccess=False,
    contents_directory='.'
) 