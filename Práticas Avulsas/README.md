# Práticas Avulsas em Python

Repositório com projetos práticos desenvolvidos em Python para automatizar tarefas do dia a dia, principalmente voltadas para atendimento, consulta de regras e geração de mensagens comerciais.

## Projetos

### Consultor de Regras

Programa em Python para consulta de regras de portabilidade bancária.

O sistema utiliza uma planilha Excel como base de dados editável, permitindo cadastrar e consultar regras de bancos de forma simples.

#### Funcionalidades

* Consulta de bancos disponíveis para portabilidade.
* Leitura das regras a partir de arquivo Excel.
* Campo pesquisável para banco de origem.
* Filtro por tipo de origem:

  * Banco de rede
  * Origem corban
* Validação de quantidade de parcelas pagas.
* Exibição de bancos disponíveis, condicionais ou recusados.
* Tratamento de nomes duplicados ou variações, como:

  * C6 / C6 Bank
  * Agibank / 121 Agibank
  * Olé / 169 Olé
* Botão para abrir e editar a planilha de regras.
* Recriação automática da planilha modelo caso o arquivo esteja inválido.

#### Tecnologias usadas

* Python
* CustomTkinter
* Pandas
* OpenPyXL

---

### Gerador de Mensagem

Programa em Python para gerar mensagens comerciais de forma mais rápida e padronizada.

O objetivo é facilitar a criação de textos para atendimento, propostas e contato com clientes, reduzindo erros de digitação e agilizando o trabalho.

#### Funcionalidades

* Geração automática de mensagens.
* Campos editáveis para dados do cliente.
* Padronização do texto comercial.
* Botão para copiar a mensagem gerada.
* Possibilidade de alterar o modelo de mensagem.
* Interface simples para uso no dia a dia.

#### Tecnologias usadas

* Python
* CustomTkinter / Tkinter
* Manipulação de arquivos de texto

---

## Como executar os projetos

Entre na pasta do projeto desejado pelo terminal.

Exemplo:

```bash
cd "Consultor de Regras"
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Execute o programa:

```bash
python main.py
```

> Dependendo do projeto, o arquivo principal pode ter outro nome. Verifique os arquivos `.py` dentro de cada pasta.

---

## Como gerar executável `.exe`

Para transformar um projeto em executável, instale o PyInstaller:

```bash
pip install pyinstaller
```

Depois, dentro da pasta do projeto, execute:

```bash
pyinstaller --onefile --windowed main.py
```

O executável será criado dentro da pasta:

```bash
dist
```

Caso o projeto utilize arquivos externos, como Excel ou `.txt`, mantenha esses arquivos na mesma pasta do executável.

---

## Objetivo do repositório

Este repositório tem como objetivo reunir pequenos projetos e automações desenvolvidos para estudo e uso prático, principalmente com foco em:

* Automação de tarefas repetitivas.
* Criação de interfaces gráficas simples.
* Organização de regras comerciais.
* Geração de mensagens padronizadas.
* Prática de desenvolvimento em Python.

---

## Observação

Os projetos deste repositório foram criados para fins de estudo e produtividade pessoal.
As regras, mensagens e dados utilizados podem precisar de ajustes conforme o uso real e as políticas de cada instituição.
