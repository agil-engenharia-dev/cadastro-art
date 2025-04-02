import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog
from .ui_form import Ui_MainWindow

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.pushButton.clicked.connect(self.onOpenButtonClicked)
        self.ui.pushButton_cadastrar.clicked.connect(self.encerrar)
        self.ui.radioButtonCE.clicked.connect(self.on_radio_button_clicked)
        self.ui.radioButtonMA.clicked.connect(self.on_radio_button_clicked)
        self.ui.radioButtonSE.clicked.connect(self.on_radio_button_clicked)
        
        # Inicializa os valores de resultado como None
        self.resultado_line_edit = None
        self.resultado_radio_button = None
        self.resultado_label = None
        self.resultado_login = None
        self.resultado_senha = None

        # Definir estilo fixo para a aplicação
        self.setFixedStyle()

    def encerrar(self):
        # Captura os valores dos campos
        self.resultado_line_edit = self.ui.lineEdit.text()
        self.resultado_label = self.ui.label.text()
        self.resultado_login = self.ui.lineEdit_login.text()
        self.resultado_senha = self.ui.lineEdit_senha.text()
        self.close()

    def on_radio_button_clicked(self):
        sender = self.sender()
        if sender.isChecked():
            self.resultado_radio_button = sender.text()

    def onOpenButtonClicked(self):
        file_name, _ = QFileDialog.getOpenFileName(
            parent=self,
            caption="Selecionar Arquivo",
            directory="",  # Diretório inicial vazio
            filter="Todos os arquivos (*)",  # Filtro de arquivos
            options=QFileDialog.Option.DontUseNativeDialog  # Opções (opcional)
        )
        
        if file_name:  # Verifica se um arquivo foi selecionado
            self.ui.label.setText(file_name)
            self.ui.pushButton_cadastrar.setEnabled(True)

    def setFixedStyle(self):
        # Defina um estilo CSS fixo para a aplicação
        app_style = """
        QMainWindow {
            background-color: #2E2E2E;
            color: #FFFFFF;
        }
        QPushButton {
            background-color: #555555;
            color: white;
            border: none;
            padding: 10px 20px;
            font-size: 14px;
        }
        QPushButton:hover {
            background-color: #555555;
        }
        QLineEdit, QRadioButton {
            background-color: #555555;
            color: white;
            border-radius: 5px;
        }
        """
        self.setStyleSheet(app_style)

def tela():
    app = QApplication.instance() or QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    app.exec()

    # Verificar se os valores não são None antes de usar strip()
    login = widget.resultado_login.strip() if widget.resultado_login else ''
    senha = widget.resultado_senha.strip() if widget.resultado_senha else ''
    dir_planilha = widget.resultado_label.strip() if widget.resultado_label else ''
    estado = widget.resultado_radio_button.strip() if widget.resultado_radio_button else ''
    numero_art = widget.resultado_line_edit.strip() if widget.resultado_line_edit else ''

    data = {
        "login": login,
        "senha": senha,
        "dir_planilha": dir_planilha,
        "estado": estado,
        "numero_art": numero_art
    }

    return data

if __name__ == "__main__":
    data = tela()
    print("Valores:", data)
