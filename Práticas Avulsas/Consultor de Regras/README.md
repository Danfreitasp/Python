# Consultor de Regras

Projeto em Python criado para auxiliar na consulta e organização de regras comerciais, especialmente em operações relacionadas a crédito consignado.

O objetivo é facilitar o acesso rápido a informações importantes, evitando consultas manuais em vários arquivos ou anotações separadas.

## Objetivo

Centralizar regras comerciais de forma simples e organizada, permitindo consultas rápidas durante o atendimento ou análise de propostas.

O projeto busca ajudar em situações como:

* Verificar regras por banco;
* Consultar condições de produtos;
* Evitar duplicidade de bancos ou regras;
* Organizar informações comerciais;
* Apoiar decisões durante o atendimento.

## Funcionalidades esperadas

Dependendo da versão do projeto, o sistema pode conter recursos como:

* Cadastro ou consulta de bancos;
* Consulta de regras por banco;
* Filtros por produto ou condição;
* Organização de informações comerciais;
* Interface local simples;
* Leitura de dados a partir de arquivos ou planilhas.

## Tecnologias utilizadas

* Python 3
* Bibliotecas padrão do Python
* Possível uso de interface gráfica com Tkinter ou CustomTkinter
* Possível uso de arquivos locais para armazenamento de dados

## Como executar

Abra a pasta do projeto no terminal.

Crie um ambiente virtual:

```bash
python -m venv .venv
```

Ative o ambiente virtual no Windows pelo CMD:

```bash
.venv\Scripts\activate.bat
```

Instale as dependências, se existir um arquivo `requirements.txt`:

```bash
pip install -r requirements.txt
```

Execute o arquivo principal do projeto:

```bash
python nome_do_arquivo.py
```

Substitua `nome_do_arquivo.py` pelo nome do arquivo principal do projeto.

## Estrutura sugerida

```text
Consultor de Regras/
│
├── README.md
├── requirements.txt
├── arquivo_principal.py
└── dados/
```

## Observações

Este projeto está em desenvolvimento e pode receber ajustes conforme novas regras e necessidades forem surgindo.

A proposta é manter uma ferramenta simples, prática e fácil de atualizar.

## Segurança

Evite subir ao GitHub arquivos com informações sensíveis, planilhas internas, dados de clientes ou regras comerciais privadas.

Use o `.gitignore` para bloquear arquivos locais e dados confidenciais.
