"""
Detecção de erro de CEP na ART (SITAC) e correção via ViaCEP.

Modo padrão: só consulta ViaCEP após a mensagem em #Result_cep.
Alternativa: CADASTRO_ART_VIACEP_MODE=before_fill (ou alterar VIACEP_MODE abaixo).
Se o CEP da planilha não existir na base da ART, tenta outros CEPs do ViaCEP,
depois um CEP genérico da cidade e, por fim, seleção manual da cidade no modal.
Com CEP genérico, os demais campos são repostos com os dados da planilha.
"""

from __future__ import annotations

import os
import time
import unicodedata
from typing import Callable

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from app.utils.selenium_actions import preencher_seguro, selecionar_por_valor_seguro
from app.utils.viacep import (
    buscar_cep_generico_cidade,
    buscar_cep_por_endereco,
    listar_ceps_por_endereco,
)

# "on_cep_error" | "before_fill"
VIACEP_MODE = os.environ.get("CADASTRO_ART_VIACEP_MODE", "on_cep_error")

CEP_ERROR_SELECTORS = [
    (By.CSS_SELECTOR, "#Result_cep .aviso_ajaxresquest_erro"),
    (By.CSS_SELECTOR, "#Result_cep div[class*='aviso_ajax']"),
]


def normalize_cep_digits(cep: str | None) -> str:
    return "".join(filter(str.isdigit, str(cep or "")))


def mensagem_indica_cep_nao_localizado(text: str | None) -> bool:
    t = (text or "").lower()
    if "cep" in t and "localiz" in t:
        return True
    return "não foi localizado" in t or "nao foi localizado" in t


def cep_generico_municipio(cep: str | None) -> str | None:
    """CEP genérico do município: cinco primeiros dígitos + 000."""
    digits = normalize_cep_digits(cep)
    if len(digits) != 8:
        return None
    generico = digits[:5] + "000"
    return generico if generico != digits else None


def _normalizar_texto_cmp(s: str | None) -> str:
    t = unicodedata.normalize("NFD", (s or "").strip().lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn")


def _parse_rotulo_cidade_uf(texto: str) -> tuple[str, str] | None:
    t = (texto or "").strip()
    if " - " not in t:
        return None
    cidade_parte, uf_parte = t.rsplit(" - ", 1)
    uf = uf_parte.strip().upper()
    if len(uf) != 2:
        return None
    return cidade_parte.strip(), uf


def pode_buscar_viacep(cliente) -> bool:
    uf = (getattr(cliente, "uf", None) or "").strip()
    cidade = (getattr(cliente, "cidade", None) or "").strip()
    logr = (getattr(cliente, "logradouro", None) or "").strip()
    return len(uf) == 2 and len(cidade) >= 3 and len(logr) >= 3


def pode_buscar_cep_generico(cliente) -> bool:
    uf = (getattr(cliente, "uf", None) or "").strip()
    cidade = (getattr(cliente, "cidade", None) or "").strip()
    return len(uf) == 2 and len(cidade) >= 3


def aguardar_overlay_invisivel(browser: WebDriver, timeout: int = 15) -> None:
    try:
        WebDriverWait(browser, timeout).until(
            EC.invisibility_of_element_located((By.ID, "ajax-overlay"))
        )
    except Exception:
        pass


def _rotulo_select2_item(li: WebElement) -> str:
    for sel in (".select2-user-result", ".select2-result-label"):
        try:
            return (li.find_element(By.CSS_SELECTOR, sel).text or "").strip()
        except Exception:
            continue
    return (li.text or "").strip()


def _clicar_item_select2(browser: WebDriver, alvo: WebElement) -> bool:
    try:
        browser.execute_script("arguments[0].scrollIntoView({block:'center'});", alvo)
        alvo.click()
        return True
    except Exception:
        try:
            browser.execute_script("arguments[0].click();", alvo)
            return True
        except Exception:
            return False


def _selecionar_select2_modal(
    browser: WebDriver,
    container_id: str,
    termo_busca: str,
    item_confere: Callable[[str], bool],
    timeout: int = 20,
) -> bool:
    if not browser.find_elements(By.ID, container_id):
        return False

    aguardar_overlay_invisivel(browser, 10)
    try:
        container = WebDriverWait(browser, timeout).until(
            EC.element_to_be_clickable((By.ID, container_id))
        )
        browser.execute_script("arguments[0].scrollIntoView({block:'center'});", container)
        container.click()
    except Exception:
        return False

    try:
        search = WebDriverWait(browser, timeout).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "#select2-drop input.select2-input")
            )
        )
        search.clear()
        search.send_keys(termo_busca or "")
    except Exception:
        return False

    time.sleep(2)

    try:
        itens = browser.find_elements(
            By.CSS_SELECTOR,
            "#select2-drop ul.select2-results li.select2-result-selectable",
        )
    except Exception:
        return False

    for li in itens:
        if item_confere(_rotulo_select2_item(li)):
            if _clicar_item_select2(browser, li):
                aguardar_overlay_invisivel(browser, 10)
                return True
            return False
    return False


