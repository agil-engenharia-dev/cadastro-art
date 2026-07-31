import pandas as pd
from app.qt.mainwindow import tela
import tempfile
import os
import traceback
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebDriver
from PyQt6.QtWidgets import QApplication
from app.utils.clienteCE import ClienteCE
from app.utils.clienteMA import ClienteMA
from app.utils.clienteCFT import ClienteCFT
from app.utils.cliente_sitac import ClienteSitac
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta

import sys
print(sys.path)

from app.utils.error_report import (
    ErrorReport,
    persistir_relatorio_erros,
    registrar_erro_cliente,
    anexar_erro_em_log,
)
from app.utils.browser_windows import (
    definir_janela_principal,
    envolver_browser,
    recuperar_janela_ativa,
 )

ESTADOS = {
    "CE": ClienteCE,
    "MA": ClienteMA,
    "CFT": ClienteCFT
}

def formatar_cpf(cpf):
    """Garante que o CPF tenha 11 dígitos, mantendo zeros à esquerda"""
    cpf = str(cpf).strip()

    cpf = "".join(filter(str.isdigit, cpf))

    return cpf.zfill(11)


def formatar_cpf_ou_cnpj(documento):
    """Normaliza CPF (11 dígitos) ou CNPJ (14 dígitos) conforme o tamanho do documento."""
    digitos = "".join(filter(str.isdigit, str(documento).strip()))
    if len(digitos) > 11:
        return digitos.zfill(14)
    return digitos.zfill(11)

def validar_data_mes_anterior(data_str):
    """Valida se a data é do mês anterior ao atual"""
    try:
        # Tenta primeiro o formato YYYY-MM-DD
        try:
            data_cliente = datetime.strptime(data_str, '%Y-%m-%d')
        except ValueError:
            # Se falhar, tenta o formato DD/MM/YYYY
            data_cliente = datetime.strptime(data_str, '%d/%m/%Y')
        
        # Obtém a data atual
        data_atual = datetime.now()
        
        # Calcula o mês anterior
        mes_anterior = data_atual.replace(day=1) - timedelta(days=1)
        
        # Verifica se o mês e ano da data do cliente são iguais ao mês anterior
        if data_cliente.month == mes_anterior.month and data_cliente.year == mes_anterior.year:
            return True
        return False
    except ValueError:
        raise ValueError("Formato de data inválido. Use DD/MM/AAAA ou AAAA-MM-DD")

def extrair_clientes(dataframe, Classe, error_report: ErrorReport | None = None):
    os.system('cls')
    colunas_para_texto = dataframe.columns
    if len(colunas_para_texto) != 12: 
        msg = "\033[31mERRO NA QUANTIDADE DE COLUNAS DA PLANILHA!\033[0m"
        if error_report is not None:
            error_report.add(
                row_data={},
                etapa="validacao_planilha",
                motivo="Quantidade de colunas inválida (esperado: 12).",
                contexto={"colunas_encontradas": len(colunas_para_texto)},
            )
        raise ValueError(msg)
    
    dataframe[colunas_para_texto] = dataframe[colunas_para_texto].astype(str)
    
    if "CPF" in dataframe.columns:
        formatar_doc = (
            formatar_cpf_ou_cnpj
            if issubclass(Classe, ClienteSitac)
            else formatar_cpf
        )
        dataframe["CPF"] = dataframe["CPF"].apply(formatar_doc)
    
    print("\033[34m", dataframe.head(), "\033[0m")
    
    clientes = []
    for idx, data in enumerate(dataframe.values):
        row_data = dict(zip(list(dataframe.columns), list(data)))
        try:
            if len(data) > 1:
                formatar_doc = (
                    formatar_cpf_ou_cnpj
                    if issubclass(Classe, ClienteSitac)
                    else formatar_cpf
                )
                data[1] = formatar_doc(data[1])
            
            # Valida a data antes de criar o cliente
            if not validar_data_mes_anterior(data[5]):  # Assumindo que a data está na coluna 5
                motivo = (
                    f"Data inválida para o cliente: {data[0]}. "
                    "A data deve ser do mês anterior ao atual."
                )
                print(f"\033[31m{motivo}\033[0m")
                if error_report is not None:
                    error_report.add(
                        row_data=row_data,
                        etapa="validacao_linha",
                        motivo=motivo,
                        contexto={"linha_index": idx, "coluna_index_data": 5},
                    )
                continue
                
            cliente = Classe(data) 
            try:
                setattr(cliente, "_row_data", row_data)
                setattr(cliente, "_row_index", idx)
            except Exception:
                pass
            print(f"\033[32m{cliente.nome} - OK\033[0m")
            clientes.append(cliente)
        except ValueError as erro:
            print(f"\033[31m {erro} no cliente : \033[34m{data}\033[0m")
            if error_report is not None:
                error_report.add(
                    row_data=row_data,
                    etapa="validacao_linha",
                    motivo=str(erro),
                    exception=erro,
                    contexto={"linha_index": idx},
                )
    return clientes

