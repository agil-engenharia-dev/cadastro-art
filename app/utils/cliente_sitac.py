"""
Base para clientes em portais SITAC (CREA-MA, CREA-CE, CFT/sinceti).

Centraliza validação PF/PJ (CPF ou CNPJ, sexo/tipo) e o fluxo Selenium de cadastro
de contratante no formulário de ART.
"""

from __future__ import annotations

import time

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait

from app.utils.art_cep import aguardar_overlay_invisivel, fluxo_modal_cep
from app.utils.browser_windows import janela_auxiliar, voltar_janela_principal
from app.utils.cliente import Cliente
from app.utils.error_report import ErrorReport
from app.utils.selenium_actions import (
    clicar_seguro,
    preencher_seguro,
    selecionar_por_valor_seguro,
)
from app.utils.validation import (
    eh_pessoa_juridica,
    extrair_digitos_documento,
    validarBairro,
    validarCep,
    validarCidade,
    validarCnpj,
    validarDataDoContrato,
    validarLogradouro,
    validarNome,
    validarNumero,
    validarSexoPorDocumento,
    validarTipoDeLogradouro,
    validarUf,
    validarValorDoPlano,
)

IDS_RAZAO_SOCIAL = ("RAZAOSOCIAL", "RAZAO_SOCIAL", "RAZAO SOCIAL")
IDS_NOME_FANTASIA = ("NOMEFANTASIA", "NOME_FANTASIA", "NOME FANTASIA")
IDS_SESSION_TIMEOUT = ("session_timeout_container", "session_timeout_clock")

SEL_AVISO_ERRO_TITULO = ".aviso_acao_erro_titulo"
SEL_AVISO_ERRO_MENSAGEM = ".aviso_acao_erro_mensagem"
SEL_AVISO_SUCESSO_TITULO = ".aviso_acao_sucesso_titulo"
SEL_AVISO_SUCESSO_MENSAGEM = ".aviso_acao_sucesso_mensagem"


class FeedbackPlataformaErro(Exception):
    """A plataforma SITAC exibiu modal de ERRO após uma ação (salvar contrato/contratante)."""

    def __init__(self, mensagem: str):
        self.mensagem = mensagem
        super().__init__(mensagem)


def _extrair_mensagem_aviso(element) -> str:
    texto = (element.text or "").strip()
    try:
        for redir in element.find_elements(By.CSS_SELECTOR, ".aviso_acao_redireciona"):
            parte = (redir.text or "").strip()
            if parte and parte in texto:
                texto = texto.replace(parte, "", 1).strip()
    except Exception:
        pass
    return texto


def _elemento_aviso_visivel(browser, seletor: str):
    for el in browser.find_elements(By.CSS_SELECTOR, seletor):
        try:
            if el.is_displayed():
                return el
        except Exception:
            continue
    return None


def aguardar_feedback_plataforma(browser, timeout: float = 20) -> dict | None:
    """
    Aguarda o modal de feedback da plataforma (sucesso ou erro) após salvar.
    Retorna {'tipo': 'erro'|'sucesso', 'mensagem': str} ou None se não aparecer.
    """
    def _modal_visivel(driver):
        if _elemento_aviso_visivel(driver, SEL_AVISO_ERRO_TITULO):
            return True
        if _elemento_aviso_visivel(driver, SEL_AVISO_SUCESSO_TITULO):
            return True
        return False

    try:
        WebDriverWait(browser, timeout).until(_modal_visivel)
    except TimeoutException:
        return None

    titulo_erro = _elemento_aviso_visivel(browser, SEL_AVISO_ERRO_TITULO)
    if titulo_erro is not None:
        msg_el = browser.find_elements(By.CSS_SELECTOR, SEL_AVISO_ERRO_MENSAGEM)
        mensagem = ""
        for el in msg_el:
            try:
                if el.is_displayed():
                    mensagem = _extrair_mensagem_aviso(el)
                    break
            except Exception:
                continue
        if not mensagem:
            mensagem = (titulo_erro.text or "ERRO").strip()
        return {"tipo": "erro", "mensagem": mensagem}

    titulo_ok = _elemento_aviso_visivel(browser, SEL_AVISO_SUCESSO_TITULO)
    if titulo_ok is not None:
        mensagem = ""
        for el in browser.find_elements(By.CSS_SELECTOR, SEL_AVISO_SUCESSO_MENSAGEM):
            try:
                if el.is_displayed():
                    mensagem = _extrair_mensagem_aviso(el)
                    break
            except Exception:
                continue
        if not mensagem:
            mensagem = (titulo_ok.text or "Sucesso").strip()
        return {"tipo": "sucesso", "mensagem": mensagem}

    return None


