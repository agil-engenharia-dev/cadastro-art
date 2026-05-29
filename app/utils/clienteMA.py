from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import time
from app.utils.cliente import Cliente
from app.utils.art_cep import fluxo_modal_cep, fluxo_cep_contrato
from app.utils.error_report import ErrorReport
from selenium.common.exceptions import NoSuchElementException, TimeoutException


class ClienteMA(Cliente):
    NIVEL_ATIVIDADE_PADRAO = "16 - Execução"
    ATIVIDADE_PROFISSIONAL_PADRAO = "55 - Execução de serviço técnico"

    def __init__(self, args):
        super().__init__(*args)
        self.URL_LOGIN_CREA = "https://servicos-crea-ma.sitac.com.br//index.php"
        self.URL_ART = (
            "https://servicos-crea-ma.sitac.com.br/app/view/sight/ini?form=Art&id="
        )

    def _selecionar_opcao_por_titulo(
        self, browser, titulo, padrao, element_id, descricao_campo
    ):
        titulo = (titulo or padrao).strip()
        element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
            EC.presence_of_element_located((By.ID, element_id))
        )
        select = Select(element_select)
        for option in select.options:
            valor = option.get_attribute("value")
            if not valor:
                continue
            opt_title = (option.get_attribute("title") or "").strip()
            opt_text = (option.text or "").strip()
            if opt_title == titulo or opt_text == titulo:
                select.select_by_value(valor)
                return
        raise ValueError(
            f"{descricao_campo} '{titulo}' não encontrado em {element_id}. "
            f"Use o texto da opção (ex: {padrao})."
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

        element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
            EC.presence_of_element_located((By.ID, f"cadastrarContratoArt{numero_art}"))
        )
        element_select.click()

        time.sleep(5)

        try:
            popup_fechar = WebDriverWait(browser, 2).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(text(),'Nunca')]")
                )
            )
            popup_fechar.click()
        except:
            pass

        time.sleep(2)
        try:
            element_select = WebDriverWait(browser, 5).until(
                EC.presence_of_element_located((By.ID, "ACAOINSTITUCIONAL"))
            )
            select = Select(element_select)
            select.select_by_value("11")  # outros
        except:
            pass

        try:
            self._selecionar_nivel_atividade(browser, nivel_atividade)
        except:
            element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
                EC.presence_of_element_located((By.ID, "NOVA_ATIVIDADE"))
            )
            element_select.click()

        time.sleep(1)

        self._selecionar_nivel_atividade(browser, nivel_atividade)

        time.sleep(2)

        self._selecionar_atividade_profissional(browser, atividade_profissional)

        # 1. Clica no botão para abrir o modal
        element_button = WebDriverWait(browser, self.TIME_TO_WAIT).until(
            EC.element_to_be_clickable((By.ID, "ESCOLHERATUACAO"))
        )
        element_button.click()
        time.sleep(2)

        browser.switch_to.window(browser.window_handles[-1])

        # 2. Espera o botão 'Mostrar todos' e clica normalmente
        mostrar_todos = WebDriverWait(browser, 20).until(
            EC.element_to_be_clickable((By.ID, "exibirTodos"))
        )
        browser.execute_script("arguments[0].scrollIntoView();", mostrar_todos)
        browser.execute_script("arguments[0].click();", mostrar_todos)
        time.sleep(2)

        # 4. Navega na árvore para selecionar o item desejado
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

            browser.switch_to.window(browser.window_handles[0])
        except Exception as e:
            print(f"Erro ao navegar na árvore: {e}")
            raise

        element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
            EC.presence_of_element_located((By.ID, "UNIDADEMEDIDA00"))
        )
        select = Select(element_select)
        select.select_by_value("79")  # unidade de medida

        element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
            EC.presence_of_element_located((By.ID, "QUANTIDADE00"))
        )
        element_select.clear()
        element_select.send_keys("1,00")  # quantidade

        element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
            EC.presence_of_element_located((By.ID, "contratante0_ContratantePF"))
        )
        element_select.click()  # contratante

        element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
            EC.presence_of_element_located((By.ID, "contratante0_CampoContratantePF"))
        )
        element_select.clear()
        element_select.send_keys(self.cpf)  # cpf

        # Aguarda o overlay desaparecer antes de clicar
        WebDriverWait(browser, 10).until(
            EC.invisibility_of_element_located((By.ID, "ajax-overlay"))
        )

        element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
            EC.presence_of_element_located((By.ID, "session_timeout_container"))
        )
        element_select.click()

        try:
            element_select = WebDriverWait(browser, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a.botao_adicionar"))
            )
            element_select.click()  # cadastrar contratante
            browser.switch_to.window(browser.window_handles[-1])
            browser.maximize_window()

            element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
                EC.presence_of_element_located((By.ID, "NOME"))
            )
            element_select.clear()
            element_select.send_keys(self.nome)  # nome

            element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
                EC.presence_of_element_located((By.ID, "CEP"))
            )

            def _click_validar_cep_modal():
                btn = WebDriverWait(browser, self.TIME_TO_WAIT).until(
                    EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, "a.botao_ajaxform_adicionar")
                    )
                )
                btn.click()

            fluxo_modal_cep(
                browser,
                element_select,
                self,
                _click_validar_cep_modal,
                self.TIME_TO_WAIT,
            )
            time.sleep(5)

            element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
                EC.presence_of_element_located((By.ID, "TIPOLOGRADOURO"))
            )
            select = Select(element_select)
            select.select_by_value(self.tipo_de_logradouro)  # tipo_de_logradouro

            element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
                EC.presence_of_element_located((By.ID, "LOGRADOURO"))
            )
            element_select.clear()
            element_select.send_keys(self.logradouro)  # logradouro

            element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
                EC.presence_of_element_located((By.ID, "ENDERECO_NUMERO"))
            )
            element_select.clear()
            element_select.send_keys(self.numero)  # numero

            element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
                EC.presence_of_element_located((By.ID, "BAIRRO"))
            )
            element_select.clear()
            element_select.send_keys(self.bairro)  # bairro

            element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
                EC.presence_of_element_located((By.ID, "save"))
            )
            element_select.click()

            browser.switch_to.window(browser.window_handles[0])

            if error_report is not None:

                # Verifica se o botão cadastrar contratante ainda está visível na tela do CPF
                try:
                    WebDriverWait(browser, 5).until(
                        EC.presence_of_element_located(
                            (By.ID, "contratante0_CampoContratantePF")
                        )
                    )
                    time.sleep(2)

                    btns = browser.find_elements(By.CSS_SELECTOR, "a.botao_adicionar")

                    for b in btns:
                        try:
                            if b.is_displayed():
                                error_report.add(
                                    row_data=getattr(self, "_row_data", {}),
                                    etapa="cadastro_endereco_contratante",
                                    motivo=(
                                        "Após o fluxo de endereço no modal do contratante, o botão "
                                        "cadastrar contratante (a.botao_adicionar) ainda está visível "
                                        "na tela do CPF — cadastro do contratante possivelmente incompleto no endereço."
                                    ),
                                    contexto={
                                        "cliente_nome": getattr(self, "nome", ""),
                                        "cpf": getattr(self, "cpf", ""),
                                    },
                                )
                                break
                        except Exception:
                            continue
                except Exception:
                    pass
        except:
            pass

        time.sleep(5)

        # Clica no botão de coordenadas para abrir o mapa
        try:
            btn_coordenadas = WebDriverWait(browser, 5).until(
                EC.element_to_be_clickable((By.ID, "ESCOLHERCORDENADASGMAP"))
            )
            btn_coordenadas.click()
            time.sleep(5)  # Aguarda o mapa abrir

            # Fecha a janela do mapa para capturar as coordenadas automaticamente
            if len(browser.window_handles) > 1:
                browser.switch_to.window(browser.window_handles[-1])
                browser.close()
                browser.switch_to.window(browser.window_handles[0])
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
            EC.presence_of_element_located((By.ID, "CONTRATO_VALOR0"))
        )
        element_select.clear()
        element_select.send_keys(self.valor_do_plano)  # data
        element_select.send_keys(Keys.TAB, Keys.ARROW_UP)

        element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
            EC.presence_of_element_located((By.ID, "CONTRATO_DATA0"))
        )
        element_select.clear()
        element_select.send_keys(self.data)  # data inicio

        element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
            EC.presence_of_element_located((By.ID, "CONTRATO_DATAINICIO0"))
        )
        element_select.clear()
        element_select.send_keys(self.data)  # data inicio

        element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
            EC.presence_of_element_located((By.ID, "CONTRATO_DATAFIM0"))
        )
        element_select.clear()
        element_select.send_keys(self.data)  # data fim

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
            select = Select(element_select)
            select.select_by_value(self.tipo_de_logradouro)  # tipo_de_logradouro

            element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
                EC.presence_of_element_located((By.ID, "CONTRATO_ENDERECO_LOGRADOURO0"))
            )
            element_select.clear()
            element_select.send_keys(self.logradouro)  # logradouro

            element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
                EC.presence_of_element_located((By.ID, "CONTRATO_ENDERECO_NUMERO0"))
            )
            element_select.clear()
            element_select.send_keys(self.numero)  # numero

            element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
                EC.presence_of_element_located((By.ID, "CONTRATO_ENDERECO_BAIRRO0"))
            )
            element_select.clear()
            element_select.send_keys(self.bairro)  # bairro

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
            try:
                Select(candidate).select_by_value("11")
            except Exception:
                try:
                    browser.execute_script(
                        "arguments[0].value='11'; arguments[0].dispatchEvent(new Event('change',{bubbles:true}));",
                        candidate,
                    )
                except Exception:
                    pass
        except Exception:
            # fallback geral: tenta localizar qualquer select ACAOINSTITUCIONAL e setar value=11
            try:
                acao_select = WebDriverWait(browser, 2).until(
                    EC.presence_of_element_located((By.ID, "ACAOINSTITUCIONAL"))
                )
                try:
                    Select(acao_select).select_by_value("11")
                except Exception:
                    try:
                        browser.execute_script(
                            "arguments[0].value='11'; arguments[0].dispatchEvent(new Event('change',{bubbles:true}));",
                            acao_select,
                        )
                    except Exception:
                        pass
            except Exception:
                pass

        # espera o overlay desaparecer antes de clicar em salvar
        WebDriverWait(browser, 10).until(
            EC.invisibility_of_element_located((By.ID, "ajax-overlay"))
        )

        element_save.click()  # salvar
        time.sleep(10)

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
                EC.presence_of_element_located((By.ID, "enviar"))
            )

            cpf_input.send_keys(login)
            senha_input.send_keys(senha)
            login_button.click()

            WebDriverWait(browser, self.TIME_TO_WAIT).until(
                EC.presence_of_element_located((By.ID, "logout_button"))
            )
