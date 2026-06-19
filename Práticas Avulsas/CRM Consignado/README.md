# CRM Consignado Local

CRM local em Flask + SQLite para controle de propostas de consignado.

## Recursos principais

- Cadastro, edição e consulta de propostas.
- Funil Kanban com arrastar e soltar.
- Funil principal mostra apenas propostas em andamento.
- Propostas `Pago` e `Perdido / Cancelado` saem do funil principal e ficam no menu **Encerradas**.
- Menu **Encerradas** com coluna verde para pagas e vermelha para perdidas.
- Histórico automático de status.
- Dashboard mensal.
- Importação e exportação CSV/XLSX.
- Importação compatível com planilhas com colunas como DIA, NOME, STATUS, TELEFONE, CPF, BANCO, PRODUTO, VALOR, PONTOS, BLOQUEADO, PROMOTORA e MOTIVO.
- Na importação, `PONTOS` vira `Comissão` e `MOTIVO` vira `Observações`.
- Importação mensal: escolha o mês antes de importar. Para Excel com abas mensais, o sistema prioriza a aba do mês escolhido, como JUNHO.

## Como rodar no Windows

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
python app.py
```

Acesse:

```text
http://127.0.0.1:5000
```

## Como atualizar mantendo seus dados

Substitua:

```text
app.py
requirements.txt
README.md
templates
static
data
```

Não substitua:

```text
database.db
.venv
```

Se apagar o `database.db`, o sistema cria um banco vazio automaticamente ao iniciar.

## Atualização v8

- Adicionado campo **Banco digitado**.
- Na importação da planilha de produção, a coluna **BANCO** agora entra como **Banco digitado**.
- Para produtos de portabilidade/refinanciamento de portabilidade, se o Banco destino estiver vazio, o sistema usa o Banco digitado como Banco destino.
- Os cards do funil passam a mostrar Banco digitado.
- O topo de cada etapa do funil mostra a quantidade de propostas e a soma das comissões daquela etapa.

## Atualização v9

- Observações agora funcionam como **Anotações da proposta**, em formato de diário/log.
- Cada nova anotação salva data e hora automaticamente.
- Observações antigas/importadas são migradas automaticamente para a primeira anotação da proposta.
- A tela de detalhes ganhou um formulário rápido para adicionar novas anotações sem apagar as anteriores.
- O histórico de status continua separado, para mostrar mudanças de etapa e atualizações do fluxo.


## v12

- Adicionada área de **Anexos iniciais** na tela **Nova proposta**.
- Agora é possível cadastrar a proposta e enviar documentos no mesmo formulário.
- Ao salvar, o CRM cria automaticamente a pasta do cliente dentro da pasta base de anexos e registra os arquivos na proposta.
- A área de anexos na tela de detalhes continua funcionando para novos envios depois do cadastro.


## Versão 13

- Adicionado botão **Excluir lead** na tela de detalhes da proposta.
- Adicionado botão **Excluir lead** diretamente nos cards do funil.
- A exclusão remove a proposta, histórico, anotações e registros de anexos.
- Quando possível, os arquivos anexados também são apagados da pasta do cliente; se algum arquivo estiver aberto ou bloqueado pelo Windows, o CRM avisa.


## v14

- Removido o botão de exclusão dos cards do funil para evitar exclusões acidentais.
- A exclusão de lead/proposta permanece disponível apenas na tela de detalhes da proposta.


## v15

- Adicionado campo **% comissão** no cadastro e edição da proposta.
- Ao informar a porcentagem, o CRM calcula automaticamente a comissão com base no campo **Valor**.
- O campo **Comissão** continua editável para ajustes manuais.
- O banco antigo é atualizado automaticamente criando a coluna `comissao_percentual`.


## Versão 17

- Ajustado o botão de copiar CPF/mensagens para funcionar melhor em acesso por IP local, como `http://192.168.x.x:5000`.
- Quando o navegador bloquear a API moderna de área de transferência, o sistema usa um método alternativo com campo temporário.

## v18 - Vinculação manual de Portabilidade e Refinanciamento

Esta versão adiciona campos para vincular manualmente propostas de portabilidade e refinanciamento por número de proposta.

Novos campos:

- Nº proposta: número da proposta atual.
- Nº proposta da port vinculada: use no refinanciamento para informar a portabilidade relacionada.
- Nº proposta do refin vinculado: use na portabilidade para informar o refinanciamento relacionado.

Na tela de detalhes, o CRM mostra um bloco "Propostas vinculadas" com os vínculos encontrados.

Exemplo de uso:

