# CRM Consignado Local

CRM local desenvolvido em **Python + Flask + SQLite** para controle de propostas de crédito consignado.

O sistema foi criado para auxiliar no acompanhamento de propostas, funil de atendimento, controle de comissões, anexos de clientes, histórico de alterações e organização da rotina comercial/administrativa.

Ele funciona localmente no computador e também pode ser acessado por outra pessoa na mesma rede local.

## Funcionalidades principais

* Cadastro de propostas de crédito consignado;
* Controle de clientes, CPF, telefone, banco, promotora e produto;
* Funil visual com cards arrastáveis;
* Etapas editáveis;
* Linha visual de etapas dentro da proposta;
* Alteração rápida de status clicando na etapa desejada;
* Separação entre propostas em andamento e propostas encerradas;
* Controle de propostas pagas, perdidas e canceladas;
* Tela de propostas encerradas com filtro por mês;
* Dashboard com resumo financeiro;
* Controle de comissão;
* Controle de valor disponível para saque;
* Controle de valor que ainda falta cair na promotora;
* Controle de valor já sacado;
* Backup automático do banco de dados;
* Modo claro e modo escuro;
* Ícone e título personalizados na aba do navegador.

## Campos da proposta

O CRM possui campos como:

* Nome do cliente;
* CPF;
* Telefone/WhatsApp;
* NB ou matrícula;
* Tipo de cliente;
* Banco atual;
* Banco destino;
* Banco digitado;
* Produto;
* Promotora;
* Benefício bloqueado;
* Status;
* Número da proposta;
* Número da portabilidade vinculada;
* Número do refinanciamento vinculado;
* Valor;
* Percentual de comissão;
* Comissão;
* Valor caiu na promotora;
* Valor já foi sacado;
* Margem após operação;
* Responsável;
* Previsão de saldo;
* Próxima ação;
* Anotações;
* Anexos.

## Funil de propostas

O funil exibe apenas propostas em andamento.

Quando uma proposta é marcada como:

```text
Pago
Perdido / Cancelado
```

ela sai do funil principal e passa para a tela **Encerradas**.

## Propostas encerradas

A tela **Encerradas** organiza propostas finalizadas e permite filtro por mês.

As propostas pagas são separadas por situação financeira:

```text
Pago - falta cair na promotora
Pago - disponível para saque
Pago - já sacado
Perdido / Cancelado
```

## Controle financeiro

O CRM permite controlar se a comissão da proposta já caiu na promotora e se já foi sacada.

A lógica utilizada é:

```text
Valor caiu na promotora: SIM/NÃO
Valor já foi sacado: SIM/NÃO
```

No dashboard, o sistema apresenta informações como:

* Comissão prevista;
* Comissão paga;
* Valor a sacar;
* Valor que falta cair na promotora;
* Valor já sacado;
* Total por status;
* Total por banco;
* Total por produto.

## Portabilidade e refinanciamento vinculado

O CRM permite vincular propostas de portabilidade e refinanciamento.

Dentro de uma proposta de portabilidade, existe a opção de criar um refinanciamento vinculado automaticamente.

Exemplo:

```text
Nº proposta da portabilidade: 12222333
Nº proposta do refinanciamento: 12222334
```

O sistema considera que o número do refinanciamento é o número da portabilidade + 1.

Ao criar o refinanciamento vinculado, o CRM aproveita os dados principais do cliente e cria uma nova proposta relacionada.

## Tela interna da proposta

A tela de detalhes da proposta possui uma interface organizada em abas internas:

```text
Resumo
Editar dados
Anotações
Anexos
Mensagens
Histórico
```

Na aba **Resumo**, aparecem informações importantes para consulta rápida:

* CPF com botão de copiar;
* Telefone com botão de copiar;
* Banco digitado;
* Número da proposta;
* Previsão de saldo;
* Valor;
* Comissão;
* Verificação diária;
* Propostas vinculadas;
* Botões rápidos para marcar como Pago ou Perdido.

## Verificação diária

O sistema possui controle de verificação diária.

Cada proposta pode ser marcada como verificada no dia.

No funil, os cards indicam visualmente:

```text
Laranja: ainda não verificada hoje
Verde: já verificada hoje
```

No dia seguinte, a proposta volta automaticamente para não verificada.

## Anotações da proposta

As observações foram organizadas como um histórico de anotações.

Cada anotação salva:

* Data;
* Hora;
* Texto da anotação.

Exemplo:

```text
18/06/2026 15:10
Cliente solicitou acompanhamento no INSS.

18/06/2026 12:45
Aguardando desbloqueio para pagamento do refin.
```

## Histórico de status

O CRM registra alterações de status da proposta.

Cada mudança salva:

* Data e hora;
* Status anterior;
* Novo status;
* Observação da alteração, quando informada.

## Anexos

O sistema permite anexar documentos dentro da proposta.

Ao enviar arquivos, o CRM cria uma pasta com o nome do cliente no diretório configurado para documentos.

Exemplo:

