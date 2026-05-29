import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog
from datetime import datetime
from .ui_form import Ui_MainWindow
import os

NIVEL_ATIVIDADE_PADRAO = "16 - Execução"
ATIVIDADE_PROFISSIONAL_PADRAO = "55 - Execução de serviço técnico"
ALTURA_JANELA_PADRAO = 650
ALTURA_JANELA_MA = 750

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
        self.ui.checkBox_salvar_erros.toggled.connect(self.onSalvarErrosToggled)
        self.ui.pushButton_caminho_erros.clicked.connect(self.onEscolherCaminhoErrosClicked)
        self.ui.comboBox_formato_erros.currentIndexChanged.connect(self.onFormatoErrosChanged)
        
        # Inicializa os valores de resultado como None
        self.resultado_line_edit = None
        self.resultado_nivel_atividade = None
        self.resultado_atividade_profissional = None
        self.resultado_radio_button = None
        self.resultado_label = None
        self.resultado_login = None
        self.resultado_senha = None
        self.resultado_salvar_erros = False
        self.resultado_formato_erros = "xlsx"
        self.resultado_caminho_erros = ""

        # Definir estilo fixo para a aplicação
        self.setFixedStyle()
        self._init_relatorio_erros_ui()
        self._init_campos_ma_ui()

    def _fmt_erros(self) -> str:
        return "xlsx" if self.ui.comboBox_formato_erros.currentIndex() == 0 else "csv"

    def _normalizar_extensao(self, caminho: str, fmt: str) -> str:
        caminho = (caminho or "").strip()
        if not caminho:
            return ""
        lower = caminho.lower()
        if fmt == "xlsx":
            if lower.endswith(".csv"):
                return caminho[:-4] + ".xlsx"
            if not lower.endswith(".xlsx"):
                return caminho + ".xlsx"
            return caminho
        # csv
        if lower.endswith(".xlsx"):
            return caminho[:-5] + ".csv"
        if not lower.endswith(".csv"):
            return caminho + ".csv"
        return caminho

    def _init_relatorio_erros_ui(self):
        # Defaults
        self.ui.comboBox_formato_erros.setCurrentIndex(0)  # Excel
        self.ui.comboBox_formato_erros.setEnabled(False)
        self.ui.lineEdit_caminho_erros.setEnabled(False)
        self.ui.pushButton_caminho_erros.setEnabled(False)

    def _init_campos_ma_ui(self):
        if not self.ui.lineEdit_nivel_atividade.text().strip():
            self.ui.lineEdit_nivel_atividade.setText(NIVEL_ATIVIDADE_PADRAO)
        if not self.ui.lineEdit_atividade_profissional.text().strip():
            self.ui.lineEdit_atividade_profissional.setText(ATIVIDADE_PROFISSIONAL_PADRAO)
        self._atualizar_campos_ma(None)

    def _atualizar_campos_ma(self, estado):
        visivel = estado == "MA"
        self.ui.lineEdit_nivel_atividade.setVisible(visivel)
        self.ui.lineEdit_atividade_profissional.setVisible(visivel)
        altura = ALTURA_JANELA_MA if visivel else ALTURA_JANELA_PADRAO
        self.setFixedSize(400, altura)
        self.ui.centralwidget.setMinimumSize(400, altura)
        self.ui.centralwidget.setMaximumSize(16777215, altura)

    def encerrar(self):
        # Captura os valores dos campos
        self.resultado_line_edit = self.ui.lineEdit.text()
        self.resultado_nivel_atividade = self.ui.lineEdit_nivel_atividade.text()
        self.resultado_atividade_profissional = (
            self.ui.lineEdit_atividade_profissional.text()
        )
        self.resultado_label = self.ui.label.text()
        self.resultado_login = self.ui.lineEdit_login.text()
        self.resultado_senha = self.ui.lineEdit_senha.text()
        self.resultado_salvar_erros = bool(self.ui.checkBox_salvar_erros.isChecked())
        self.resultado_formato_erros = "xlsx" if self.ui.comboBox_formato_erros.currentIndex() == 0 else "csv"
        self.resultado_caminho_erros = self.ui.lineEdit_caminho_erros.text()
        self.close()

    def on_radio_button_clicked(self):
        sender = self.sender()
        if sender.isChecked():
            estado = sender.text()
            self.resultado_radio_button = estado
            self._atualizar_campos_ma(estado)

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

    def onSalvarErrosToggled(self, checked: bool):
        self.ui.comboBox_formato_erros.setEnabled(bool(checked))
        self.ui.lineEdit_caminho_erros.setEnabled(bool(checked))
        self.ui.pushButton_caminho_erros.setEnabled(bool(checked))

        if checked and not self.ui.lineEdit_caminho_erros.text().strip():
            # Sugere um nome padrão na mesma pasta da planilha (quando possível)
            base_dir = ""
            try:
                planilha_path = self.ui.label.text().strip()
                if planilha_path and planilha_path != "...":
                    base_dir = os.path.dirname(planilha_path)
            except Exception:
                base_dir = ""

            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            ext = ".xlsx" if self._fmt_erros() == "xlsx" else ".csv"
            nome = f"erros_cadastro_{ts}{ext}"
            sugestao = os.path.join(base_dir, nome) if base_dir else nome
            self.ui.lineEdit_caminho_erros.setText(sugestao)
        elif checked:
            # Garante que a extensão está coerente com o formato selecionado
            fmt = self._fmt_erros()
            atual = self.ui.lineEdit_caminho_erros.text()
            self.ui.lineEdit_caminho_erros.setText(self._normalizar_extensao(atual, fmt))

    def onFormatoErrosChanged(self, _index: int):
        if not self.ui.checkBox_salvar_erros.isChecked():
            return
        fmt = self._fmt_erros()
        atual = self.ui.lineEdit_caminho_erros.text()
        self.ui.lineEdit_caminho_erros.setText(self._normalizar_extensao(atual, fmt))

    def onEscolherCaminhoErrosClicked(self):
        fmt = self._fmt_erros()
        filtro = "Excel (*.xlsx)" if fmt == "xlsx" else "CSV (*.csv)"
        sugestao = self._normalizar_extensao(self.ui.lineEdit_caminho_erros.text(), fmt)
        file_name, _ = QFileDialog.getSaveFileName(
            parent=self,
            caption="Salvar relatório de erros",
            directory=sugestao,
            filter=filtro,
            options=QFileDialog.Option.DontUseNativeDialog,
        )
        if file_name:
            self.ui.lineEdit_caminho_erros.setText(self._normalizar_extensao(file_name, fmt))

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
    nivel_atividade = None
    atividade_profissional = None
    if estado == "MA":
        nivel_atividade = (
            widget.resultado_nivel_atividade.strip()
            if widget.resultado_nivel_atividade
            else NIVEL_ATIVIDADE_PADRAO
        )
        if not nivel_atividade:
            nivel_atividade = NIVEL_ATIVIDADE_PADRAO
        atividade_profissional = (
            widget.resultado_atividade_profissional.strip()
            if widget.resultado_atividade_profissional
            else ATIVIDADE_PROFISSIONAL_PADRAO
        )
        if not atividade_profissional:
            atividade_profissional = ATIVIDADE_PROFISSIONAL_PADRAO

    data = {
        "login": login,
        "senha": senha,
        "dir_planilha": dir_planilha,
        "estado": estado,
        "numero_art": numero_art,
        "nivel_atividade": nivel_atividade,
        "atividade_profissional": atividade_profissional,
        "salvar_relatorio_erros": widget.resultado_salvar_erros,
        "formato_relatorio_erros": widget.resultado_formato_erros,
        "caminho_relatorio_erros": widget.resultado_caminho_erros.strip() if widget.resultado_caminho_erros else "",
    }

    return data

if __name__ == "__main__":
    data = tela()
    print("Valores:", data)