1. Abra a proposta de Portabilidade e preencha o Nº proposta dela.
2. Abra a proposta de Refinanciamento e preencha o Nº proposta da port vinculada.
3. Ao abrir qualquer uma das duas, o bloco de propostas vinculadas mostrará a outra proposta.

O banco antigo é atualizado automaticamente ao iniciar o sistema.


## Correção v20

- Corrigido erro ao salvar edição da proposta: quantidade incorreta de parâmetros no UPDATE do SQLite.


## Novidade v21

- Adicionado botão **Criar refin vinculado** dentro da proposta de Portabilidade.
- O CRM usa o número da proposta da portabilidade e gera o número do refinanciamento como **número da port + 1**.
- O refinanciamento criado copia dados principais do cliente, banco digitado, promotora, telefone, CPF e responsável.
- A portabilidade recebe automaticamente o número do refin vinculado e o refin recebe o número da port vinculada.
- Se já existir uma proposta com o número do refinanciamento, o CRM apenas cria o vínculo e abre a proposta existente.


## v22 - Mensagens preservadas

A partir desta versão, as mensagens padrão editadas no CRM são salvas no `database.db`. Assim, ao atualizar o sistema substituindo as pastas `templates`, `static` e `data`, as mensagens personalizadas não são perdidas. O arquivo `data/modelos_mensagens.json` fica apenas como fallback/backup legível.


## v23 - Modo escuro

- Adicionado botão no topo para alternar entre modo claro e modo escuro.
- A preferência fica salva no navegador usando `localStorage`.
- Não altera o banco de dados e não exige nova dependência.

### Atualização

Substitua `app.py`, `requirements.txt`, `README.md`, `templates`, `static` e `data`.

Não substitua `database.db`, `.venv` nem a pasta `backups`.


## Identidade visual da aba

A versão atual usa o nome **CRM Consig** no título do navegador e inclui um favicon próprio em `static/favicon.svg`.

Isso ajuda a identificar rapidamente a aba do sistema quando há várias abas abertas no navegador.


## v25 - Linha de etapas na proposta

- Adicionada uma linha visual de etapas dentro da tela de detalhes da proposta.
- Cada etapa aparece como um círculo clicável.
- Ao clicar em uma etapa, a proposta muda diretamente para aquele status.
- Etapas anteriores ficam em verde claro e a etapa atual fica em verde destacado.
- Funciona também no modo escuro.


## v26

Ajustes de interface na tela de detalhes da proposta:

- Removida a linha visual de etapas, que estava deixando a tela poluída;
- Adicionada a seção recolhível **Editar dados desta proposta** dentro da própria proposta;
- A edição completa continua disponível pelo botão **Editar**, mas agora também pode ser feita sem sair da tela de detalhes.

## Atualização v27

- Reorganiza a tela de detalhes da proposta em abas internas: Resumo, Editar dados, Anotações, Anexos, Mensagens e Histórico.
- Restaura a linha visual de etapas clicável dentro da proposta.
- Remove o formulário tradicional de mudança de status para reduzir poluição visual.
- Mantém a edição rápida dos dados dentro da própria proposta.
- Move informações menos usadas para a área recolhível de dados completos.


## Atualização v30

- Adicionada área de **Anotações recentes** no resumo da proposta, abaixo de Valor e Comissão.
- A aba **Anotações** continua disponível para visualizar o histórico completo e adicionar novos registros.

## Atualização v31

- Adicionado campo **Endereço do cliente**.
- Adicionado campo **Dados bancários do cliente**.
- Os novos campos ficam em **Dados completos da proposta** e também podem ser editados na aba **Editar dados**.
- Os campos foram incluídos na criação, edição, importação, exportação e migração automática do banco.

## Atualização v32

- Adicionada base de **Clientes** separada das propostas.
- O cliente é identificado por **CPF + NB/Matrícula**.
- Ao criar ou editar uma proposta, o CRM cria/atualiza automaticamente o cadastro do cliente.
- Ao digitar um CPF na tela de cadastro/edição, o CRM consulta matrículas já cadastradas.
- Se houver clientes encontrados, o campo de matrícula mostra opções como:
  - Matrícula 1
  - Matrícula 2
  - Cadastrar nova matrícula
- Ao selecionar uma matrícula cadastrada, o CRM preenche automaticamente:
  - Nome
  - Telefone
  - Tipo de cliente
  - Endereço
  - Dados bancários
- O campo **Benefício bloqueado** não é reaproveitado do cliente, porque pode mudar de uma proposta para outra.
- A importação de planilhas também alimenta a base de clientes automaticamente.
- Propostas antigas são migradas automaticamente para a tabela de clientes ao iniciar o sistema.
