import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog

from qt.ui_form import Ui_MainWindow



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
        self.resultado_line_edit = None
        self.resultado_radio_button = None
        self.resultado_label = None
        self.resultado_login = None
        self.resultado_senha = None

    def encerrar(self):
        self.resultado_line_edit = self.ui.lineEdit.text().strip()
        self.resultado_label = self.ui.label.text().strip()
        self.resultado_login = self.ui.lineEdit_login.text().strip()
        self.resultado_senha = self.ui.lineEdit_senha.text().strip()
        self.close()

    def on_radio_button_clicked(self):
            sender = self.sender()
            if sender.isChecked():
                self.resultado_radio_button = sender.text().strip()

    def onOpenButtonClicked(self):
        options = QFileDialog.Options()
        file_dialog = QFileDialog(self, options=options)
        file_dialog.setNameFilter('Todos os arquivos (*)')

        if file_dialog.exec():
            file_names = file_dialog.selectedFiles()
            file_name = file_names[0]
            self.ui.label.setText(f"{file_name}")
            self.ui.pushButton_cadastrar.setEnabled(True)



def tela():
    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    app.exec()

    data = {
    "login":widget.resultado_login,
    "senha":widget.resultado_senha,
    "dir_planilha":widget.resultado_label,
    "estado":widget.resultado_radio_button,
    "numero_art":widget.resultado_line_edit
    }


    return data
if __name__ == "__main__":
    data = tela()
    print("Valores:",data)
