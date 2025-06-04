# 📝 Cadastro ART - Automação de Cadastro de ART's

Automação desenvolvida em Python para cadastro de ART's (Anotações de Responsabilidade Técnica) nos sistemas do CREA-CE e CREA-MA.

![Screenshot da Interface](docs/interface_screenshot.png)

## 🚀 Funcionalidades

- ✔️ Cadastro automatizado de ART's
- 🌐 Suporte aos sistemas:
  - CREA-CE (https://servicos-crea-ce.sitac.com.br)
  - CREA-MA (https://sistemas.crea-ma.gov.br)
- 🖥️ Interface gráfica com PyQt6
- 📊 Processamento de planilhas Excel
- 🔄 Gerenciamento automático de drivers

## 📦 Pré-requisitos

- Python 3.12+
- Google Chrome (versão compatível)
- Conta ativa no CREA
- Planilha Excel no formato especificado

## 🛠️ Instalação

1. Clone o repositório:

```bash
git clone https://github.com/seu-usuario/cadastro-art.git
```

2. Instale as Dependências:

```bash
cd cadastro-art
```

```bash
pip install pipenv
```

```bash
pipen install
```

```bash
python -m webdriver_manager chrome
```

## ▶️ Como Usar

```bash
python app/main.py
```

## 🔧 Gerando o Executável

Para gerar o executável do programa:

```bash
pip install pyinstaller
pyinstaller build.spec
```

O executável será gerado na pasta `dist/`.
