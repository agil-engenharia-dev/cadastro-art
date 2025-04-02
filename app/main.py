from selenium import webdriver
import pandas as pd
from app.qt.mainwindow import tela
import tempfile
import os
from selenium.webdriver.chrome.options import Options
from PyQt6.QtWidgets import QApplication
from app.utils.clienteCE import ClienteCE
from app.utils.clienteMA import ClienteMA
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service 

import sys
print(sys.path)

ESTADOS = {
    "CE": ClienteCE,
    "MA": ClienteMA
}

def formatar_cpf(cpf):
    """Garante que o CPF tenha 11 dígitos, mantendo zeros à esquerda"""
    cpf = str(cpf).strip()
    
    cpf = ''.join(filter(str.isdigit, cpf))
    
    return cpf.zfill(11)

def extrair_clientes(dataframe, Classe):
    os.system('cls')
    colunas_para_texto = dataframe.columns
    if len(colunas_para_texto) != 12: 
        raise ValueError("\033[31mERRO NA QUANTIDADE DE COLUNAS DA PLANILHA!\033[0m")
    
    
    dataframe[colunas_para_texto] = dataframe[colunas_para_texto].astype(str)
    
    
    if 'CPF' in dataframe.columns:
        dataframe['CPF'] = dataframe['CPF'].apply(formatar_cpf)
    
    print("\033[34m", dataframe.head(), "\033[0m")
    
    clientes = []
    for data in dataframe.values:
        try:
            
            if len(data) > 1:  
                data[1] = formatar_cpf(data[1])
            cliente = Classe(data) 
            print(f"\033[32m{cliente.nome} - OK\033[0m")
            clientes.append(cliente)
        except ValueError as erro:
            print(f"\033[31m {erro} no cliente : \033[34m{data}\033[0m")
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


if __name__ == "__main__":
    
    pd.set_option('display.float_format', lambda x: '%.0f' % x)
    
    dados = tela()
    if None in dados.values():
        print("\033[31mERRO NOS DADOS INSERIDOS!\033[0m")
        quit()
        
   
    dataframe = pd.read_excel(dados["dir_planilha"], dtype={'CPF': str})  
    
    clientes = extrair_clientes(dataframe, ESTADOS[dados["estado"]])

    if input("deseja continuar? [S/N]").upper() == "S":
        browser = browserChromeFactory()
        for cliente in clientes:
            try:
                print("número ART: " + dados["numero_art"])
                cliente.login_crea(browser, dados["login"], dados["senha"])
                cliente.cadastrar(browser, dados["numero_art"])
                print(f"\033[32mSUCESSO NO CLIENTE: {cliente.nome}\033[0m")
            except Exception as e:
                print(f"\033[31mERRO NO CLIENTE: {cliente.nome}\033[0m")
                print(f"\033[31mDetalhes do erro: {e}\033[0m")