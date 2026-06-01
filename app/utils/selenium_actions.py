"""Ações Selenium resilientes (overlays, viewport e diferenças Chrome/Windows)."""

from __future__ import annotations

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import Select


def scroll_para_elemento(browser: WebDriver, element: WebElement) -> None:
    browser.execute_script(
        "arguments[0].scrollIntoView({block:'center', inline:'nearest'});",
        element,
    )


def clicar_seguro(browser: WebDriver, element: WebElement) -> None:
    scroll_para_elemento(browser, element)
    try:
        element.click()
    except Exception:
        browser.execute_script("arguments[0].click();", element)


def preencher_seguro(browser: WebDriver, element: WebElement, texto: str) -> None:
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


def selecionar_por_valor_seguro(
    browser: WebDriver, element: WebElement, value: str
) -> None:
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