```text
C:\Users\tatia\OneDrive\DOCUMENTOS FACILITA - VILA VELHA\DANIEL\NOME DO CLIENTE
```

Os anexos podem ser enviados:

* Na criação da proposta;
* Dentro da tela de detalhes da proposta.

## Mensagens para WhatsApp

O CRM possui mensagens padrão para WhatsApp.

As mensagens podem utilizar variáveis da proposta, como:

```text
{nome}
{cpf}
{telefone}
{banco_atual}
{banco_destino}
{banco_digitado}
{produto}
{valor}
{troco}
{comissao}
{status}
```

As mensagens padrão podem ser editadas dentro do próprio sistema.

A partir das versões mais recentes, as mensagens editadas ficam salvas no banco de dados, evitando perda ao atualizar os arquivos do sistema.

## Pesquisa rápida

O sistema possui uma barra de pesquisa com sugestões.

É possível buscar por:

* Nome;
* CPF;
* Telefone.

Ao selecionar um resultado, o CRM abre diretamente a proposta.

## Importação de planilhas

O CRM possui importação compatível com planilhas de produção.

Colunas reconhecidas:

```text
DIA
NOME
STATUS
TELEFONE
CPF
BANCO
PRODUTO
VALOR
PONTOS
BLOQUEADO
PROMOTORA
SALDO PMT.
ACERTO
MOTIVO
```

Mapeamento principal:

```text
DIA          → Data de criação
NOME         → Nome do cliente
STATUS       → Status
TELEFONE     → Telefone
CPF          → CPF
BANCO        → Banco digitado
PRODUTO      → Produto
VALOR        → Valor
PONTOS       → Comissão
BLOQUEADO    → Benefício bloqueado
PROMOTORA    → Promotora
SALDO PMT.   → Valor caiu na promotora
ACERTO       → Valor já foi sacado
MOTIVO       → Observações/anotações
```

A importação permite escolher o mês desejado, evitando importar dados antigos sem necessidade.

## Backup automático

O CRM cria backups automáticos do banco de dados na pasta:

```text
backups/
```

O sistema mantém os backups mais recentes e evita acumular arquivos em excesso.

## Modo escuro

O sistema possui modo claro e modo escuro.

A preferência fica salva no navegador.

## Tecnologias utilizadas

* Python 3;
* Flask;
* SQLite;
* HTML;
* CSS;
* JavaScript;
* Pandas;
* OpenPyXL.

## Estrutura do projeto

```text
CRM Consignado/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── templates/
│   └── Arquivos HTML do sistema
│
├── static/
│   ├── style.css
│   ├── script.js
│   └── favicon.svg
│
├── data/
│   └── Arquivos auxiliares
│
└── backups/
    └── Backups automáticos do banco
```

## Instalação no Windows

Abra a pasta do projeto no VS Code ou no terminal.

Crie o ambiente virtual:

```bash
python -m venv .venv
```

Ative pelo CMD:

```bash
.venv\Scripts\activate.bat
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

## Acesso pela rede local

Para permitir acesso de outro computador na mesma rede, o Flask deve estar configurado assim no final do `app.py`:

```python
if __name__ == "__main__":
    with app.app_context():
        init_db()

    app.run(host="0.0.0.0", port=5000, debug=False)
```

No computador principal, descubra o IP com:

```bash
ipconfig
```

A outra pessoa acessa no navegador usando:

```text
http://IP-DO-COMPUTADOR:5000
```

Exemplo:

```text
http://192.168.18.103:5000
```

## Arquivos que não devem ser enviados ao GitHub

Este projeto pode trabalhar com dados sensíveis de clientes.

Não envie ao GitHub:

```text
database.db
*.db
*.sqlite
*.sqlite3
backups/
uploads/
anexos/
documentos/
clientes/
.venv/
__pycache__/
.env
```

## Exemplo de `.gitignore`

```gitignore
# Ambiente virtual
.venv/
venv/
env/

# Banco de dados local
database.db
*.db
*.sqlite
*.sqlite3

# Backups
backups/

# Anexos e documentos
uploads/
anexos/
documentos/
clientes/

# Cache Python
__pycache__/
*.pyc
*.pyo
*.pyd

# Configurações locais
.env
instance/

# VS Code
.vscode/

# Sistema operacional
.DS_Store
Thumbs.db
desktop.ini
```

## Segurança

Este sistema pode armazenar dados sensíveis, como CPF, telefone, documentos e informações comerciais.

Recomendações:

* Não publicar banco de dados real no GitHub;
* Não subir anexos de clientes;
* Não compartilhar backups com dados reais;
* Usar apenas em rede confiável;
* Adicionar login antes de disponibilizar fora da rede local;
* Evitar exposição direta na internet sem HTTPS e autenticação.

## Observação

Este CRM foi desenvolvido para uso local e operacional, com foco em praticidade, organização e controle de propostas de crédito consignado.

O projeto está em evolução e pode receber melhorias conforme novas necessidades surgirem.

## Autor

Desenvolvido por Daniel de Freitas Pinto como ferramenta prática para controle de propostas de crédito consignado e estudos em desenvolvimento de software.
