# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

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
        'webdriver_manager',
        'openpyxl',
        'selenium',
        'PyQt6.QtCore',
        'PyQt6.QtWidgets',
        'PyQt6.QtNetwork',
        'PyQt6.QtGui',
        'selenium.webdriver',
        'selenium.webdriver.common',
        'selenium.webdriver.chrome.service',
        'selenium.webdriver.remote.webelement',
        'webdriver_manager.chrome',
        'PyQt6.sip',
        'PyQt6.QtPrintSupport'
    ],
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
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico'
) 