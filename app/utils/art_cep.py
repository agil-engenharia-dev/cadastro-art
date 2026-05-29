"""
Detecção de erro de CEP na ART (SITAC) e correção via ViaCEP.

Modo padrão: só consulta ViaCEP após a mensagem em #Result_cep.
Alternativa: CADASTRO_ART_VIACEP_MODE=before_fill (ou alterar VIACEP_MODE abaixo).
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

from app.utils.viacep import buscar_cep_por_endereco

# "on_cep_error" | "before_fill"
VIACEP_MODE = os.environ.get("CADASTRO_ART_VIACEP_MODE", "on_cep_error")

CEP_ERROR_SELECTORS = [
    (By.CSS_SELECTOR, "#Result_cep .aviso_ajaxresquest_erro"),
    (By.CSS_SELECTOR, "#Result_cep div[class*='aviso_ajax']"),
]


def normalize_cep_digits(cep: str | None) -> str:
    return "".join(filter(str.isdigit, str(cep or "")))


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


def aguardar_overlay_invisivel(browser: WebDriver, timeout: int = 15) -> None:
    try:
        WebDriverWait(browser, timeout).until(
            EC.invisibility_of_element_located((By.ID, "ajax-overlay"))
        )
    except Exception:
        pass


def selecionar_cidade_select2_modal_cep(browser: WebDriver, cliente, timeout: int = 20) -> bool:
    """
    Quando o CEP continua com erro na base da ART, abre o Select2 #s2id_CIDADE,
    pesquisa pela cidade do cliente e seleciona o item que coincide com cidade e UF
    (comparação sem acentos e case insensitive).
    """
    cidade_cli = _normalizar_texto_cmp(getattr(cliente, "cidade", None))
    uf_cli = _normalizar_texto_cmp(getattr(cliente, "uf", None))
    if len(cidade_cli) < 3 or len(uf_cli) != 2:
        return False

    aguardar_overlay_invisivel(browser, 10)
    try:
        container = WebDriverWait(browser, timeout).until(
            EC.element_to_be_clickable((By.ID, "s2id_CIDADE"))
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
        search.send_keys(getattr(cliente, "cidade", "") or "")
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

    alvo = None
    for li in itens:
        try:
            rotulo_el = li.find_element(By.CSS_SELECTOR, ".select2-user-result")
        except Exception:
            try:
                rotulo_el = li.find_element(By.CSS_SELECTOR, ".select2-result-label")
            except Exception:
                continue
        parsed = _parse_rotulo_cidade_uf(rotulo_el.text)
        if not parsed:
            continue
        c_p, u_p = parsed
        if _normalizar_texto_cmp(c_p) == cidade_cli and _normalizar_texto_cmp(u_p) == uf_cli:
            alvo = li
            break

    if alvo is None:
        return False

    try:
        browser.execute_script("arguments[0].scrollIntoView({block:'center'});", alvo)
        alvo.click()
    except Exception:
        try:
            browser.execute_script("arguments[0].click();", alvo)
        except Exception:
            return False

    aguardar_overlay_invisivel(browser, 10)
    return True


def _elemento_erro_cep_visivel(browser: WebDriver) -> bool:
    for by, sel in CEP_ERROR_SELECTORS:
        try:
            el = browser.find_element(by, sel)
            if not el.is_displayed():
                continue
            text = (el.text or "").lower()
            if "cep" in text and "localiz" in text:
                return True
            if "não foi localizado" in text or "nao foi localizado" in text:
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

    cep_el.clear()
    cep_el.send_keys(primeiro)
    click_validar()
    time.sleep(0.5)
    aguardar_overlay_invisivel(browser, time_to_wait)

    if not art_cep_nao_localizado(browser, timeout=12):
        return

    if first_from_viacep:
        cep_el.clear()
        cep_el.send_keys(plan)
        click_validar()
        time.sleep(0.5)
        aguardar_overlay_invisivel(browser, time_to_wait)
        if not art_cep_nao_localizado(browser, timeout=10):
            return

    v = _buscar_viacep_cliente(cliente)
    atual = normalize_cep_digits(cep_el.get_attribute("value") or "")
    if v and v != atual:
        cep_el.clear()
        cep_el.send_keys(v)
        click_validar()
        time.sleep(0.5)
        aguardar_overlay_invisivel(browser, time_to_wait)

    if art_cep_nao_localizado(browser, timeout=4):
        if selecionar_cidade_select2_modal_cep(
            browser, cliente, timeout=min(20, time_to_wait)
        ):
            click_validar()
            time.sleep(0.5)
            aguardar_overlay_invisivel(browser, time_to_wait)


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

    cep_el.clear()
    cep_el.send_keys(primeiro)
    cep_el.send_keys(Keys.TAB)
    time.sleep(0.5)
    aguardar_overlay_invisivel(browser, time_to_wait)

    if not art_cep_nao_localizado(browser, timeout=12):
        return

    if first_from_viacep:
        cep_el.clear()
        cep_el.send_keys(plan)
        cep_el.send_keys(Keys.TAB)
        time.sleep(0.5)
        aguardar_overlay_invisivel(browser, time_to_wait)
        if not art_cep_nao_localizado(browser, timeout=10):
            return

    v = _buscar_viacep_cliente(cliente)
    atual = normalize_cep_digits(cep_el.get_attribute("value") or "")
    if v and v != atual:
        cep_el.clear()
        cep_el.send_keys(v)
        cep_el.send_keys(Keys.TAB)
        time.sleep(0.5)
        aguardar_overlay_invisivel(browser, time_to_wait)
