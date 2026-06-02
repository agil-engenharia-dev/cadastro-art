from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import time

from app.utils.browser_windows import definir_janela_principal
from app.utils.cliente_sitac import ClienteSitac
from app.utils.error_report import ErrorReport
from app.utils.selenium_actions import preencher_seguro


class ClienteCFT(ClienteSitac):
    def __init__(self, args):
        super().__init__(args)
        self.URL_LOGIN_CFT = "https://servicos.sinceti.net.br/"
        self.URL_TRT = "https://servicos.sinceti.net.br/app/view/sight/ini?form=Art&id="

    def _preencher_campos_extras_modal_pf(self, browser) -> None:
        element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
            EC.presence_of_element_located((By.ID, "SEXO"))
        )
        select = Select(element_select)
        select.select_by_value(self.sexo[0].upper())

    def cadastrar(
        self, browser, numero_trt, error_report: ErrorReport | None = None
    ):
        browser.get(self.URL_TRT + numero_trt)
        definir_janela_principal(browser)

        element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
            EC.presence_of_element_located(
                (By.ID, f"cadastrarContratoArt{numero_trt}")
            )
        )
        element_select.click()

        time.sleep(5)

        try:
            element_select = WebDriverWait(browser, 2).until(
                EC.presence_of_element_located((By.ID, "NIVEL00"))
            )
            select = Select(element_select)
            select.select_by_value("5")
        except Exception:
            element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
                EC.presence_of_element_located((By.ID, "NOVA_ATIVIDADE"))
            )
            element_select.click()

        element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
            EC.presence_of_element_located((By.ID, "CONTRATO_DATA0"))
        )
        element_select.clear()
        element_select.send_keys(self.data)

        element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
            EC.presence_of_element_located((By.ID, "CONTRATO_DATAINICIO0"))
        )
        element_select.clear()
        element_select.send_keys(self.data)

        element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
            EC.presence_of_element_located((By.ID, "CONTRATO_DATAFIM0"))
        )
        element_select.clear()
        element_select.send_keys(self.data)

        element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
            EC.presence_of_element_located((By.ID, "NIVEL00"))
        )
        select = Select(element_select)
        select.select_by_value("5")

        element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
            EC.presence_of_element_located((By.ID, "ATIVIDADEPROFISSIONAL00"))
        )
        select = Select(element_select)
        select.select_by_value("2394")

        element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
            EC.presence_of_element_located((By.ID, "LABELATUACAO00"))
        )
        element_select.send_keys("1", "9", "9", "0")
        time.sleep(4)
        xpath = "//div[@id='listaAtividadeEscolherATUACAO00']//li[1]"
        browser.find_element(By.XPATH, xpath).click()

        element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
            EC.presence_of_element_located((By.ID, "UNIDADEMEDIDA00"))
        )
        select = Select(element_select)
        select.select_by_value("79")

        element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
            EC.presence_of_element_located((By.ID, "QUANTIDADE00"))
        )
        element_select.clear()
        element_select.send_keys("1,000")

        self.cadastrar_contratante(browser, error_report)

        element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
            EC.presence_of_element_located((By.ID, "CONTRATO_VALOR0"))
        )
        element_select.clear()
        element_select.send_keys(self.valor_do_plano)

        time.sleep(5)
        element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
            EC.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    "#evtContratoEnderecoContainerSpecific0 > div.cad_form_cont_campo > input[type=radio]:nth-child(1)",
                )
            )
        )
        element_select.click()
        time.sleep(5)

        element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
            EC.presence_of_element_located((By.ID, "save"))
        )

        WebDriverWait(browser, 10).until(
            EC.invisibility_of_element_located((By.ID, "ajax-overlay"))
        )

        element_select.click()
        self.verificar_feedback_plataforma(
            browser,
            error_report,
            etapa="cadastro_contrato",
        )

    def login_CFT(self, browser, login, senha) -> None:
        browser.get(self.URL_LOGIN_CFT)

        cpf_input = WebDriverWait(browser, self.TIME_TO_WAIT).until(
            EC.presence_of_element_located((By.ID, "login"))
        )

        senha_input = WebDriverWait(browser, self.TIME_TO_WAIT).until(
            EC.presence_of_element_located((By.ID, "senha"))
        )

        login_button = WebDriverWait(browser, self.TIME_TO_WAIT).until(
            EC.presence_of_element_located((By.ID, "enviar"))
        )

        preencher_seguro(browser, cpf_input, login)
        preencher_seguro(browser, senha_input, senha)
        login_button.click()

        WebDriverWait(browser, self.TIME_TO_WAIT).until(
            EC.presence_of_element_located((By.ID, "logout_info"))
        )
