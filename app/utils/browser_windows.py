"""
Gerenciamento global de janelas/popups do Chrome no fluxo SITAC.

- Guarda a janela principal do formulário da ART no driver.
- Recupera automaticamente quando o Selenium aponta para uma janela fechada.
- Context manager para fluxos que abrem popup (contratante, atuação, mapa).
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Callable, Iterator

from selenium.common.exceptions import NoSuchWindowException, TimeoutException, WebDriverException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait

ATTR_JANELA_PRINCIPAL = "_cadastro_art_main_handle"

_METODOS_COM_RECUPERACAO = frozenset(
    {
        "find_element",
        "find_elements",
        "execute_script",
        "execute_async_script",
        "get",
        "refresh",
        "back",
        "forward",
        "current_url",
        "page_source",
    }
)


def desembrulhar(browser) -> WebDriver:
    """Retorna o WebDriver real (sem o proxy de recuperação)."""
    atual = browser
    while hasattr(atual, "_driver_interno"):
        atual = atual._driver_interno
    return atual


def definir_janela_principal(browser, handle: str | None = None) -> str:
    """Registra qual aba é o formulário principal da ART."""
    driver = desembrulhar(browser)
    if handle is None:
        handle = driver.current_window_handle
    setattr(driver, ATTR_JANELA_PRINCIPAL, handle)
    return handle


def obter_janela_principal(browser) -> str | None:
    return getattr(desembrulhar(browser), ATTR_JANELA_PRINCIPAL, None)


def janela_atual_valida(browser) -> bool:
    driver = desembrulhar(browser)
    try:
        return driver.current_window_handle in driver.window_handles
    except (NoSuchWindowException, WebDriverException):
        return False


def recuperar_janela_ativa(browser) -> str | None:
    """
    Troca para a janela principal registrada ou para qualquer aba ainda aberta.
    Retorna o handle ativo ou None se não houver janelas.
    """
    driver = desembrulhar(browser)
    candidatos: list[str] = []
    principal = obter_janela_principal(browser)
    if principal:
        candidatos.append(principal)
    try:
        candidatos.extend(driver.window_handles)
    except (NoSuchWindowException, WebDriverException):
        pass

    vistos: set[str] = set()
    for handle in candidatos:
        if not handle or handle in vistos:
            continue
        vistos.add(handle)
        try:
            if handle not in driver.window_handles:
                continue
            driver.switch_to.window(handle)
            definir_janela_principal(browser, handle)
            return handle
        except Exception:
            continue
    return None


def voltar_janela_principal(browser, main_handle: str | None = None) -> None:
    """Volta ao formulário da ART após popup/modal."""
    driver = desembrulhar(browser)
    alvo = main_handle or obter_janela_principal(browser)
    try:
        if alvo and alvo in driver.window_handles:
            driver.switch_to.window(alvo)
            return
    except Exception:
        pass
    recuperar_janela_ativa(browser)


def executar_com_recuperacao_janela(browser, acao: Callable):
    """Executa callable; em janela fechada, recupera e tenta de novo."""
    try:
        return acao()
    except NoSuchWindowException:
        if recuperar_janela_ativa(browser) is None:
            raise
        return acao()


class _SwitchToComRecuperacao:
    def __init__(self, proxy: "WebDriverComRecuperacaoJanela"):
        self._proxy = proxy

    def window(self, handle: str) -> None:
        def _ir():
            self._proxy._driver_interno.switch_to.window(handle)

        self._proxy._executar(_ir)

    def __getattr__(self, name):
        return getattr(self._proxy._driver_interno.switch_to, name)


class WebDriverComRecuperacaoJanela:
    """
    Proxy do WebDriver: em NoSuchWindowException volta à janela principal e repete.
    Use envolver_browser() na factory do Chrome.
    """

    def __init__(self, driver: WebDriver):
        self._driver_interno = driver

    def _executar(self, acao: Callable):
        try:
            return acao()
        except NoSuchWindowException:
            if recuperar_janela_ativa(self) is None:
                raise
            return acao()

    def __getattr__(self, name):
        attr = getattr(self._driver_interno, name)
        if name in _METODOS_COM_RECUPERACAO and callable(attr):

            def wrapper(*args, **kwargs):
                return self._executar(lambda: attr(*args, **kwargs))

            return wrapper
        return attr

    @property
    def switch_to(self) -> _SwitchToComRecuperacao:
        return _SwitchToComRecuperacao(self)

    @property
    def current_window_handle(self) -> str:
        return self._executar(lambda: self._driver_interno.current_window_handle)

    @property
    def window_handles(self) -> list[str]:
        return self._executar(lambda: self._driver_interno.window_handles)

    @property
    def title(self) -> str:
        return self._executar(lambda: self._driver_interno.title)


def envolver_browser(driver: WebDriver):
    if isinstance(driver, WebDriverComRecuperacaoJanela):
        return driver
    return WebDriverComRecuperacaoJanela(driver)


def wait(browser, timeout: float) -> WebDriverWait:
    """WebDriverWait usando o driver (com recuperação de janela se envolvido)."""
    return WebDriverWait(browser, timeout)


@contextmanager
def janela_auxiliar(
    browser,
    abrir: Callable[[], None],
    *,
    timeout: float = 5,
    fechar_ao_sair: bool = False,
) -> Iterator[bool]:
    """
    Abre popup via callback, executa o bloco na nova janela e volta à principal.

    Yields True se entrou em uma nova janela; False se nenhuma abriu.
    """
    driver = desembrulhar(browser)
    principal = obter_janela_principal(browser) or driver.current_window_handle
    definir_janela_principal(browser, principal)

    handles_antes = set(driver.window_handles)
    abrir()

    try:
        WebDriverWait(browser, timeout).until(
            lambda d: len(desembrulhar(d).window_handles) > len(handles_antes)
        )
    except TimeoutException:
        pass

    novas = list(set(driver.window_handles) - handles_antes)
    entrou_popup = False
    if novas:
        driver.switch_to.window(novas[-1])
        entrou_popup = True
        try:
            driver.maximize_window()
        except Exception:
            pass

    try:
        yield entrou_popup
    finally:
        if entrou_popup and fechar_ao_sair:
            try:
                driver.close()
            except Exception:
                pass
        voltar_janela_principal(browser, principal)