def _selecionar_uf_select2(
    browser: WebDriver,
    cliente,
    container_ids: tuple[str, ...],
    timeout: int = 20,
) -> bool:
    uf_cli = (getattr(cliente, "uf", None) or "").strip().upper()
    if len(uf_cli) != 2:
        return False

    def _confere(rotulo: str) -> bool:
        rotulo_cmp = rotulo.strip().upper()
        if rotulo_cmp == uf_cli:
            return True
        parsed = _parse_rotulo_cidade_uf(rotulo)
        return parsed is not None and parsed[1].upper() == uf_cli

    for container_id in container_ids:
        if _selecionar_select2_modal(browser, container_id, uf_cli, _confere, timeout):
            return True
    return False


def selecionar_uf_select2_modal_cep(browser: WebDriver, cliente, timeout: int = 20) -> bool:
    """Seleciona a UF no Select2 quando o campo existir no formulário."""
    return _selecionar_uf_select2(browser, cliente, ("s2id_UF",), timeout)


def selecionar_cidade_select2_modal_cep(browser: WebDriver, cliente, timeout: int = 20) -> bool:
    """
    Abre o Select2 #s2id_CIDADE, pesquisa pela cidade do cliente e seleciona
    o item que coincide com cidade e UF (sem acentos, case insensitive).
    """
    cidade_cli = _normalizar_texto_cmp(getattr(cliente, "cidade", None))
    uf_cli = _normalizar_texto_cmp(getattr(cliente, "uf", None))
    if len(cidade_cli) < 3 or len(uf_cli) != 2:
        return False

    def _confere(rotulo: str) -> bool:
        parsed = _parse_rotulo_cidade_uf(rotulo)
        if not parsed:
            return False
        c_p, u_p = parsed
        return (
            _normalizar_texto_cmp(c_p) == cidade_cli
            and _normalizar_texto_cmp(u_p) == uf_cli
        )

    return _selecionar_select2_modal(
        browser,
        "s2id_CIDADE",
        getattr(cliente, "cidade", "") or "",
        _confere,
        timeout,
    )


def _elemento_erro_cep_visivel(browser: WebDriver) -> bool:
    for by, sel in CEP_ERROR_SELECTORS:
        try:
            el = browser.find_element(by, sel)
            if not el.is_displayed():
                continue
            if mensagem_indica_cep_nao_localizado(el.text):
                return True
        except Exception:
            continue
    return False


def art_cep_nao_localizado(browser: WebDriver, timeout: float = 12) -> bool:
    """True se a ART exibir o aviso de CEP não localizado dentro do timeout."""
    end = time.time() + timeout
    while time.time() < end:
        if _elemento_erro_cep_visivel(browser):
            return True
        time.sleep(0.25)
    return False


def _buscar_viacep_cliente(cliente) -> str | None:
    if not pode_buscar_viacep(cliente):
        return None
    return buscar_cep_por_endereco(
        cliente.uf,
        cliente.cidade,
        cliente.logradouro,
        getattr(cliente, "bairro", None),
    )


def _listar_ceps_viacep_cliente(cliente) -> list[str]:
    if not pode_buscar_viacep(cliente):
        return []
    return listar_ceps_por_endereco(
        cliente.uf,
        cliente.cidade,
        cliente.logradouro,
        getattr(cliente, "bairro", None),
    )


