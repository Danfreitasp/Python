# Gerenciador de Senhas Local

Aplicação local em Python para cadastro, organização e consulta de senhas pessoais ou de sistemas.

O projeto foi criado como estudo prático de interface gráfica, armazenamento local e segurança básica em aplicações desktop.

## Objetivo

Criar um gerenciador de senhas simples, local e funcional, permitindo armazenar dados de acesso sem depender de serviços online.

O sistema tem como foco:

* Praticar desenvolvimento de aplicações desktop;
* Trabalhar com senha mestra;
* Organizar credenciais;
* Proteger informações salvas localmente;
* Criar uma interface simples para consulta e edição.

## Funcionalidades esperadas

Dependendo da versão do projeto, o sistema pode conter:

* Tela de login com senha mestra;
* Cadastro de credenciais;
* Consulta de senhas salvas;
* Edição de registros;
* Exclusão de registros;
* Cópia de senha para área de transferência;
* Campos como:

  * Site ou sistema;
  * Login ou e-mail;
  * Senha;
  * Categoria;
  * URL;
  * Observações;
  * Data de criação;
  * Data de alteração;
* Armazenamento local;
* Criptografia dos dados salvos.

## Tecnologias utilizadas

* Python 3;
* Tkinter ou CustomTkinter;
* Arquivos locais;
* Possível uso da biblioteca `cryptography`;
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

## Segurança

Este projeto lida com informações sensíveis.

Não envie ao GitHub arquivos contendo senhas reais, banco de dados local, cofres criptografados ou chaves de segurança.

Arquivos que devem ser mantidos fora do versionamento:

```text
*.enc
*.db
*.sqlite
vault/
senhas_vault.enc
chave.key
.env
.venv/
```

## Aviso importante

Este projeto é uma aplicação local de estudo e uso pessoal.

Para uso real com senhas importantes, recomenda-se revisar cuidadosamente:

* Criptografia;
* Geração de chave;
* Proteção da senha mestra;
* Backup seguro;
* Tratamento de erros;
* Bloqueio de tela;
* Segurança do computador onde o sistema será usado.

## Observações

O projeto pode evoluir com melhorias de segurança, interface e organização dos dados.

A proposta inicial é manter uma ferramenta simples, local e fácil de entender.
