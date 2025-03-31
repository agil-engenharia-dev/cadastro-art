# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('C:/Ágil/cadastro-art/app/qt/mainwindow.py', 'qt'), ('C:/Ágil/cadastro-art/app/qt/ui_form.py', 'qt'), ('C:/Ágil/cadastro-art/app/qt/img_rc.py', 'qt'), ('C:\\Ágil\\cadastro-art\\app\\__init__.py', 'app'), ('C:\\Ágil\\cadastro-art\\app\\utils\\cliente.py', 'utils'), ('C:\\Ágil\\cadastro-art\\app\\utils\\clienteCE.py', 'utils'), ('C:\\Ágil\\cadastro-art\\app\\utils\\clienteMA.py', 'utils'), ('C:\\Ágil\\cadastro-art\\app\\utils\\validation.py', 'utils')],
    hiddenimports=['PySide6.QtCore', 'PySide6.QtWidgets', 'PySide6.QtGui', 'selenium.webdriver.common.by', 'selenium.webdriver.support.wait', 'selenium.webdriver.support.expected_conditions', 'selenium.webdriver.support.ui', 'selenium.common.exceptions', 'selenium.webdriver.common.keys', 'selenium.webdriver.chrome.options', 'selenium.webdriver', 'webdriver_manager'],
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
    name='main',
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
)