def _buscar_cep_generico_cliente(cliente) -> str | None:
    generico = cep_generico_municipio(getattr(cliente, "cep", None))
    if generico:
        return generico
    if not pode_buscar_cep_generico(cliente):
        return None
    return buscar_cep_generico_cidade(cliente.uf, cliente.cidade)


def _preencher_e_validar_cep(
    cep_el: WebElement,
    cep: str,
    validar: Callable[[], None],
) -> None:
    cep_el.clear()
    cep_el.send_keys(cep)
    validar()
    time.sleep(0.5)


def _preencher_campo_texto_se_editavel(
    browser: WebDriver, by: By, selector: str, valor: str | None
) -> None:
    texto = (valor or "").strip()
    if not texto:
        return
    try:
        el = browser.find_element(by, selector)
        if el.is_displayed() and el.is_enabled():
            preencher_seguro(browser, el, texto)
    except Exception:
        pass


def _preencher_texto_por_ids(
    browser: WebDriver, ids: tuple[str, ...], valor: str | None
) -> None:
    for element_id in ids:
        _preencher_campo_texto_se_editavel(browser, By.ID, element_id, valor)


def _preencher_select_se_existir(
    browser: WebDriver, by: By, selector: str, valor: str | None
) -> None:
    val = (valor or "").strip()
    if not val:
        return
    try:
        el = browser.find_element(by, selector)
        if el.is_displayed() and el.is_enabled():
            selecionar_por_valor_seguro(browser, el, val)
    except Exception:
        pass


def _preencher_select_por_ids(
    browser: WebDriver, ids: tuple[str, ...], valor: str | None
) -> None:
    for element_id in ids:
        _preencher_select_se_existir(browser, By.ID, element_id, valor)


def _selecionar_cidade_select2_contrato(browser: WebDriver, cliente, timeout: int = 15) -> bool:
    cidade_cli = _normalizar_texto_cmp(getattr(cliente, "cidade", None))
    uf_cli = _normalizar_texto_cmp(getattr(cliente, "uf", None))
    if len(cidade_cli) < 3 or len(uf_cli) != 2:
        return False

    def _confere(rotulo: str) -> bool:
        parsed = _parse_rotulo_cidade_uf(rotulo)
        if not parsed:
            return False
        c_p, u_p = parsed
        return (
            _normalizar_texto_cmp(c_p) == cidade_cli
            and _normalizar_texto_cmp(u_p) == uf_cli
        )

    for container_id in ("s2id_CONTRATO_ENDERECO_CIDADE0", "s2id_CIDADE"):
        if _selecionar_select2_modal(
            browser,
            container_id,
            getattr(cliente, "cidade", "") or "",
            _confere,
            timeout,
        ):
            return True
    return False


def restaurar_endereco_planilha_modal(browser: WebDriver, cliente) -> None:
    """Sobrescreve autopreenchimento do SITAC com os dados da planilha."""
    _preencher_select_por_ids(browser, ("UF",), getattr(cliente, "uf", None))
    selecionar_uf_select2_modal_cep(browser, cliente, timeout=15)
    selecionar_cidade_select2_modal_cep(browser, cliente, timeout=15)
    _preencher_texto_por_ids(browser, ("CIDADE",), getattr(cliente, "cidade", None))
    _preencher_select_por_ids(
        browser, ("TIPOLOGRADOURO",), getattr(cliente, "tipo_de_logradouro", None)
    )
    _preencher_texto_por_ids(browser, ("LOGRADOURO",), getattr(cliente, "logradouro", None))
    _preencher_texto_por_ids(
        browser,
        ("ENDERECO_NUMERO", "NUMERO"),
        getattr(cliente, "numero", None),
    )
    _preencher_texto_por_ids(browser, ("BAIRRO",), getattr(cliente, "bairro", None))
    _preencher_texto_por_ids(
        browser,
        ("COMPLEMENTO", "ENDERECO_COMPLEMENTO"),
        getattr(cliente, "complemento", None),
    )


