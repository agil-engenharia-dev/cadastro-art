from selenium import webdriver
import pandas as pd
from app.qt.mainwindow import tela
import tempfile
import os
from selenium.webdriver.chrome.options import Options
from PyQt6.QtWidgets import QApplication
from app.utils.clienteCE import ClienteCE
from app.utils.clienteMA import ClienteMA
from app.utils.clienteCFT import ClienteCFT
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta

import sys
print(sys.path)

from app.utils.error_report import ErrorReport

ESTADOS = {
    "CE": ClienteCE,
    "MA": ClienteMA,
    "CFT": ClienteCFT
}

def formatar_cpf(cpf):
    """Garante que o CPF tenha 11 dígitos, mantendo zeros à esquerda"""
    cpf = str(cpf).strip()
    
    cpf = ''.join(filter(str.isdigit, cpf))
    
    return cpf.zfill(11)

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
    
    if 'CPF' in dataframe.columns:
        dataframe['CPF'] = dataframe['CPF'].apply(formatar_cpf)
    
    print("\033[34m", dataframe.head(), "\033[0m")
    
    clientes = []
    for idx, data in enumerate(dataframe.values):
        row_data = dict(zip(list(dataframe.columns), list(data)))
        try:
            if len(data) > 1:  
                data[1] = formatar_cpf(data[1])
            
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
    
    
    browser = webdriver.Chrome(
        service=service,
        options=chrome_options
    )
    
   
    browser.set_page_load_timeout(45)
    browser.set_script_timeout(30)
    browser.implicitly_wait(0)  
    
    return browser

def salvar_relatorio_erros(dados: dict, error_report: ErrorReport) -> None:
    try:
        if not dados.get("salvar_relatorio_erros"):
            return
        if not error_report.has_errors:
            return

        output_path = (dados.get("caminho_relatorio_erros") or "").strip()
        formato = dados.get("formato_relatorio_erros") or "xlsx"
        if not output_path:
            print("\033[33mRelatório de erros habilitado, mas sem caminho de saída.\033[0m")
            return

        saved = error_report.export(output_path, formato=formato)
        print(f"\033[33mRelatório de erros salvo em: {saved}\033[0m")
    except Exception as e:
        print(f"\033[31mFalha ao salvar relatório de erros: {e}\033[0m")

if __name__ == "__main__":
    
    pd.set_option('display.float_format', lambda x: '%.0f' % x)
    
    dados = tela()
    if None in dados.values():
        print("\033[31mERRO NOS DADOS INSERIDOS!\033[0m")
        quit()
        
   
    dataframe = pd.read_excel(dados["dir_planilha"], dtype={'CPF': str})  

    error_report = ErrorReport(dataframe.columns)
    
    if dados["estado"] == "CFT":
        # Usa a classe ClienteCFT para processar todos os usuários
        clientes = extrair_clientes(dataframe, ClienteCFT, error_report)
    else:
        clientes = extrair_clientes(dataframe, ESTADOS[dados["estado"]], error_report)

    if input("deseja continuar? [S/N]").upper() == "S":
        browser = browserChromeFactory()
        
        for i, cliente in enumerate(clientes, 1):
            try:
                print(f"\n{'='*60}")
                print(f"Processando cliente {i}/{len(clientes)}: {cliente.nome}")
                print(f"{'='*60}")
                
                # Verifica se o browser ainda está ativo
                try:
                    browser.title  # Testa se o browser está ativo
                except:
                    print("⚠ Navegador fechou, recriando...")
                    browser = browserChromeFactory()
                    print("✓ Navegador recriado")
                
                print("número ART: " + dados["numero_art"])
                # Verifica se já está logado
                try:
                    WebDriverWait(browser, 5).until(
                        EC.presence_of_element_located((By.ID, "logout_info"))
                    )
                    print("Já está logado, continuando...")
                except:
                    # Se não estiver logado, faz o login
                    if dados["estado"] == "CFT":
                        try:
                            cliente.login_CFT(browser, dados["login"], dados["senha"])
                        except Exception as e:
                            error_report.add(
                                row_data=getattr(cliente, "_row_data", {}),
                                etapa="login",
                                motivo="Falha no login (CFT).",
                                exception=e,
                                contexto={
                                    "cliente_nome": getattr(cliente, "nome", ""),
                                    "cliente_index": i,
                                    "estado": dados.get("estado"),
                                },
                            )
                            raise
                    else:
                        try:
                            cliente.login_crea(browser, dados["login"], dados["senha"])
                        except Exception as e:
                            error_report.add(
                                row_data=getattr(cliente, "_row_data", {}),
                                etapa="login",
                                motivo="Falha no login (CREA).",
                                exception=e,
                                contexto={
                                    "cliente_nome": getattr(cliente, "nome", ""),
                                    "cliente_index": i,
                                    "estado": dados.get("estado"),
                                },
                            )
                            raise
                
                try:
                    if dados["estado"] == "CE":
                        cliente.cadastrar(
                            browser, dados["numero_art"], error_report=error_report
                        )
                    elif dados["estado"] == "MA":
                        cliente.cadastrar(
                            browser,
                            dados["numero_art"],
                            nivel_atividade=dados.get("nivel_atividade"),
                            atividade_profissional=dados.get("atividade_profissional"),
                            error_report=error_report,
                        )
                    else:
                        cliente.cadastrar(browser, dados["numero_art"])
                except Exception as e:
                    error_report.add(
                        row_data=getattr(cliente, "_row_data", {}),
                        etapa="cadastrar",
                        motivo="Falha durante o cadastro no site.",
                        exception=e,
                        contexto={
                            "cliente_nome": getattr(cliente, "nome", ""),
                            "cliente_index": i,
                            "estado": dados.get("estado"),
                            "numero_art": dados.get("numero_art"),
                        },
                    )
                    raise
                print(f"\033[32m✓ SUCESSO NO CLIENTE: {cliente.nome}\033[0m")
            except Exception as e:
                print(f"\033[31m✗ ERRO NO CLIENTE: {cliente.nome}\033[0m")
                print(f"\033[31mDetalhes do erro: {e}\033[0m")
                
                # Tenta fechar e recriar o browser após erro
                try:
                    browser.quit()
                except:
                    pass
                
                if i < len(clientes):  # Se não for o último cliente
                    print("\n⚠ Recriando navegador para próximo cliente...")
                    browser = browserChromeFactory()
                    print("✓ Navegador recriado")

        salvar_relatorio_erros(dados, error_report)
    else:
        # Ainda permite salvar erros de validação/leitura da planilha
        salvar_relatorio_erros(dados, error_report)