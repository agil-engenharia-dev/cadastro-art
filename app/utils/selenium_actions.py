"""Ações Selenium resilientes (overlays, viewport e diferenças Chrome/Windows)."""

from __future__ import annotations

from selenium.common.exceptions import NoSuchWindowException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import Select

from app.utils.browser_windows import executar_com_recuperacao_janela


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
            element.send_keys(texto)
        except Exception:
            browser.execute_script(
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
        try:
            Select(element).select_by_value(value)
        except Exception:
            browser.execute_script(
                "arguments[0].value = arguments[1];"
                "arguments[0].dispatchEvent(new Event('change', {bubbles: true}));",
                element,
                value,
            )

    try:
        _selecionar()
    except NoSuchWindowException:
        executar_com_recuperacao_janela(browser, _selecionar)