def restaurar_endereco_planilha_contrato(browser: WebDriver, cliente) -> None:
    """Sobrescreve autopreenchimento do SITAC com os dados da planilha."""
    _preencher_select_por_ids(
        browser,
        ("CONTRATO_ENDERECO_UF0", "UF0"),
        getattr(cliente, "uf", None),
    )
    _selecionar_uf_select2(
        browser,
        cliente,
        ("s2id_CONTRATO_ENDERECO_UF0", "s2id_UF"),
        timeout=15,
    )
    _selecionar_cidade_select2_contrato(browser, cliente, timeout=15)
    _preencher_texto_por_ids(
        browser,
        ("CONTRATO_ENDERECO_CIDADE0", "CIDADE0"),
        getattr(cliente, "cidade", None),
    )
    _preencher_select_por_ids(
        browser,
        ("CONTRATO_ENDERECO_TIPOLOGRADOURO0",),
        getattr(cliente, "tipo_de_logradouro", None),
    )
    _preencher_texto_por_ids(
        browser, ("CONTRATO_ENDERECO_LOGRADOURO0",), getattr(cliente, "logradouro", None)
    )
    _preencher_texto_por_ids(
        browser, ("CONTRATO_ENDERECO_NUMERO0",), getattr(cliente, "numero", None)
    )
    _preencher_texto_por_ids(
        browser, ("CONTRATO_ENDERECO_BAIRRO0",), getattr(cliente, "bairro", None)
    )
    _preencher_texto_por_ids(
        browser,
        ("CONTRATO_ENDERECO_COMPLEMENTO0", "COMPLEMENTO0"),
        getattr(cliente, "complemento", None),
    )


def _tentar_ceps_em_sequencia(
    browser: WebDriver,
    cep_el: WebElement,
    ceps: list[str],
    validar: Callable[[], None],
    time_to_wait: int,
    timeout_erro: float,
) -> bool:
    atual = normalize_cep_digits(cep_el.get_attribute("value") or "")
    for cep in ceps:
        if cep == atual:
            continue
        _preencher_e_validar_cep(cep_el, cep, validar)
        aguardar_overlay_invisivel(browser, time_to_wait)
        if not art_cep_nao_localizado(browser, timeout=timeout_erro):
            return True
        atual = cep
    return False


def _corrigir_cep_apos_falha(
    browser: WebDriver,
    cep_el: WebElement,
    cliente,
    validar: Callable[[], None],
    time_to_wait: int,
    restaurar_planilha: Callable[[WebDriver], None],
    usar_select2_cidade: bool,
) -> None:
    atual = normalize_cep_digits(cep_el.get_attribute("value") or "")

    alternativos = [c for c in _listar_ceps_viacep_cliente(cliente) if c != atual]
    if _tentar_ceps_em_sequencia(
        browser,
        cep_el,
        alternativos,
        validar,
        time_to_wait,
        timeout_erro=10,
    ):
        return

    generico = _buscar_cep_generico_cliente(cliente)
    if generico and generico != normalize_cep_digits(cep_el.get_attribute("value") or ""):
        _preencher_e_validar_cep(cep_el, generico, validar)
        aguardar_overlay_invisivel(browser, time_to_wait)
        if not art_cep_nao_localizado(browser, timeout=10):
            restaurar_planilha(browser)
            return

    if not art_cep_nao_localizado(browser, timeout=4):
        return

    if usar_select2_cidade and selecionar_cidade_select2_modal_cep(
        browser, cliente, timeout=min(20, time_to_wait)
    ):
        validar()
        time.sleep(0.5)
        aguardar_overlay_invisivel(browser, time_to_wait)
        if not art_cep_nao_localizado(browser, timeout=10):
            restaurar_planilha(browser)


