import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QLabel, QMessageBox
from PyQt6.QtCore import QSignalBlocker
from datetime import datetime
from .ui_form import Ui_MainWindow
from app.utils.validation import validar_dados_formulario
from app.utils.credentials_store import CredentialsStore
from app.utils.error_report import (
    caminho_relatorio_informado_na_ui,
    caminho_relatorio_padrao,
)
import os

NIVEL_ATIVIDADE_PADRAO = "16 - Execução"
ATIVIDADE_PROFISSIONAL_PADRAO = "55 - Execução de serviço técnico"
ALTURA_JANELA_PADRAO = 650
ALTURA_JANELA_MA = 750

_ESTILO_CAMPO_ERRO = (
    "border: 2px solid #ff4444;"
    "border-radius:10px;"
    "padding-left:6px;"
    "color:#fff;"
)
_ESTILO_LABEL_PLANILHA_ERRO = "color:#ff4444; background-color:transparent;"

_CAMPOS_WIDGET = {
    "login": "lineEdit_login",
    "senha": "lineEdit_senha",
    "dir_planilha": "label",
    "numero_art": "lineEdit",
    "nivel_atividade": "lineEdit_nivel_atividade",
    "atividade_profissional": "lineEdit_atividade_profissional",
    "caminho_relatorio_erros": "lineEdit_caminho_erros",
}


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
        self._aceito = False
        self._estilos_campos_originais: dict[str, str] = {}
        self._credentials = CredentialsStore()

        # Definir estilo fixo para a aplicação
        self.setFixedStyle()
        self._init_relatorio_erros_ui()
        self._init_campos_ma_ui()
        self._init_validacao_ui()
        self._init_credenciais_ui()

    def _init_credenciais_ui(self):
        # Carrega último login/senha e pré-preenche (sem forçar seleção de tipo)
        self._credentials.load()
        last_tipo = self._credentials.get_last_tipo()

        # Pré-seleciona o último tipo (se nenhum estiver marcado)
        if not self._estado_selecionado() and last_tipo:
            self._selecionar_estado(last_tipo)

        last = self._credentials.get_last()
        if not self.ui.lineEdit_login.text().strip() and last.login:
            self.ui.lineEdit_login.setText(last.login)
        if not self.ui.lineEdit_senha.text().strip() and last.senha:
            self.ui.lineEdit_senha.setText(last.senha)

        # Se já houver um estado marcado no .ui, aplica o do tipo
        estado = self._estado_selecionado()
        if estado:
            self._aplicar_credenciais_para_estado(estado)

    def _selecionar_estado(self, estado: str) -> None:
        estado = (estado or "").strip().upper()
        if estado == "CE":
            with QSignalBlocker(self.ui.radioButtonCE):
                self.ui.radioButtonCE.setChecked(True)
            self._atualizar_campos_ma("CE")
            return
        if estado == "MA":
            with QSignalBlocker(self.ui.radioButtonMA):
                self.ui.radioButtonMA.setChecked(True)
            self._atualizar_campos_ma("MA")
            return
        if estado == "CFT":
            with QSignalBlocker(self.ui.radioButtonSE):
                self.ui.radioButtonSE.setChecked(True)
            self._atualizar_campos_ma("CFT")
            return

    def _aplicar_credenciais_para_estado(self, estado: str):
        estado = (estado or "").strip().upper()
        if not estado:
            return
        cred = self._credentials.get_for_tipo(estado)
        if not cred.login and not cred.senha:
            cred = self._credentials.get_last()
        if cred.login:
            self.ui.lineEdit_login.setText(cred.login)
        if cred.senha:
            self.ui.lineEdit_senha.setText(cred.senha)

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
        # Relatório de erros ativo por padrão (sempre gravado quando houver falhas)
        self.ui.comboBox_formato_erros.setCurrentIndex(0)  # Excel
        self.ui.checkBox_salvar_erros.setChecked(True)
        self.onSalvarErrosToggled(True)

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

    def _init_validacao_ui(self):
        self.label_validacao = QLabel(parent=self.ui.centralwidget)
        self.label_validacao.setWordWrap(True)
        self.label_validacao.setStyleSheet(
            "color: #ff6b6b; background: transparent; font-size: 12px;"
        )
        self.label_validacao.setVisible(False)
        idx = self.ui.verticalLayout.indexOf(self.ui.pushButton_cadastrar)
        self.ui.verticalLayout.insertWidget(idx, self.label_validacao)

    def _estado_selecionado(self) -> str:
        if self.ui.radioButtonCE.isChecked():
            return "CE"
        if self.ui.radioButtonMA.isChecked():
            return "MA"
        if self.ui.radioButtonSE.isChecked():
            return "CFT"
        return ""

    def _coletar_dados_formulario(self) -> dict:
        estado = self._estado_selecionado()
        planilha = self.ui.label.text().strip()
        dados = {
            "login": self.ui.lineEdit_login.text().strip(),
            "senha": self.ui.lineEdit_senha.text().strip(),
            "dir_planilha": planilha,
            "estado": estado,
            "numero_art": self.ui.lineEdit.text().strip(),
            "salvar_relatorio_erros": bool(self.ui.checkBox_salvar_erros.isChecked()),
            "caminho_relatorio_erros": caminho_relatorio_informado_na_ui(
                self.ui.lineEdit_caminho_erros.text()
            ),
        }
        if estado == "MA":
            dados["nivel_atividade"] = self.ui.lineEdit_nivel_atividade.text().strip()
            dados["atividade_profissional"] = (
                self.ui.lineEdit_atividade_profissional.text().strip()
            )
        return dados

    def _widget_por_campo(self, campo: str):
        if campo == "estado":
            return None
        nome = _CAMPOS_WIDGET.get(campo)
        if not nome:
            return None
        return getattr(self.ui, nome, None)

    def _limpar_destaque_erros(self):
        for campo, estilo in self._estilos_campos_originais.items():
            widget = self._widget_por_campo(campo)
            if widget is not None:
                widget.setStyleSheet(estilo)
        self._estilos_campos_originais.clear()
        self.label_validacao.clear()
        self.label_validacao.setVisible(False)

    def _destacar_campos_invalidos(self, erros: list[tuple[str, str]]):
        self._limpar_destaque_erros()
        for campo, _ in erros:
            widget = self._widget_por_campo(campo)
            if widget is None:
                continue
            if campo not in self._estilos_campos_originais:
                self._estilos_campos_originais[campo] = widget.styleSheet()
            if campo == "dir_planilha":
                widget.setStyleSheet(_ESTILO_LABEL_PLANILHA_ERRO)
            else:
                widget.setStyleSheet(_ESTILO_CAMPO_ERRO)

    def _mostrar_erros_validacao(self, erros: list[tuple[str, str]]):
        mensagens = [msg for _, msg in erros]
        texto = "Preencha os campos indicados:\n\n• " + "\n• ".join(mensagens)
        self.label_validacao.setText(texto)
        self.label_validacao.setVisible(True)
        self._destacar_campos_invalidos(erros)
        if any(campo == "estado" for campo, _ in erros):
            QMessageBox.warning(
                self,
                "Dados incompletos",
                texto + "\n\nSelecione CE, MA ou CFT acima do número da ART.",
            )
        else:
            QMessageBox.warning(self, "Dados incompletos", texto)

    def encerrar(self):
        dados_parciais = self._coletar_dados_formulario()
        erros = validar_dados_formulario(dados_parciais)
        if erros:
            self._mostrar_erros_validacao(erros)
            return

        self._limpar_destaque_erros()
        self._aceito = True

        # Persistência do último login/senha por tipo (CE/MA/CFT)
        try:
            estado = (dados_parciais.get("estado") or "").strip().upper()
            login = (dados_parciais.get("login") or "").strip()
            senha = (dados_parciais.get("senha") or "")
            if estado:
                self._credentials.set_for_tipo(estado, login=login, senha=senha)
            self._credentials.set_last(estado, login=login, senha=senha)
            self._credentials.save()
        except Exception:
            pass

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
        self.resultado_radio_button = self._estado_selecionado()
        self.close()

    def on_radio_button_clicked(self):
        sender = self.sender()
        if sender.isChecked():
            estado = sender.text()
            self.resultado_radio_button = estado
            self._atualizar_campos_ma(estado)
            self._aplicar_credenciais_para_estado(estado)
            self._limpar_destaque_erros()

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

        if checked:
            atual = self.ui.lineEdit_caminho_erros.text().strip()
            if not atual or not caminho_relatorio_informado_na_ui(atual):
                self.ui.lineEdit_caminho_erros.setText(
                    caminho_relatorio_padrao(self._fmt_erros())
                )
            else:
                fmt = self._fmt_erros()
                self.ui.lineEdit_caminho_erros.setText(
                    self._normalizar_extensao(atual, fmt)
                )

    def onFormatoErrosChanged(self, _index: int):
        if not self.ui.checkBox_salvar_erros.isChecked():
            return
        fmt = self._fmt_erros()
        atual = caminho_relatorio_informado_na_ui(self.ui.lineEdit_caminho_erros.text())
        if atual:
            self.ui.lineEdit_caminho_erros.setText(self._normalizar_extensao(atual, fmt))

    def onEscolherCaminhoErrosClicked(self):
        fmt = self._fmt_erros()
        filtro = "Excel (*.xlsx)" if fmt == "xlsx" else "CSV (*.csv)"
        atual = caminho_relatorio_informado_na_ui(self.ui.lineEdit_caminho_erros.text())
        sugestao = atual or caminho_relatorio_padrao(fmt)
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

def tela() -> dict | None:
    app = QApplication.instance() or QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    app.exec()

    if not widget._aceito:
        return None

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
        "caminho_relatorio_erros": caminho_relatorio_informado_na_ui(
            widget.resultado_caminho_erros or ""
        ),
    }

    return data

if __name__ == "__main__":
    data = tela()
    print("Valores:", data)
