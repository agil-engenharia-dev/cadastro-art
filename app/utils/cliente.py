from app.utils.validation import *

class Cliente:
    def __init__(
        self,
        nome,
        cpf,
        sexo,
        cep,
        tipo_de_logradouro,
        data_do_contrato,
        logradouro,
        numero,
        bairro,
        cidade,
        uf,
        valor_do_plano,
    ):
        self.nome = validarNome(nome)
        self.cpf = validarCpf(cpf)
        self.sexo = validarSexo(sexo)
        self.cep = validarCep(cep)
        self.tipo_de_logradouro = validarTipoDeLogradouro(tipo_de_logradouro)
        self.data = validarDataDoContrato(data_do_contrato)
        self.logradouro = validarLogradouro(logradouro)
        self.numero =validarNumero(numero)
        self.bairro = validarBairro(bairro)
        self.cidade = validarCidade(cidade)
        self.uf = validarUf(uf)
        self.valor_do_plano = validarValorDoPlano(valor_do_plano)
        self.TIME_TO_WAIT = 60 #segundos
    
    def __str__(self):
        RESET = "\033[0m"
        BOLD = "\033[1m"
        RED = "\033[31m"
        GREEN = "\033[32m"
        BLUE = "\033[34m"
        YELLOW = "\033[33m"
        return f"""
{BOLD}nome:{RESET} {GREEN}{self.nome}{RESET}
{BOLD}cpf:{RESET} {BLUE}{self.cpf}{RESET}
{BOLD}sexo:{RESET} {YELLOW}{self.sexo}{RESET}
{BOLD}cep:{RESET} {RED}{self.cep}{RESET}
{BOLD}data:{RESET} {GREEN}{self.data}{RESET}
{BOLD}tipo_de_logradouro:{RESET} {BLUE}{self.tipo_de_logradouro}{RESET}
{BOLD}logradouro:{RESET} {BLUE}{self.logradouro}{RESET}
{BOLD}numero:{RESET} {YELLOW}{self.numero}{RESET}
{BOLD}uf:{RESET} {RED}{self.uf}{RESET}
{BOLD}cidade:{RESET} {GREEN}{self.cidade}{RESET}
{BOLD}bairro:{RESET} {BLUE}{self.bairro}{RESET}
{BOLD}valor_do_plano:{RESET} {YELLOW}{self.valor_do_plano}{RESET}"""

