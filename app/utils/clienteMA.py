from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import time
import re
import unicodedata
from app.utils.cliente_sitac import ClienteSitac
from app.utils.art_cep import (
    aguardar_overlay_invisivel,
    fluxo_modal_cep,
    fluxo_cep_contrato,
)
from app.utils.browser_windows import definir_janela_principal, janela_auxiliar
from app.utils.error_report import ErrorReport
from app.utils.selenium_actions import (
    clicar_seguro,
    preencher_seguro,
    selecionar_por_valor_seguro,
)
from selenium.common.exceptions import NoSuchElementException, TimeoutException


class ClienteMA(ClienteSitac):
    NIVEL_ATIVIDADE_PADRAO = "16 - Execução"
    ATIVIDADE_PROFISSIONAL_PADRAO = "55 - Execução de serviço técnico"

    def __init__(self, args):
        super().__init__(args)
        self.URL_LOGIN_CREA = "https://servicos-crea-ma.sitac.com.br//index.php"
        self.URL_ART = (
            "https://servicos-crea-ma.sitac.com.br/app/view/sight/ini?form=Art&id="
        )

    def _selecionar_opcao_por_titulo(
        self, browser, titulo, padrao, element_id, descricao_campo
    ):
        def _norm(s: str) -> str:
            s = (s or "").strip()
            if not s:
                return ""
            s = unicodedata.normalize("NFKD", s)
            s = "".join(ch for ch in s if not unicodedata.combining(ch))
            s = s.lower()
            s = re.sub(r"\s+", " ", s).strip()
            return s

        def _codigo_prefixo(s: str) -> str | None:
            m = re.match(r"^\s*(\d+)\s*[-–]\s*.+$", s or "")
            return m.group(1) if m else None

        titulo = (titulo or padrao).strip()
        titulo_norm = _norm(titulo)
        titulo_cod = _codigo_prefixo(titulo)

        element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
            EC.presence_of_element_located((By.ID, element_id))
        )

        # Em alguns formulários do SITAC as opções do <select> são carregadas via JS
        # após a presença do elemento. Espera até existir pelo menos 1 opção com value.
        WebDriverWait(browser, self.TIME_TO_WAIT).until(
            lambda d: any(
                (opt.get_attribute("value") or "").strip()
                for opt in Select(d.find_element(By.ID, element_id)).options
            )
        )

        select = Select(element_select)
        for option in select.options:
            valor = (option.get_attribute("value") or "").strip()
            if not valor:
                continue

            opt_title = (option.get_attribute("title") or "").strip()
            opt_text = (option.text or "").strip()
            opt_norm_title = _norm(opt_title)
            opt_norm_text = _norm(opt_text)

            # Match flexível: exato / normalizado / por código numérico (ex: "16 - ...")
            opt_cod = _codigo_prefixo(opt_text) or _codigo_prefixo(opt_title)
            if (
                opt_title == titulo
                or opt_text == titulo
                or (titulo_norm and (opt_norm_title == titulo_norm or opt_norm_text == titulo_norm))
                or (titulo_cod and opt_cod and titulo_cod == opt_cod)
                or (titulo_norm and (titulo_norm in opt_norm_text or titulo_norm in opt_norm_title))
            ):
                selecionar_por_valor_seguro(browser, element_select, valor)
                return

        raise ValueError(
            f"{descricao_campo} '{titulo}' não encontrado em {element_id}. "
            f"Use o texto/código da opção (ex: {padrao})."
        )

    def _selecionar_nivel_atividade(
        self, browser, nivel_atividade=None, element_id="NIVEL00"
    ):
        self._selecionar_opcao_por_titulo(
            browser,
            nivel_atividade,
            self.NIVEL_ATIVIDADE_PADRAO,
            element_id,
            "Nível",
        )

    def _selecionar_atividade_profissional(
        self, browser, atividade_profissional=None, element_id="ATIVIDADEPROFISSIONAL00"
    ):
        element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
            EC.presence_of_element_located((By.ID, element_id))
        )
        if not element_select.is_enabled():
            WebDriverWait(browser, 10).until(
                lambda d: d.find_element(By.ID, element_id).is_enabled()
            )
        self._selecionar_opcao_por_titulo(
            browser,
            atividade_profissional,
            self.ATIVIDADE_PROFISSIONAL_PADRAO,
            element_id,
            "Atividade profissional",
        )

    def cadastrar(
        self,
        browser,
        numero_art,
        nivel_atividade=None,
        atividade_profissional=None,
        error_report: ErrorReport | None = None,
    ):
        nivel_atividade = (nivel_atividade or self.NIVEL_ATIVIDADE_PADRAO).strip()
        atividade_profissional = (
            atividade_profissional or self.ATIVIDADE_PROFISSIONAL_PADRAO
        ).strip()
        browser.get(self.URL_ART + numero_art)
        definir_janela_principal(browser)
        try:
            browser.maximize_window()
        except Exception:
            pass

        aguardar_overlay_invisivel(browser)
        element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
            EC.element_to_be_clickable(
                (By.ID, f"cadastrarContratoArt{numero_art}")
            )
        )
        clicar_seguro(browser, element_select)

        time.sleep(5)

        try:
            popup_fechar = WebDriverWait(browser, 2).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(text(),'Nunca')]")
                )
            )
            clicar_seguro(browser, popup_fechar)
        except:
            pass

        time.sleep(2)
        try:
            element_select = WebDriverWait(browser, 5).until(
                EC.presence_of_element_located((By.ID, "ACAOINSTITUCIONAL"))
            )
            selecionar_por_valor_seguro(browser, element_select, "11")  # outros
        except:
            pass

        try:
            self._selecionar_nivel_atividade(browser, nivel_atividade)
        except:
            element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
                EC.element_to_be_clickable((By.ID, "NOVA_ATIVIDADE"))
            )
            clicar_seguro(browser, element_select)

        time.sleep(1)

        self._selecionar_nivel_atividade(browser, nivel_atividade)

        time.sleep(2)

        self._selecionar_atividade_profissional(browser, atividade_profissional)

        # 1. Clica no botão para abrir o modal
        aguardar_overlay_invisivel(browser)
        element_button = WebDriverWait(browser, self.TIME_TO_WAIT).until(
            EC.element_to_be_clickable((By.ID, "ESCOLHERATUACAO"))
        )
        with janela_auxiliar(
            browser, lambda: clicar_seguro(browser, element_button)
        ) as entrou_popup:
            if not entrou_popup:
                raise TimeoutException(
                    "Popup de atuação profissional não abriu após ESCOLHERATUACAO."
                )

            time.sleep(2)
            mostrar_todos = WebDriverWait(browser, 20).until(
                EC.element_to_be_clickable((By.ID, "exibirTodos"))
            )
            browser.execute_script("arguments[0].scrollIntoView();", mostrar_todos)
            browser.execute_script("arguments[0].click();", mostrar_todos)
            time.sleep(2)

            try:
                eletronica = WebDriverWait(browser, 20).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//*[contains(text(), '12 - Eletrônica')]")
                    )
                )
                browser.execute_script("arguments[0].scrollIntoView();", eletronica)
                browser.execute_script("arguments[0].click();", eletronica)
                time.sleep(1)

                fibras = WebDriverWait(browser, 20).until(
                    EC.element_to_be_clickable(
                        (
                            By.XPATH,
                            "//*[contains(text(), '12.7 - Sistemas e Equipamentos de Fibras Ópticas')]",
                        )
                    )
                )
                browser.execute_script("arguments[0].scrollIntoView();", fibras)
                browser.execute_script("arguments[0].click();", fibras)
                time.sleep(1)

                item_alvo = WebDriverWait(browser, 20).until(
                    EC.element_to_be_clickable(
                        (
                            By.XPATH,
                            "//*[contains(text(), '12.7.1 - de rede de fibra óptica')]",
                        )
                    )
                )
                browser.execute_script("arguments[0].scrollIntoView();", item_alvo)
                browser.execute_script("arguments[0].click();", item_alvo)
                time.sleep(1)
            except Exception as e:
                print(f"Erro ao navegar na árvore: {e}")
                raise

        element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
            EC.presence_of_element_located((By.ID, "UNIDADEMEDIDA00"))
        )
        selecionar_por_valor_seguro(browser, element_select, "79")  # unidade de medida

        element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
            EC.element_to_be_clickable((By.ID, "QUANTIDADE00"))
        )
        preencher_seguro(browser, element_select, "1,00")  # quantidade

        self.cadastrar_contratante(browser, error_report)

        time.sleep(5)

        # Clica no botão de coordenadas para abrir o mapa
        try:
            btn_coordenadas = WebDriverWait(browser, 5).until(
                EC.element_to_be_clickable((By.ID, "ESCOLHERCORDENADASGMAP"))
            )
            with janela_auxiliar(
                browser,
                lambda: clicar_seguro(browser, btn_coordenadas),
                fechar_ao_sair=True,
            ):
                time.sleep(5)
            time.sleep(1)

            # Preenche latitude e longitude com 0 apenas se estiverem vazios
            try:
                latitude = WebDriverWait(browser, 3).until(
                    EC.presence_of_element_located(
                        (By.ID, "CONTRATO_ENDERECO_LATITUDE0")
                    )
                )
                if (
                    not latitude.get_attribute("value")
                    or latitude.get_attribute("value").strip() == ""
                ):
                    latitude.clear()
                    latitude.send_keys("0")

                longitude = WebDriverWait(browser, 3).until(
                    EC.presence_of_element_located(
                        (By.ID, "CONTRATO_ENDERECO_LONGITUDE0")
                    )
                )
                if (
                    not longitude.get_attribute("value")
                    or longitude.get_attribute("value").strip() == ""
                ):
                    longitude.clear()
                    longitude.send_keys("0")
            except:
                pass
        except:
            pass  # Se não encontrar o botão, continua normalmente

        element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
            EC.element_to_be_clickable((By.ID, "CONTRATO_VALOR0"))
        )
        preencher_seguro(browser, element_select, self.valor_do_plano)
        element_select.send_keys(Keys.TAB, Keys.ARROW_UP)

        element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
            EC.element_to_be_clickable((By.ID, "CONTRATO_DATA0"))
        )
        preencher_seguro(browser, element_select, self.data)

        element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
            EC.element_to_be_clickable((By.ID, "CONTRATO_DATAINICIO0"))
        )
        preencher_seguro(browser, element_select, self.data)

        element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
            EC.element_to_be_clickable((By.ID, "CONTRATO_DATAFIM0"))
        )
        preencher_seguro(browser, element_select, self.data)

        time.sleep(5)

        try:
            element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
                EC.presence_of_element_located((By.ID, "CONTRATO_ENDERECO_CEP0"))
            )
            fluxo_cep_contrato(browser, element_select, self, self.TIME_TO_WAIT)

            element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
                EC.presence_of_element_located(
                    (By.ID, "CONTRATO_ENDERECO_TIPOLOGRADOURO0")
                )
            )
            selecionar_por_valor_seguro(
                browser, element_select, self.tipo_de_logradouro
            )  # tipo_de_logradouro

            element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
                EC.element_to_be_clickable((By.ID, "CONTRATO_ENDERECO_LOGRADOURO0"))
            )
            preencher_seguro(browser, element_select, self.logradouro)  # logradouro

            element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
                EC.element_to_be_clickable((By.ID, "CONTRATO_ENDERECO_NUMERO0"))
            )
            preencher_seguro(browser, element_select, self.numero)  # numero

            element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
                EC.element_to_be_clickable((By.ID, "CONTRATO_ENDERECO_BAIRRO0"))
            )
            preencher_seguro(browser, element_select, self.bairro)  # bairro

        except:
            pass

        element_save = WebDriverWait(browser, self.TIME_TO_WAIT).until(
            EC.presence_of_element_located((By.ID, "save"))
        )

        # tenta selecionar o select ACAOINSTITUCIONAL imediatamente acima do botão 'save'
        try:
            candidate = element_save.find_element(
                By.XPATH, "./preceding::select[@id='ACAOINSTITUCIONAL'][1]"
            )
            selecionar_por_valor_seguro(browser, candidate, "11")
        except Exception:
            try:
                acao_select = WebDriverWait(browser, 2).until(
                    EC.presence_of_element_located((By.ID, "ACAOINSTITUCIONAL"))
                )
                selecionar_por_valor_seguro(browser, acao_select, "11")
            except Exception:
                pass

        aguardar_overlay_invisivel(browser)
        element_save = WebDriverWait(browser, self.TIME_TO_WAIT).until(
            EC.element_to_be_clickable((By.ID, "save"))
        )
        clicar_seguro(browser, element_save)  # salvar
        self.verificar_feedback_plataforma(
            browser,
            error_report,
            etapa="cadastro_contrato",
        )

    def login_crea(self, browser, login, senha) -> None:
        try:
            logout_button = browser.find_element(By.ID, "logout_button")
            print("Online!")
        except NoSuchElementException:
            print("Offline, prosseguindo com o login!")

            browser.get(self.URL_LOGIN_CREA)

            cpf_input = WebDriverWait(browser, self.TIME_TO_WAIT).until(
                EC.presence_of_element_located((By.ID, "login"))
            )
            senha_input = WebDriverWait(browser, self.TIME_TO_WAIT).until(
                EC.presence_of_element_located((By.ID, "senha"))
            )
            login_button = WebDriverWait(browser, self.TIME_TO_WAIT).until(
                EC.element_to_be_clickable((By.ID, "enviar"))
            )

            preencher_seguro(browser, cpf_input, login)
            preencher_seguro(browser, senha_input, senha)
            clicar_seguro(browser, login_button)

            WebDriverWait(browser, self.TIME_TO_WAIT).until(
                EC.presence_of_element_located((By.ID, "logout_button"))
            )