class ClienteSitac(Cliente):
    """Cliente com suporte a contratante PF (CPF) e PJ (CNPJ) em formulários SITAC."""

    SUPORTA_CNPJ = True

    def __init__(self, args):
        self._sucesso_confirmado = False
        dados = list(args)
        self.is_pj = eh_pessoa_juridica(dados[1])

        if self.is_pj:
            self._inicializar_pessoa_juridica(dados)
        else:
            super().__init__(*dados)

    def _inicializar_pessoa_juridica(self, dados: list) -> None:
        self.nome = validarNome(dados[0])
        self.cpf = validarCnpj(dados[1])
        self.sexo = validarSexoPorDocumento(dados[2], dados[1])
        self.cep = validarCep(dados[3])
        self.tipo_de_logradouro = validarTipoDeLogradouro(dados[4])
        self.data = validarDataDoContrato(dados[5])
        self.logradouro = validarLogradouro(dados[6])
        self.numero = validarNumero(dados[7])
        self.bairro = validarBairro(dados[8])
        self.cidade = validarCidade(dados[9])
        self.uf = validarUf(dados[10])
        self.valor_do_plano = validarValorDoPlano(dados[11])
        self.TIME_TO_WAIT = 60

    @property
    def documento_digitos(self) -> str:
        return extrair_digitos_documento(self.cpf)

    def _preencher_campos_extras_modal_pf(self, browser) -> None:
        """Gancho para campos adicionais no modal PF (ex.: SEXO no CFT)."""

    def _preencher_campos_extras_modal_pj(self, browser) -> None:
        """Gancho para campos adicionais no modal PJ após razão social / fantasia."""

    def _preencher_campo_por_ids(self, browser, ids: tuple[str, ...], valor: str) -> None:
        for element_id in ids:
            try:
                element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
                    EC.presence_of_element_located((By.ID, element_id))
                )
                preencher_seguro(browser, element_select, valor)
                return
            except TimeoutException:
                continue
        raise ValueError(f"Campo não encontrado (ids tentados: {', '.join(ids)}).")

    def _selecionar_tipo_contratante_privado(self, browser) -> None:
        for element_id in ("TIPOCONTRATANTE", "TIPO", "TIPO_EMPRESA", "SEXO"):
            try:
                element_select = browser.find_element(By.ID, element_id)
                select = Select(element_select)
                for option in select.options:
                    texto = (option.text or "").strip().upper()
                    valor = (option.get_attribute("value") or "").strip().upper()
                    if "PRIVADO" in texto or valor in ("P", "2", "PRIVADO"):
                        selecionar_por_valor_seguro(
                            browser, element_select, option.get_attribute("value")
                        )
                        return
            except NoSuchElementException:
                continue

    def _dismiss_session_timeout(self, browser) -> None:
        for element_id in IDS_SESSION_TIMEOUT:
            try:
                element_select = browser.find_element(By.ID, element_id)
                if element_select.is_displayed():
                    clicar_seguro(browser, element_select)
                    return
            except Exception:
                continue

    def verificar_feedback_plataforma(
        self,
        browser,
        error_report: ErrorReport | None = None,
        *,
        etapa: str,
        timeout: float = 20,
    ) -> None:
        """
        Aguarda o modal de feedback do SITAC.

        Regras:
        - Se aparecer sucesso: marca `_sucesso_confirmado=True` e segue.
        - Se aparecer erro: registra no relatório e levanta FeedbackPlataformaErro.
        - Se não aparecer modal nenhum: registra como erro e levanta FeedbackPlataformaErro.
        """
        feedback = aguardar_feedback_plataforma(browser, timeout=timeout)
        if feedback is None:
            motivo = (
                "Nenhum modal de feedback (sucesso/erro) foi exibido pela plataforma "
                "após salvar. Não é possível confirmar o sucesso do cadastro."
            )
            print(f"\033[33mPlataforma (ALERTA - SEM MODAL): {motivo}\033[0m")
            if error_report is not None:
                error_report.add(
                    row_data=getattr(self, "_row_data", {}),
                    etapa=etapa,
                    motivo=motivo,
                    contexto={
                        "cliente_nome": getattr(self, "nome", ""),
                        "cpf": getattr(self, "cpf", ""),
                        "is_pj": self.is_pj,
                        "feedback_plataforma": None,
                    },
                )
                try:
                    self._erro_registrado = True
                except Exception:
                    pass
            raise FeedbackPlataformaErro(motivo)
        if feedback["tipo"] == "sucesso":
            self._sucesso_confirmado = True
            print(
                f"\033[32mPlataforma: {feedback.get('mensagem') or 'cadastro confirmado'}\033[0m"
            )
            return

        motivo = feedback.get("mensagem") or "Erro retornado pela plataforma (sem mensagem)."
        print(f"\033[31mPlataforma (ERRO): {motivo}\033[0m")

        if error_report is not None:
            error_report.add(
                row_data=getattr(self, "_row_data", {}),
                etapa=etapa,
                motivo=motivo,
                contexto={
                    "cliente_nome": getattr(self, "nome", ""),
                    "cpf": getattr(self, "cpf", ""),
                    "is_pj": self.is_pj,
                    "feedback_plataforma": feedback,
                },
            )
            try:
                self._erro_registrado = True
            except Exception:
                pass

        raise FeedbackPlataformaErro(motivo)

    def cadastrar_contratante(
        self, browser, error_report: ErrorReport | None = None
    ) -> None:
        if self.is_pj:
            self._cadastrar_contratante_pj(browser, error_report)
        else:
            self._cadastrar_contratante_pf(browser, error_report)

    def _cadastrar_contratante_pf(
        self, browser, error_report: ErrorReport | None = None
    ) -> None:
        aguardar_overlay_invisivel(browser)
        element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
            EC.element_to_be_clickable((By.ID, "contratante0_ContratantePF"))
        )
        clicar_seguro(browser, element_select)

        element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
            EC.element_to_be_clickable((By.ID, "contratante0_CampoContratantePF"))
        )
        preencher_seguro(browser, element_select, self.documento_digitos)

        aguardar_overlay_invisivel(browser)
        self._dismiss_session_timeout(browser)

        def _abrir_modal():
            btn = WebDriverWait(browser, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a.botao_adicionar"))
            )
            clicar_seguro(browser, btn)

        try:
            with janela_auxiliar(browser, _abrir_modal) as entrou_popup:
                if not entrou_popup:
                    return

                element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
                    EC.presence_of_element_located((By.ID, "NOME"))
                )
                preencher_seguro(browser, element_select, self.nome)
                self._preencher_campos_extras_modal_pf(browser)

                self._preencher_endereco_modal_contratante(browser, error_report)
        except FeedbackPlataformaErro:
            voltar_janela_principal(browser)
            raise
        except Exception:
            pass

        if error_report is not None:
            self._verificar_cadastro_contratante_incompleto(
                browser,
                error_report,
                campo_documento_id="contratante0_CampoContratantePF",
                tipo_documento="CPF",
            )

    def _cadastrar_contratante_pj(
        self, browser, error_report: ErrorReport | None = None
    ) -> None:
        aguardar_overlay_invisivel(browser)
        element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
            EC.element_to_be_clickable((By.ID, "contratante0_ContratantePJ"))
        )
        clicar_seguro(browser, element_select)

        element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
            EC.element_to_be_clickable((By.ID, "contratante0_CampoContratantePJ"))
        )
        preencher_seguro(browser, element_select, self.documento_digitos)

        aguardar_overlay_invisivel(browser)
        self._dismiss_session_timeout(browser)

        def _abrir_modal():
            btn = WebDriverWait(browser, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a.botao_adicionar"))
            )
            clicar_seguro(browser, btn)

        try:
            with janela_auxiliar(browser, _abrir_modal) as entrou_popup:
                if not entrou_popup:
                    return

                self._preencher_campo_por_ids(browser, IDS_RAZAO_SOCIAL, self.nome)
                self._preencher_campo_por_ids(browser, IDS_NOME_FANTASIA, self.nome)
                self._selecionar_tipo_contratante_privado(browser)
                self._preencher_campos_extras_modal_pj(browser)

                self._preencher_endereco_modal_contratante(browser, error_report)
        except FeedbackPlataformaErro:
            voltar_janela_principal(browser)
            raise
        except Exception:
            pass

        if error_report is not None:
            self._verificar_cadastro_contratante_incompleto(
                browser,
                error_report,
                campo_documento_id="contratante0_CampoContratantePJ",
                tipo_documento="CNPJ",
            )

    def _preencher_endereco_modal_contratante(
        self, browser, error_report: ErrorReport | None = None
    ) -> None:
        element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
            EC.presence_of_element_located((By.ID, "CEP"))
        )

        def _click_validar_cep_modal():
            btn = WebDriverWait(browser, self.TIME_TO_WAIT).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "a.botao_ajaxform_adicionar")
                )
            )
            clicar_seguro(browser, btn)

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
        selecionar_por_valor_seguro(browser, element_select, self.tipo_de_logradouro)

        element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
            EC.element_to_be_clickable((By.ID, "LOGRADOURO"))
        )
        preencher_seguro(browser, element_select, self.logradouro)

        element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
            EC.element_to_be_clickable((By.ID, "ENDERECO_NUMERO"))
        )
        preencher_seguro(browser, element_select, self.numero)

        element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
            EC.element_to_be_clickable((By.ID, "BAIRRO"))
        )
        preencher_seguro(browser, element_select, self.bairro)

        element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
            EC.element_to_be_clickable((By.ID, "save"))
        )
        clicar_seguro(browser, element_select)
        self.verificar_feedback_plataforma(
            browser,
            error_report,
            etapa="cadastro_contratante",
            timeout=15,
        )

    def _verificar_cadastro_contratante_incompleto(
        self,
        browser,
        error_report: ErrorReport,
        campo_documento_id: str,
        tipo_documento: str,
    ) -> None:
        try:
            WebDriverWait(browser, 5).until(
                EC.presence_of_element_located((By.ID, campo_documento_id))
            )
            time.sleep(2)

            for btn in browser.find_elements(By.CSS_SELECTOR, "a.botao_adicionar"):
                try:
                    if btn.is_displayed():
                        error_report.add(
                            row_data=getattr(self, "_row_data", {}),
                            etapa="cadastro_endereco_contratante",
                            motivo=(
                                "Após o fluxo de endereço no modal do contratante, o botão "
                                "cadastrar contratante (a.botao_adicionar) ainda está visível "
                                f"na tela do {tipo_documento} — cadastro do contratante "
                                "possivelmente incompleto no endereço."
                            ),
                            contexto={
                                "cliente_nome": getattr(self, "nome", ""),
                                "cpf": getattr(self, "cpf", ""),
                                "is_pj": self.is_pj,
                            },
                        )
                        break
                except Exception:
                    continue
        except Exception:
            pass
