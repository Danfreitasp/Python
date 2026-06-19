\# CRM Consignado Local



CRM local desenvolvido em \*\*Python + Flask + SQLite\*\* para controle de propostas de crédito consignado.



O sistema foi criado para auxiliar no acompanhamento de propostas, funil de atendimento, controle de comissões, anexos de clientes e histórico de alterações, funcionando localmente no computador ou em rede local.



\## Funcionalidades



\* Cadastro de propostas de consignado;

\* Controle de clientes, CPF, telefone, banco, promotora e produto;

\* Funil visual com cards arrastáveis;

\* Etapas editáveis;

\* Separação entre propostas em andamento e encerradas;

\* Controle de propostas pagas, perdidas e canceladas;

\* Controle financeiro de comissão;

\* Campos para:



&#x20; \* Comissão;

&#x20; \* Percentual de comissão;

&#x20; \* Valor caiu na promotora;

&#x20; \* Valor já foi sacado;

&#x20; \* Benefício bloqueado;

&#x20; \* Banco digitado;

&#x20; \* Número da proposta;

&#x20; \* Proposta de portabilidade vinculada;

&#x20; \* Proposta de refinanciamento vinculada;

\* Criação automática de refinanciamento vinculado à portabilidade;

\* Histórico de status;

\* Anotações por proposta em formato de log;

\* Mensagens padrão para WhatsApp editáveis pelo sistema;

\* Upload de anexos dos clientes;

\* Criação automática de pasta do cliente para documentos;

\* Pesquisa rápida por nome, CPF ou telefone;

\* Botão para copiar CPF;

\* Verificação diária de propostas com indicador visual;

\* Dashboard com resumo financeiro;

\* Filtro por mês em propostas encerradas;

\* Backup automático do banco de dados;

\* Modo claro e modo escuro.



\## Tecnologias utilizadas



\* Python 3

\* Flask

\* SQLite

\* HTML

\* CSS

\* JavaScript



\## Estrutura do projeto



```text

CRM Consignado/

│

├── app.py

├── requirements.txt

├── README.md

├── .gitignore

│

├── templates/

│   └── arquivos HTML do sistema

│

├── static/

│   ├── style.css

│   └── script.js

│

├── data/

│   └── arquivos auxiliares

│

└── backups/

&#x20;   └── backups automáticos do banco

```



\## Arquivos que não devem ser enviados ao GitHub



Este projeto trabalha com dados sensíveis de clientes. Por isso, alguns arquivos e pastas devem ficar apenas no computador local:



```text

database.db

backups/

uploads/

anexos/

.venv/

\_\_pycache\_\_/

```



Nunca envie ao GitHub arquivos com CPF, documentos, contratos, planilhas reais ou banco de dados com informações de clientes.



\## Instalação no Windows



Abra a pasta do projeto no VS Code.



Crie o ambiente virtual:



```bash

python -m venv .venv

```



Ative o ambiente virtual pelo CMD:



```bash

.venv\\Scripts\\activate.bat

```



Instale as dependências:



```bash

pip install -r requirements.txt

```



Execute o sistema:



```bash

python app.py

```



Acesse no navegador:



```text

http://127.0.0.1:5000

```



\## Acesso pela rede local



Para outra pessoa acessar o CRM no mesmo Wi-Fi, o sistema deve estar rodando no computador principal.



No arquivo `app.py`, o Flask deve estar configurado com:



```python

app.run(host="0.0.0.0", port=5000, debug=False)

```



Depois, descubra o IP do computador principal com:



```bash

ipconfig

```



A outra pessoa acessa pelo navegador usando:



```text

http://IP-DO-COMPUTADOR:5000

```



Exemplo:



```text

http://192.168.18.103:5000

```



\## Banco de dados



O sistema utiliza SQLite.



O arquivo principal do banco é:



```text

database.db

```



Esse arquivo é criado automaticamente ao iniciar o sistema, caso não exista.



\## Backup automático



O sistema cria backups automáticos do banco de dados na pasta:



```text

backups/

```



Esses backups não devem ser enviados ao GitHub.



\## Anexos



Os documentos dos clientes são salvos em uma pasta local configurada no sistema.



Os anexos não devem ser enviados ao GitHub por conterem dados sensíveis.



\## Uso recomendado



Este CRM foi pensado para uso local ou em rede privada, por poucas pessoas.



Para uso externo pela internet, recomenda-se adicionar antes:



\* Login com usuário e senha;

\* HTTPS;

\* Controle de permissões;

\* Banco de dados mais robusto;

\* Hospedagem segura;

\* Política de backup externo.



\## Aviso de segurança



Este projeto pode conter ou manipular dados sensíveis, como CPF, telefone e documentos de clientes.



Antes de publicar qualquer versão no GitHub, confirme que o banco de dados, anexos, backups e planilhas reais não estão sendo enviados.



\## Autor



Desenvolvido para uso em operação de crédito consignado.