def browserChromeFactory():
    chrome_options = Options()
    
    
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-save-password-bubble")  
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--remote-allow-origins=*")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    
    
    chrome_options.add_experimental_option("prefs", {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "autofill.profile_enabled": False,  
        "autofill.address_enabled": False, 
        "autofill.credit_card_enabled": False  
    })
    
    
    service = Service(
        ChromeDriverManager().install(),
        service_args=['--verbose'],
        log_path='chromedriver.log'
    )
    
    
    browser = ChromeWebDriver(
        service=service,
        options=chrome_options
    )
    
   
    browser.set_page_load_timeout(45)
    browser.set_script_timeout(30)
    browser.implicitly_wait(0)

    try:
        browser.maximize_window()
    except Exception:
        pass

    return envolver_browser(browser)

def _limpar_flag_erro_cliente(cliente) -> None:
    try:
        cliente._erro_registrado = False
    except Exception:
        pass


if __name__ == "__main__":
    
    pd.set_option('display.float_format', lambda x: '%.0f' % x)
    
    dados = tela()
    if dados is None:
        print("\033[33mOperação cancelada ou formulário não confirmado.\033[0m")
        sys.exit(0)

    error_report: ErrorReport | None = None
    browser = None

    try:
        dataframe = pd.read_excel(dados["dir_planilha"], dtype={'CPF': str})

        error_report = ErrorReport(dataframe.columns)

        if dados["estado"] == "CFT":
            clientes = extrair_clientes(dataframe, ClienteCFT, error_report)
        else:
            clientes = extrair_clientes(dataframe, ESTADOS[dados["estado"]], error_report)

        persistir_relatorio_erros(dados, error_report)

        if input("deseja continuar? [S/N]").upper() == "S":
            try:
                try:
                    browser = browserChromeFactory()
                except Exception as e:
                    error_report.add(
                        row_data={},
                        etapa="inicializacao_browser",
                        motivo="Falha ao iniciar o navegador (Chrome/ChromeDriver).",
                        exception=e,
                        contexto={"estado": dados.get("estado")},
                    )
                    persistir_relatorio_erros(dados, error_report)
                    raise

                for i, cliente in enumerate(clientes, 1):
                    _limpar_flag_erro_cliente(cliente)
                    try:
                        print(f"\n{'='*60}")
                        print(f"Processando cliente {i}/{len(clientes)}: {cliente.nome}")
                        print(f"{'='*60}")

                        try:
                            browser.title
                        except Exception:
                            # Nem sempre o Chrome fechou: às vezes só a aba atual foi fechada
                            # (NoSuchWindowException). Tenta recuperar uma janela válida antes
                            # de recriar a sessão e forçar novo login.
                            if recuperar_janela_ativa(browser) is not None:
                                print("⚠ Janela atual fechou; recuperando sessão do navegador...")
                                definir_janela_principal(browser)
                            else:
                                print("⚠ Navegador fechou, recriando...")
                                browser = browserChromeFactory()
                                definir_janela_principal(browser)
                                print("✓ Navegador recriado")

                        print("número ART: " + dados["numero_art"])
                        try:
                            WebDriverWait(browser, 5).until(
                                EC.presence_of_element_located((By.ID, "logout_info"))
                            )
                            print("Já está logado, continuando...")
                        except Exception:
                            if dados["estado"] == "CFT":
                                try:
                                    cliente.login_CFT(
                                        browser, dados["login"], dados["senha"]
                                    )
                                    definir_janela_principal(browser)
                                except Exception as e:
                                    registrar_erro_cliente(
                                        error_report,
                                        cliente,
                                        etapa="login",
                                        motivo="Falha no login (CFT).",
                                        exception=e,
                                        contexto={
                                            "cliente_index": i,
                                            "estado": dados.get("estado"),
                                        },
                                        dados=dados,
                                    )
                                    raise
                            else:
                                try:
                                    cliente.login_crea(
                                        browser, dados["login"], dados["senha"]
                                    )
                                    definir_janela_principal(browser)
                                except Exception as e:
                                    registrar_erro_cliente(
                                        error_report,
                                        cliente,
                                        etapa="login",
                                        motivo="Falha no login (CREA).",
                                        exception=e,
                                        contexto={
                                            "cliente_index": i,
                                            "estado": dados.get("estado"),
                                        },
                                        dados=dados,
                                    )
                                    raise

                        try:
                            definir_janela_principal(browser)
                            if dados["estado"] == "CE":
                                cliente.cadastrar(
                                    browser,
                                    dados["numero_art"],
                                    error_report=error_report,
                                )
                            elif dados["estado"] == "MA":
                                cliente.cadastrar(
                                    browser,
                                    dados["numero_art"],
                                    nivel_atividade=dados.get("nivel_atividade"),
                                    atividade_profissional=dados.get(
                                        "atividade_profissional"
                                    ),
                                    atuacao=dados.get("atuacao"),
                                    error_report=error_report,
                                )
                            else:
                                cliente.cadastrar(
                                    browser,
                                    dados["numero_art"],
                                    error_report=error_report,
                                )
                        except Exception as e:
                            registrar_erro_cliente(
                                error_report,
                                cliente,
                                etapa="cadastrar",
                                motivo="Falha durante o cadastro no site.",
                                exception=e,
                                contexto={
                                    "cliente_index": i,
                                    "estado": dados.get("estado"),
                                    "numero_art": dados.get("numero_art"),
                                },
                                dados=dados,
                            )
                            raise
                        if not getattr(cliente, "_sucesso_confirmado", False):
                            motivo = (
                                "Cadastro finalizou sem confirmação explícita de sucesso "
                                "pela plataforma (modal de sucesso não detectado)."
                            )
                            print(f"\033[33m⚠ ALERTA NO CLIENTE: {cliente.nome}\033[0m")
                            print(f"\033[33mDetalhes do alerta: {motivo}\033[0m")
                            registrar_erro_cliente(
                                error_report,
                                cliente,
                                etapa="feedback_plataforma",
                                motivo=motivo,
                                exception=None,
                                contexto={
                                    "cliente_index": i,
                                    "estado": dados.get("estado"),
                                    "numero_art": dados.get("numero_art"),
                                },
                                dados=dados,
                            )
                            raise RuntimeError(motivo)
                        print(f"\033[32m✓ SUCESSO NO CLIENTE: {cliente.nome}\033[0m")
                    except Exception as e:
                        print(f"\033[31m✗ ERRO NO CLIENTE: {cliente.nome}\033[0m")
                        print(f"\033[31mDetalhes do erro: {e}\033[0m")
                        try:
                            print("\033[31mTraceback (Python):\033[0m")
                            print(traceback.format_exc())
                        except Exception:
                            pass

                        if not getattr(cliente, "_erro_registrado", False):
                            registrar_erro_cliente(
                                error_report,
                                cliente,
                                etapa="processamento_cliente",
                                motivo="Erro inesperado ao processar o cliente.",
                                exception=e,
                                contexto={"cliente_index": i},
                                dados=dados,
                            )
                        try:
                            anexar_erro_em_log(
                                dados,
                                etapa="processamento_cliente",
                                motivo="Erro inesperado ao processar o cliente.",
                                exception=e,
                                contexto={
                                    "cliente_nome": getattr(cliente, "nome", ""),
                                    "cliente_index": i,
                                    "estado": dados.get("estado"),
                                    "numero_art": dados.get("numero_art"),
                                },
                            )
                        except Exception:
                            pass

                        # Mantém o navegador e a sessão logada para o próximo cliente.
                        # O início do loop já recria o browser só se ele tiver fechado
                        # e só faz login se logout_info não estiver presente.
                        if i < len(clientes):
                            print(
                                "\n⚠ Erro neste cliente; mantendo navegador aberto "
                                "para o próximo."
                            )
            finally:
                if browser is not None:
                    try:
                        browser.quit()
                    except Exception:
                        pass

    except Exception as e:
        print(f"\033[31mErro fatal na execução: {e}\033[0m")
        try:
            print("\033[31mTraceback (Python):\033[0m")
            print(traceback.format_exc())
        except Exception:
            pass
        if error_report is None:
            error_report = ErrorReport([])
        error_report.add(
            row_data={},
            etapa="execucao",
            motivo="Erro fatal antes ou durante o processamento.",
            exception=e,
            contexto={"estado": dados.get("estado")},
        )
        try:
            anexar_erro_em_log(
                dados,
                etapa="execucao",
                motivo="Erro fatal antes ou durante o processamento.",
                exception=e,
                contexto={"estado": dados.get("estado")},
            )
        except Exception:
            pass
    finally:
        if error_report is not None:
            persistir_relatorio_erros(dados, error_report)