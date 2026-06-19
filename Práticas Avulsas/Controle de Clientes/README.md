# Controle de Clientes

Projeto em Python voltado para controle de clientes, propostas e produção, com foco em organização de dados e acompanhamento de operações comerciais.

O sistema foi criado para apoiar rotinas de controle, consulta e atualização de informações, principalmente em contextos envolvendo propostas de crédito consignado.

## Objetivo

Facilitar o controle de clientes e propostas, substituindo controles manuais ou planilhas muito espalhadas.

O projeto busca ajudar em tarefas como:

* Organizar clientes;
* Consultar propostas;
* Filtrar informações por mês;
* Acompanhar status;
* Controlar produção;
* Apoiar análises comerciais;
* Trabalhar com dados vindos de planilhas.

## Funcionalidades

Dependendo da versão do projeto, podem existir recursos como:

* Cadastro de clientes;
* Controle de propostas;
* Filtros por mês;
* Filtros por banco;
* Filtros por status;
* Consulta por nome ou CPF;
* Organização de dados de produção;
* Leitura e escrita em planilhas Excel;
* Geração de relatórios simples;
* Interface local em Python.

## Tecnologias utilizadas

* Python 3
* Pandas
* OpenPyXL
* Tkinter ou CustomTkinter
* Manipulação de arquivos Excel

## Como executar

Abra a pasta do projeto no terminal.

Crie o ambiente virtual:

```bash
python -m venv .venv
```

Ative no Windows pelo CMD:

```bash
.venv\Scripts\activate.bat
```

Instale as dependências, se houver `requirements.txt`:

```bash
pip install -r requirements.txt
```

Execute o arquivo principal:

```bash
python main_controle_producao_consignado_v2_meses.py
```

Caso o nome do arquivo principal seja diferente, substitua pelo arquivo correto da versão que deseja executar.

## Organização dos dados

O projeto pode trabalhar com planilhas Excel contendo informações de clientes, propostas e produção.

Recomenda-se manter cópias de segurança das planilhas antes de realizar importações, alterações ou testes.

## Observações

Este projeto é uma ferramenta prática em evolução.

Algumas funcionalidades podem ter sido substituídas ou aprimoradas pelo projeto `CRM Consignado`, que possui uma estrutura mais completa em Flask + SQLite.

Mesmo assim, este projeto continua útil para testes, organização em planilhas e automações pontuais.

## Segurança

Não envie ao GitHub planilhas reais com dados de clientes, CPF, telefones, contratos ou informações comerciais sensíveis.

Evite subir arquivos como:

```text
*.xlsx
*.xls
*.csv
database.db
backups/
.venv/
```

Caso precise versionar exemplos, utilize arquivos fictícios ou anonimizados.
