from selenium import webdriver
import pandas as pd
from qt.mainwindow import tela
import tempfile
import os
from selenium.webdriver.chrome.options import Options

from utils.clienteCE import ClienteCE
from utils.clienteMA import ClienteMA


ESTADOS = {
    "CE":ClienteCE,
    "MA":ClienteMA
}


def extrair_clientes(dataframe,Classe):
    os.system('cls')
    colunas_para_texto = dataframe.columns
    if(len(colunas_para_texto) != 12): 
        raise ValueError("\033[31mERRO NA QUANTIDADES DE COLUNAS DA PLANILHA!\033[0m")
    dataframe[colunas_para_texto] = dataframe[colunas_para_texto].astype(str)
    print("\033[34m",dataframe.head(),"\033[0m")
    
    clientes = []
    for data in dataframe.values:
        try:
            cliente = Classe(data)
            print(f"\033[32m{cliente.nome} - OK\033[0m")
            clientes.append(cliente)
        except ValueError as erro:
            print(f"\033[31m {erro} no cliente : \033[34m{data}\033[0m")

    return clientes

def browserChromeFactory():
    chrome_options = Options()
    temp_profile = tempfile.mkdtemp()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument(f"--user-data-dir={temp_profile}")
    browser = webdriver.Chrome(options=chrome_options)
    browser.maximize_window()
    return browser

if __name__ == "__main__":
    dados = tela()
    if(None in dados.values()):
        print("\033[31mERRO NOS DADOS INSERIDOS!\033[0m")
        quit()
        
    dataframe = pd.read_excel(dados["dir_planilha"])
    clientes = extrair_clientes(dataframe,ESTADOS[dados["estado"]])

    if(input("deseja continuar? [S/N]").upper()=="S"):
        for cliente in clientes:
            try:
                browser = browserChromeFactory()
                cliente.login_crea(browser,dados["login"],dados["senha"])
                cliente.cadastrar(browser,dados["numero_art"])
                browser.quit()
                print(f"\033[32mSUCESSO NO CLIENTE: {cliente.nome}\033[0m")
            except:
                print(f"\033[31mERRO NO CLIENTE: {cliente.nome}\033[0m")