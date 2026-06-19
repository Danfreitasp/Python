# Práticas Avulsas em Python

Este repositório reúne projetos práticos, estudos e ferramentas desenvolvidas em Python.

A proposta é centralizar aplicações criadas para aprendizado, automação de tarefas e apoio em rotinas administrativas, comerciais e pessoais. Os projetos variam desde ferramentas simples de produtividade até sistemas locais mais completos.

## Projetos

### Consultor de Regras

Ferramenta para consulta e organização de regras comerciais.

Objetivo principal:

* Centralizar regras de bancos e produtos;
* Facilitar consultas rápidas;
* Evitar duplicidade e confusão entre bancos;
* Apoiar decisões durante atendimento ou análise de propostas.

---

### Controle de Clientes

Projeto voltado para controle de clientes, propostas e produção.

Objetivo principal:

* Organizar informações de clientes;
* Controlar propostas;
* Trabalhar com planilhas;
* Filtrar dados por mês, banco, produto ou status;
* Apoiar análises comerciais e acompanhamento de produção.

---

### CRM Consignado

Sistema local em Flask + SQLite para controle de propostas de crédito consignado.

Principais recursos:

* Cadastro de propostas;
* Funil visual;
* Controle de comissões;
* Anexos;
* Histórico de status;
* Anotações por proposta;
* Dashboard;
* Mensagens padrão;
* Backup automático;
* Modo escuro.

> Este projeto possui README próprio dentro da pasta `CRM Consignado`.

---

### Gerador de Mensagem

Ferramenta para gerar mensagens comerciais padronizadas.

Objetivo principal:

* Criar mensagens para clientes;
* Padronizar textos de atendimento;
* Reduzir erros manuais;
* Facilitar cópia de mensagens para WhatsApp;
* Apoiar rotinas de contato comercial.

---

### Gerenciador de Senhas Local

Aplicação local para armazenamento e organização de senhas.

Objetivo principal:

* Cadastrar senhas de sites, sistemas e contas;
* Armazenar dados localmente;
* Utilizar senha mestra;
* Proteger informações sensíveis;
* Servir como estudo prático de interface gráfica, arquivos locais e segurança básica.

## Tecnologias utilizadas

Os projetos podem utilizar diferentes tecnologias, dependendo da proposta de cada um:

* Python 3;
* Flask;
* SQLite;
* HTML;
* CSS;
* JavaScript;
* Pandas;
* OpenPyXL;
* Tkinter;
* CustomTkinter;
* Bibliotecas de criptografia.

## Estrutura do repositório

```text
Práticas Avulsas/
│
├── Consultor de Regras/
│   └── Consulta e organização de regras comerciais
│
├── Controle de Clientes/
│   └── Controle de clientes, propostas e produção
│
├── CRM Consignado/
│   └── CRM local para propostas de crédito consignado
│
├── Gerador de Mensagem/
│   └── Geração de mensagens comerciais padronizadas
│
├── Gerenciador de Senhas Local/
│   └── Gerenciador local de senhas
│
├── .gitignore
└── README.md
```

## Como executar os projetos

Cada projeto pode ter suas próprias dependências e forma de execução.

De forma geral, entre na pasta do projeto desejado:

```bash
cd "Nome do Projeto"
```

Crie um ambiente virtual:

```bash
python -m venv .venv
```

Ative no Windows usando CMD:

```bash
.venv\Scripts\activate.bat
```

Instale as dependências, se houver `requirements.txt`:

```bash
pip install -r requirements.txt
```

Execute o arquivo principal:

```bash
python nome_do_arquivo.py
```

Em projetos Flask, normalmente a execução será:

```bash
python app.py
```

## Segurança

Alguns projetos podem manipular dados sensíveis, como clientes, CPF, documentos, senhas, bancos de dados locais ou planilhas reais.

Arquivos sensíveis não devem ser enviados ao GitHub.

Exemplos de arquivos ignorados:

```text
database.db
*.db
*.sqlite
*.sqlite3
.venv/
backups/
uploads/
anexos/
documentos/
clientes/
__pycache__/
.env
```

## Observações

Este repositório contém projetos em evolução.

Alguns códigos podem ter sido criados para estudo, testes ou uso pessoal, e podem receber melhorias conforme novas necessidades surgirem.

## Autor

Desenvolvido por Daniel de Freitas Pinto como parte dos estudos em Engenharia de Software e aplicações práticas em rotinas administrativas, comerciais e pessoais.
