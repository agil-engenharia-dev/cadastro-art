"""
Detecção de erro de CEP na ART (SITAC) e correção via ViaCEP.

Modo padrão: só consulta ViaCEP após a mensagem em #Result_cep.
Alternativa: CADASTRO_ART_VIACEP_MODE=before_fill (ou alterar VIACEP_MODE abaixo).
"""

from __future__ import annotations

import os
import time
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
