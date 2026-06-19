# Gerador de Mensagem

Projeto em Python criado para gerar mensagens comerciais padronizadas de forma rápida e organizada.

A ferramenta foi pensada para apoiar rotinas de atendimento, principalmente em contatos com clientes via WhatsApp, reduzindo retrabalho e evitando erros na digitação manual.

## Objetivo

Facilitar a criação de mensagens personalizadas para clientes, usando campos preenchidos pelo usuário e modelos de texto pré-definidos.

O projeto ajuda em tarefas como:

* Gerar mensagens comerciais;
* Padronizar comunicação;
* Evitar erros de português ou informações incompletas;
* Copiar textos rapidamente para envio;
* Agilizar contatos com clientes;
* Manter modelos de mensagens reutilizáveis.

## Possíveis usos

O sistema pode ser utilizado para gerar mensagens relacionadas a:

* Portabilidade;
* Refinanciamento;
* Redução de parcela;
* Liberação de troco;
* Solicitação de documentos;
* Andamento de proposta;
* Recontato de cliente;
* Avisos comerciais em geral.

## Funcionalidades

Dependendo da versão do projeto, a ferramenta pode conter:

* Campos para preencher dados do cliente;
* Modelos de mensagens;
* Geração automática do texto final;
* Botão para copiar mensagem;
* Interface gráfica local;
* Possibilidade de editar mensagem padrão;
* Salvamento de modelos em arquivo local.

## Tecnologias utilizadas

* Python 3;
* Tkinter ou CustomTkinter;
* Manipulação de arquivos locais;
* Interface gráfica desktop.

## Como executar

Abra a pasta do projeto no terminal.

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

Substitua `nome_do_arquivo.py` pelo arquivo principal do projeto.

## Estrutura sugerida

```text
Gerador de Mensagem/
│
├── README.md
├── requirements.txt
├── arquivo_principal.py
└── modelos/
```

## Observações

Este projeto foi criado como ferramenta prática para uso diário e também como exercício de programação em Python.

O código pode evoluir para incluir novos modelos, novas telas e integração com outros sistemas locais.

## Segurança

Evite subir ao GitHub arquivos contendo dados reais de clientes, CPF, telefone ou mensagens com informações sensíveis.

Caso use exemplos no projeto, prefira dados fictícios.
