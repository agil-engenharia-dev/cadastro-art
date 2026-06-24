"""Ações Selenium resilientes (overlays, viewport e diferenças Chrome/Windows)."""

from __future__ import annotations

from selenium.common.exceptions import NoSuchWindowException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import Select

from app.utils.browser_windows import executar_com_recuperacao_janela
from app.utils.validation import remove_accentuation


def _normalizar_opcao_select(valor: str) -> str:
    return remove_accentuation((valor or "").strip().upper())


def _resolver_valor_opcao_select(element: WebElement, value: str) -> str:
    """Encontra o value real da option, ignorando diferenças de acentuação."""
    alvo = _normalizar_opcao_select(value)
    if not alvo:
        return value

    for option in Select(element).options:
        option_value = (option.get_attribute("value") or "").strip()
        option_text = (option.text or "").strip()
        if _normalizar_opcao_select(option_value) == alvo:
            return option_value
        if _normalizar_opcao_select(option_text) == alvo:
            return option_value or option_text

    return value


def scroll_para_elemento(browser: WebDriver, element: WebElement) -> None:
    def _scroll():
        browser.execute_script(
            "arguments[0].scrollIntoView({block:'center', inline:'nearest'});",
            element,
        )

    try:
        _scroll()
    except NoSuchWindowException:
        executar_com_recuperacao_janela(browser, _scroll)


def clicar_seguro(browser: WebDriver, element: WebElement) -> None:
    def _clicar():
        scroll_para_elemento(browser, element)
        try:
            element.click()
        except Exception:
            browser.execute_script("arguments[0].click();", element)

    try:
        _clicar()
    except NoSuchWindowException:
        executar_com_recuperacao_janela(browser, _clicar)


def preencher_seguro(browser: WebDriver, element: WebElement, texto: str) -> None:
    def _preencher():
        scroll_para_elemento(browser, element)
        try:
            element.clear()
            # Limpa autofill do Chrome (comum no Windows) antes de digitar o valor desejado.
            element.send_keys(Keys.CONTROL, "a")
            element.send_keys(Keys.DELETE)
            element.send_keys(texto)
        except Exception:
            browser.execute_script(
                "arguments[0].value = '';"
                "arguments[0].dispatchEvent(new Event('input', {bubbles: true}));"
                "arguments[0].dispatchEvent(new Event('change', {bubbles: true}));"
                "arguments[0].value = arguments[1];"
                "arguments[0].dispatchEvent(new Event('input', {bubbles: true}));"
                "arguments[0].dispatchEvent(new Event('change', {bubbles: true}));",
                element,
                texto,
            )

    try:
        _preencher()
    except NoSuchWindowException:
        executar_com_recuperacao_janela(browser, _preencher)


def selecionar_por_valor_seguro(
    browser: WebDriver, element: WebElement, value: str
) -> None:
    def _selecionar():
        scroll_para_elemento(browser, element)
        valor_resolvido = _resolver_valor_opcao_select(element, value)
        try:
            Select(element).select_by_value(valor_resolvido)
        except Exception:
            try:
                Select(element).select_by_visible_text(valor_resolvido)
            except Exception:
                browser.execute_script(
                    "arguments[0].value = arguments[1];"
                    "arguments[0].dispatchEvent(new Event('change', {bubbles: true}));",
                    element,
                    valor_resolvido,
                )

    try:
        _selecionar()
    except NoSuchWindowException:
        executar_com_recuperacao_janela(browser, _selecionar)
