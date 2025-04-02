from cx_Freeze import setup, Executable
import sys
import os
import platform

def main():
    # 1. Verifica arquitetura (x64 ou x86)
    arch = platform.architecture()[0]
    if arch != "64bit":
        print("Erro: Este build requer arquitetura x64.")
        sys.exit(1)

    # 2. Configuração dos caminhos do PyQt6
    def get_qt_paths():
        """Obtém os caminhos corretos para os arquivos do Qt"""
        # Tenta primeiro no ambiente virtual
        base_path = sys.prefix
        pyqt6_path = os.path.join(base_path, "Lib", "site-packages", "PyQt6")
        
        # Fallback para instalação global
        if not os.path.exists(pyqt6_path):
            base_path = os.path.dirname(sys.executable)
            pyqt6_path = os.path.join(base_path, "Lib", "site-packages", "PyQt6")
        
        if not os.path.exists(pyqt6_path):
            raise FileNotFoundError("PyQt6 não encontrado. Instale com: pip install PyQt6")
        
        return {
            'plugins': os.path.join(pyqt6_path, "Qt6", "plugins"),
            'translations': os.path.join(pyqt6_path, "Qt6", "translations"),
        }

    qt_paths = get_qt_paths()

    # 3. Arquivos adicionais para incluir
    include_files = [
        ('icon.ico', 'icon.ico'),  # Ícone do aplicativo
    ]

    # Plugins essenciais do Qt
    qt_plugins = [
        ('platforms', 'platforms'),
        ('styles', 'styles'),
        ('tls', 'tls')
    ]

    for plugin, dest in qt_plugins:
        src_path = os.path.join(qt_paths['plugins'], plugin)
        if os.path.exists(src_path):
            include_files.append((src_path, dest))

    # 4. Configuração de build otimizada
    build_options = {
        'packages': [
            'pandas',
            'webdriver_manager',
            'openpyxl',
            'selenium',
        ],
        'includes': [
            'PyQt6.QtCore', 'PyQt6.QtWidgets',
            'PyQt6.QtNetwork',
            'PyQt6.QtGui',
            'selenium.webdriver',
            'selenium.webdriver.common',
            'selenium.webdriver.chrome.service',
            'selenium.webdriver.remote.webelement',
            'webdriver_manager.chrome'
        ],
        'excludes': [
            'PyQt5',
            'PySide6',
            'PySide2',
            'tkinter',
            'matplotlib',
            'numpy.tests'  # Reduz tamanho excluindo testes do numpy
        ],
        'include_files': include_files,
        'include_msvcr': True,
        'optimize': 2,
        'zip_include_packages': '*',
        'zip_exclude_packages': [],
    }

    # 5. Configuração do executável
    executables = [
        Executable(
            'app/main.py',
            base= None,
            target_name='auto_art_v2.exe',
            icon='icon.ico',
            shortcut_name="Auto Art v2.0",
            shortcut_dir="DesktopFolder"
        )
    ]

    setup(
        name='Auto Art v2.0',
        version='2.0',
        description='Aplicativo de automação de art',
        options={'build_exe': build_options},
        executables=executables
    )

if __name__ == '__main__':
    main()