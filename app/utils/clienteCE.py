from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import time
from app.utils.cliente import Cliente
from selenium.common.exceptions import NoSuchElementException

class ClienteCE(Cliente):
    def __init__(self, args):
        super().__init__(*args)
        self.URL_LOGIN_CREA = "https://servicos-crea-ce.sitac.com.br/index.php"
        self.URL_ART = "https://servicos-crea-ce.sitac.com.br/app/view/sight/ini?form=Art&id="

        
    
    def cadastrar(self, browser, numero_art):
        browser.get(self.URL_ART + numero_art)
        
        element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
            EC.presence_of_element_located((By.ID, f'cadastrarContratoArt{numero_art}'))
        )
        element_select.click()
        
        time.sleep(5)

        try:
            popup_fechar = WebDriverWait(browser, 2).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Nunca')]"))
            )
            popup_fechar.click()
        except:
            pass  

        time.sleep(2)
        try:
            element_select = WebDriverWait(browser, 5).until(
            EC.presence_of_element_located((By.ID, 'ACAOINSTITUCIONAL')))
            select = Select(element_select)
            select.select_by_value("11") #nao optante
        except:pass
        
        try:
            element_select = WebDriverWait(browser, 2).until(
            EC.presence_of_element_located((By.ID, 'NIVEL00')))
            select = Select(element_select)
            select.select_by_value("38")#execução
        except:
            element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
            EC.presence_of_element_located((By.ID, 'NOVA_ATIVIDADE')))
            element_select.click()
        
       
        
        element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
        EC.presence_of_element_located((By.ID, 'NIVEL00')))
        select = Select(element_select)
        select.select_by_value("38")#execução

        element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
        EC.presence_of_element_located((By.ID, 'ATIVIDADEPROFISSIONAL00')))
        select = Select(element_select)
        select.select_by_value("4180")#atividade profissional
        
        element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
            EC.presence_of_element_located(
                (By.ID, 'LABELATUACAO00')
            )
        )
        element_select.send_keys('1', '2', '.', '7')
        time.sleep(4)
        xpath = "//div[@id='listaAtividadeEscolherATUACAO00']//li[1]"
        browser.find_element(By.XPATH, xpath).click()
        
        element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
        EC.presence_of_element_located((By.ID, 'UNIDADEMEDIDA00')))
        select = Select(element_select)
        select.select_by_value("18924748")#unidade de medida
        
        element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
        EC.presence_of_element_located((By.ID, 'QUANTIDADE00')))
        element_select.clear()
        element_select.send_keys("1,00")#quantidade
        
        element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
        EC.presence_of_element_located((By.ID, "contratante0_ContratantePF")))
        element_select.click() #contratante 
        
        
        element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
        EC.presence_of_element_located((By.ID, 'contratante0_CampoContratantePF')))
        element_select.clear()
        element_select.send_keys(self.cpf)#cpf
        element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
        EC.presence_of_element_located((By.ID, 'session_timeout_container')))
        element_select.click()
        

        try:
            element_select = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.botao_adicionar")))
            element_select.click()#cadastrar contratante
            browser.switch_to.window(browser.window_handles[-1])
            browser.maximize_window()
            
            
            element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
            EC.presence_of_element_located((By.ID, 'NOME')))
            element_select.clear()
            element_select.send_keys(self.nome)#nome
            
            element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
            EC.presence_of_element_located((By.ID, 'CEP')))
            element_select.clear()
            element_select.send_keys(self.cep)#cep
            
            
            element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a.botao_ajaxform_adicionar")))
            element_select.click()#botao endereco
            time.sleep(5)
                
            element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
            EC.presence_of_element_located((By.ID, 'TIPOLOGRADOURO')))
            select = Select(element_select)
            select.select_by_value(self.tipo_de_logradouro)#tipo_de_logradouro
            
            
            element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
            EC.presence_of_element_located((By.ID, 'LOGRADOURO')))
            element_select.clear()
            element_select.send_keys(self.logradouro)#logradouro
            
            element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
            EC.presence_of_element_located((By.ID, 'ENDERECO_NUMERO')))
            element_select.clear()
            element_select.send_keys(self.numero)#numero
            
            element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
            EC.presence_of_element_located((By.ID, 'BAIRRO')))
            element_select.clear()
            element_select.send_keys(self.bairro)#bairro
            
            
            element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
            EC.presence_of_element_located((By.ID, 'save')))
            element_select.click()
            
            browser.switch_to.window(browser.window_handles[0])
        except:
            pass


        time.sleep(5)
        
        element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
        EC.presence_of_element_located((By.ID, 'CONTRATO_VALOR0')))
        element_select.clear()
        element_select.send_keys(self.valor_do_plano)#data
        element_select.send_keys(Keys.TAB, Keys.ARROW_UP)

        element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
        EC.presence_of_element_located((By.ID, 'CONTRATO_DATA0')))
        element_select.clear()
        element_select.send_keys(self.data)#data inicio
        
        element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
        EC.presence_of_element_located((By.ID, 'CONTRATO_DATAINICIO0')))
        element_select.clear()
        element_select.send_keys(self.data)#data inicio
        
        element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
        EC.presence_of_element_located((By.ID, 'CONTRATO_DATAFIM0')))
        element_select.clear()
        element_select.send_keys(self.data)#data fim
        
        time.sleep(5)

        try:

            if self.cep:
                raise ValueError("CEP está preenchido")

            element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
                EC.presence_of_element_located((By.ID, 'CONTRATO_ENDERECO_CEP0')))
            element_select.clear()
            element_select.send_keys(self.cep)  # cep

            element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
                EC.presence_of_element_located((By.ID, 'CONTRATO_ENDERECO_TIPOLOGRADOURO0')))
            select = Select(element_select)
            select.select_by_value(self.tipo_de_logradouro)  # tipo_de_logradouro

            element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
                EC.presence_of_element_located((By.ID, 'CONTRATO_ENDERECO_LOGRADOURO0')))
            element_select.clear()
            element_select.send_keys(self.logradouro)  # logradouro

            element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
                EC.presence_of_element_located((By.ID, 'CONTRATO_ENDERECO_NUMERO0')))
            element_select.clear()
            element_select.send_keys(self.numero)  # numero

            element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
                EC.presence_of_element_located((By.ID, 'CONTRATO_ENDERECO_BAIRRO0')))
            element_select.clear()
            element_select.send_keys(self.bairro)  # bairro

        except:
            pass
        

        
        element_select = WebDriverWait(browser, self.TIME_TO_WAIT).until(
        EC.presence_of_element_located((By.ID, "save")))
        element_select.click() #salvar
        time.sleep(10)

    def login_crea(self, browser, login, senha) -> None:
        try:
            logout_button = browser.find_element(By.ID, "logout_button")
            print("Online!")
        except NoSuchElementException:
            print("Offline, prosseguindo com o login!")

            browser.get(self.URL_LOGIN_CREA)

            cpf_input = WebDriverWait(browser, self.TIME_TO_WAIT).until(
                EC.presence_of_element_located((By.ID, "login"))
            )
            senha_input = WebDriverWait(browser, self.TIME_TO_WAIT).until(
                EC.presence_of_element_located((By.ID, "senha"))
            )
            login_button = WebDriverWait(browser, self.TIME_TO_WAIT).until(
                EC.presence_of_element_located((By.ID, "enviar"))
            )

            cpf_input.send_keys(login)
            senha_input.send_keys(senha)
            login_button.click()

            WebDriverWait(browser, self.TIME_TO_WAIT).until(
                EC.presence_of_element_located((By.ID, "logout_button"))
            )