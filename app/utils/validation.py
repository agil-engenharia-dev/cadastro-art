from datetime import date, datetime
import unicodedata


def remove_accentuation(word):
    return "".join(
        c for c in unicodedata.normalize("NFD", word) if unicodedata.category(c) != "Mn"
    )


TIPOS_LOGRADOUROS = {
    "": "",
    "RUA": "RUA",
    "AVENIDA": "AVENIDA",
    "APARTAMENTO": "APARTAMENTO",
    "LOTEAMENTO": "LOTEAMENTO",
    "TRAVESSA": "TRAVESSA",
    "AEROPORTO": "AEROPORTO",
    "ALAMEDA": "ALAMEDA",
    "AREA": "AREA",
    "CAMINHO": "CAMINHO",
    "CAMPO": "CAMPO",
    "CHACARA": "CHáCARA",
    "COLÔNIA": "COLôNIA",
    "CONDOMINIO": "CONDOMINIO",
    "CONJUNTO": "CONJUNTO",
    "DISTRITO": "DISTRITO",
    "ESPLANADA": "ESPLANADA",
    "ESTAÇAO": "ESTAçãO",
    "ESTRADA": "ESTRADA",
    "FAVELA": "FAVELA",
    "FAZENDA": "FAZENDA",
    "FEIRA": "FEIRA",
    "JARDIM": "JARDIM",
    "LADEIRA": "LADEIRA",
    "LAGO": "LAGO",
    "LAGOA": "LAGOA",
    "LARGO": "LARGO",
    "MORRO": "MORRO",
    "NUCLEO": "NúCLEO",
    "PARQUE": "PARQUE",
    "PASSARELA": "PASSARELA",
    "PASSAGEM": "PASSAGEM",
    "PATIO": "PáTIO",
    "POVOADO": "POVOADO",
    "PRAÇA": "PRAçA",
    "QUADRA": "QUADRA",
    "RAMAL": "RAMAL",
    "RECANTO": "RECANTO",
    "RESIDENCIAL": "RESIDENCIAL",
    "RODOVIA": "RODOVIA",
    "SETOR": "SETOR",
    "SITIO": "SíTIO",
    "TRECHO": "TRECHO",
    "TREVO": "TREVO",
    "UNIDADE": "UNIDADE",
    "VALE": "VALE",
    "VEREDA": "VEREDA",
    "VIA": "VIA",
    "VIADUTO": "VIADUTO",
    "VIELA": "VIELA",
    "VILA": "VILA",
    "OUTROS": "OUTROS",
    "SEM DEFINIÇAO": "SEM DEFINIçãO",
}


def validarNome(nome) -> str:
    try:
        nome = str(nome)
    except:
        raise ValueError("NOME ERROR")
    nome = nome.strip()
    nome = nome.title()
    return nome


def extrair_digitos_documento(documento) -> str:
    try:
        return "".join(filter(str.isdigit, str(documento)))
    except Exception:
        raise ValueError("CPF ERROR")


def eh_pessoa_juridica(documento) -> bool:
    return len(extrair_digitos_documento(documento)) > 11


def validarCnpj(cnpj) -> str:
    try:
        string_cnpj = str(cnpj)
    except Exception:
        raise ValueError("CNPJ ERROR")
    digitos = extrair_digitos_documento(string_cnpj)
    if len(digitos) != 14:
        raise ValueError("CNPJ ERROR")
    if digitos == digitos[0] * 14:
        raise ValueError("CNPJ ERROR")

    pesos1 = (5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2)
    pesos2 = (6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2)

    def calcular_digito(base: str, pesos: tuple[int, ...]) -> int:
        soma = sum(int(n) * p for n, p in zip(base, pesos))
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto

    d1 = calcular_digito(digitos[:12], pesos1)
    if d1 != int(digitos[12]):
        raise ValueError("CNPJ ERROR")
    d2 = calcular_digito(digitos[:12] + str(d1), pesos2)
    if d2 != int(digitos[13]):
        raise ValueError("CNPJ ERROR")

    return string_cnpj


def validarSexoPorDocumento(sexo, documento) -> str:
    try:
        sexo = str(sexo).strip().upper()
    except Exception:
        raise ValueError("SEXO ERROR")

    if eh_pessoa_juridica(documento):
        if sexo not in ("PUBLICO", "PRIVADO"):
            raise ValueError("SEXO ERROR")
        if sexo != "PRIVADO":
            raise ValueError(
                "PJ PUBLICO - apenas empresas com tipo PRIVADO são processadas"
            )
        return "PRIVADO"

    if sexo not in ("FEMININO", "MASCULINO"):
        raise ValueError("SEXO ERROR")
    return sexo


def validarCpf(cpf) -> str:
    try:
        stringCpf = str(cpf)
    except:
        raise ValueError("CPF ERROR")
    cpf = "".join(filter(str.isdigit, stringCpf))
    if len(cpf) != 11:
        raise ValueError("CPF ERROR")
    if cpf == cpf[0] * 11:
        raise ValueError("CPF ERROR")
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    resto = (soma * 10) % 11
    if resto == 10:
        resto = 0
    if resto != int(cpf[9]):
        raise ValueError("CPF ERROR")
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    resto = (soma * 10) % 11
    if resto == 10:
        resto = 0
    if resto != int(cpf[10]):
        raise ValueError("CPF ERROR")

    return stringCpf


def validarSexo(sexo) -> str:
    try:
        sexo = str(sexo)
    except:
        raise ValueError("SEXO ERROR")
    sexo = sexo.upper()
    if sexo != "FEMININO" and sexo != "MASCULINO":
        raise ValueError("SEXO ERROR")
    return sexo