def aplicar_cep_generico_modal(
    browser: WebDriver,
    cep_el: WebElement,
    cliente,
    click_validar: Callable[[], None],
    time_to_wait: int = 60,
) -> bool:
    """
    Força CEP genérico no modal e repõe endereço com dados da planilha.
    Usado quando a validação ajax passa mas o salvamento rejeita o CEP.
    """
    generico = _buscar_cep_generico_cliente(cliente)
    if not generico:
        return False

    _preencher_e_validar_cep(cep_el, generico, click_validar)
    aguardar_overlay_invisivel(browser, time_to_wait)

    if art_cep_nao_localizado(browser, timeout=10):
        if not selecionar_cidade_select2_modal_cep(
            browser, cliente, timeout=min(20, time_to_wait)
        ):
            return False
        click_validar()
        time.sleep(0.5)
        aguardar_overlay_invisivel(browser, time_to_wait)
        if art_cep_nao_localizado(browser, timeout=10):
            return False

    restaurar_endereco_planilha_modal(browser, cliente)
    return True


def fluxo_modal_cep(
    browser: WebDriver,
    cep_el: WebElement,
    cliente,
    click_validar: Callable[[], None],
    time_to_wait: int = 60,
) -> None:
    """
    Preenche #CEP, dispara validação (botão ajax), corrige com ViaCEP se necessário.
    """
    aguardar_overlay_invisivel(browser, 10)
    plan = normalize_cep_digits(cliente.cep)
    first_from_viacep = False

    if VIACEP_MODE == "before_fill":
        v = _buscar_viacep_cliente(cliente)
        if v:
            primeiro = v
            first_from_viacep = True
        else:
            primeiro = plan
    else:
        primeiro = plan

    _preencher_e_validar_cep(cep_el, primeiro, click_validar)
    aguardar_overlay_invisivel(browser, time_to_wait)

    if not art_cep_nao_localizado(browser, timeout=12):
        return

    if first_from_viacep:
        _preencher_e_validar_cep(cep_el, plan, click_validar)
        aguardar_overlay_invisivel(browser, time_to_wait)
        if not art_cep_nao_localizado(browser, timeout=10):
            return

    v = _buscar_viacep_cliente(cliente)
    atual = normalize_cep_digits(cep_el.get_attribute("value") or "")
    if v and v != atual:
        _preencher_e_validar_cep(cep_el, v, click_validar)
        aguardar_overlay_invisivel(browser, time_to_wait)
        if not art_cep_nao_localizado(browser, timeout=10):
            return

    _corrigir_cep_apos_falha(
        browser,
        cep_el,
        cliente,
        click_validar,
        time_to_wait,
        lambda b: restaurar_endereco_planilha_modal(b, cliente),
        usar_select2_cidade=True,
    )


def fluxo_cep_contrato(
    browser: WebDriver,
    cep_el: WebElement,
    cliente,
    time_to_wait: int = 60,
) -> None:
    """CONTRATO_ENDERECO_CEP*: validação via TAB (sem botão ajax)."""
    aguardar_overlay_invisivel(browser, 10)
    plan = normalize_cep_digits(cliente.cep)
    first_from_viacep = False

    if VIACEP_MODE == "before_fill":
        v = _buscar_viacep_cliente(cliente)
        if v:
            primeiro = v
            first_from_viacep = True
        else:
            primeiro = plan
    else:
        primeiro = plan

    def _validar_tab() -> None:
        cep_el.send_keys(Keys.TAB)

    _preencher_e_validar_cep(cep_el, primeiro, _validar_tab)
    aguardar_overlay_invisivel(browser, time_to_wait)

    if not art_cep_nao_localizado(browser, timeout=12):
        return

    if first_from_viacep:
        _preencher_e_validar_cep(cep_el, plan, _validar_tab)
        aguardar_overlay_invisivel(browser, time_to_wait)
        if not art_cep_nao_localizado(browser, timeout=10):
            return

    v = _buscar_viacep_cliente(cliente)
    atual = normalize_cep_digits(cep_el.get_attribute("value") or "")
    if v and v != atual:
        _preencher_e_validar_cep(cep_el, v, _validar_tab)
        aguardar_overlay_invisivel(browser, time_to_wait)
        if not art_cep_nao_localizado(browser, timeout=10):
            return

    _corrigir_cep_apos_falha(
        browser,
        cep_el,
        cliente,
        _validar_tab,
        time_to_wait,
        lambda b: restaurar_endereco_planilha_contrato(b, cliente),
        usar_select2_cidade=False,
    )