def validarCep(cep) -> str:
    try:
        stringCep = str(cep)
        stringCep = stringCep.strip()
    except:
        raise ValueError("CEP ERROR")
    cep = "".join(filter(str.isdigit, stringCep))
    if len(cep) != 8:
        raise ValueError("CEP ERROR")
    return cep


def validarTipoDeLogradouro(tipo_de_logradouro) -> str:
    try:
        tipo_de_logradouro = str(tipo_de_logradouro)
    except:
        raise ValueError("TIPO DE LOGRADOURO ERROR")
    try:
        tipo_de_logradouro = TIPOS_LOGRADOUROS[
            remove_accentuation(tipo_de_logradouro.upper())
        ]
        return remove_accentuation(tipo_de_logradouro).upper()
    except:
        raise ValueError("TIPO DE LOGRADOURO ERROR")


def validarDataDoContrato(data):
    if isinstance(data, str):
        try:
            try:
                data = datetime.strptime(data, "%Y-%m-%d %H:%M:%S")
            except:
                try:
                    data = datetime.strptime(data, "%Y-%m-%d")
                except:
                    data = datetime.strptime(data, "%d/%m/%Y")

            day = str(data.day)
            month = str(data.month)
            year = str(data.year)
            if len(day) == 1:
                day = "0" + day
            if len(month) == 1:
                month = "0" + month
            return f"{day}/{month}/{year}"
        except ValueError:
            raise ValueError("DATA ERROR, FORMATO VÁLIDO = YYYY-MM-DD.")
    if isinstance(data, date):
        day = str(data.day)
        month = str(data.month)
        year = str(data.year)
        if len(day) == 1:
            day = "0" + day
        if len(month) == 1:
            month = "0" + month
        return f"{day}/{month}/{year}"
    else:
        raise ValueError("DATA ERROR, FORMATO VÁLIDO = YYYY-MM-DD.")


def validarLogradouro(logradouro) -> str:
    if logradouro.isdigit():
        return str(logradouro)
    try:

        logradouro = str(logradouro)
    except:
        raise ValueError("LOGRADOURO ERROR")
    return logradouro.title()


def validarNumero(numero):
    try:
        numero = int(numero)
        if numero == 0:
            numero = "sn"
    except:
        pass
    numero = str(numero)
    numero = numero.lower()

    return numero


def validarBairro(bairro):
    try:
        bairro = str(bairro)
    except:
        raise ValueError("BAIRRO ERROR")
    return bairro.title()


def validarCidade(cidade):
    try:
        cidade = str(cidade)
    except:
        raise ValueError("CIDADE ERROR")
    return cidade.title()


def validarUf(uf):
    try:
        uf = str(uf)
    except:
        raise ValueError("UF ERROR")
    return uf.upper()


ESTADOS_FORMULARIO_VALIDOS = frozenset({"CE", "MA", "CFT"})


def validar_dados_formulario(dados: dict) -> list[tuple[str, str]]:
    """
    Valida os dados coletados na tela inicial.
    Retorna lista de (campo, mensagem); campo identifica o widget na UI.
    Campos exclusivos do MA não são exigidos nos demais estados.
    """
    erros: list[tuple[str, str]] = []

    if not (dados.get("login") or "").strip():
        erros.append(("login", "Informe o login do CREA/CFT."))

    if not (dados.get("senha") or "").strip():
        erros.append(("senha", "Informe a senha."))

    planilha = (dados.get("dir_planilha") or "").strip()
    if not planilha or planilha == "...":
        erros.append(
            (
                "dir_planilha",
                "Selecione a planilha de clientes (botão Escolher Arquivo).",
            )
        )

    estado = (dados.get("estado") or "").strip().upper()
    if not estado:
        erros.append(("estado", "Selecione o estado: CE, MA ou CFT."))
    elif estado not in ESTADOS_FORMULARIO_VALIDOS:
        erros.append(("estado", f"Estado inválido: «{estado}». Use CE, MA ou CFT."))

    if not (dados.get("numero_art") or "").strip():
        erros.append(("numero_art", "Informe o número da ART."))

    if estado == "MA":
        if not (dados.get("nivel_atividade") or "").strip():
            erros.append(
                (
                    "nivel_atividade",
                    "Informe o nível de atividade (ex.: 16 ou 16 - Execução).",
                )
            )
        if not (dados.get("atividade_profissional") or "").strip():
            erros.append(
                (
                    "atividade_profissional",
                    "Informe a atividade profissional (ex.: 46 ou 46 - Execução de Instalação).",
                )
            )
        if not (dados.get("atuacao") or "").strip():
            erros.append(
                (
                    "atuacao",
                    "Informe a atuação (ex.: 15.9.6).",
                )
            )

    return erros


def validarValorDoPlano(valor_do_plano):
    try:
        valor_do_plano = str(valor_do_plano)
        valor_do_plano = (
            valor_do_plano.replace("R$", "").replace(":", "").replace(" ", "")
        )
    except:
        raise ValueError("VALOR DO PLANO ERROR")
    valor_do_plano = valor_do_plano.strip()
    valor_do_plano = valor_do_plano.replace(",", ".")
    try:
        valor_do_plano = float(valor_do_plano)
    except:
        raise ValueError("VALOR DO PLANO ERROR")
    valor_do_plano = f"{valor_do_plano:.2f}".replace(".", ",")
    return valor_do_plano
