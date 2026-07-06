# CRM Consignado — teste local com NiceGUI

Esta é uma versão inicial e somente de leitura do Kanban do CRM Consignado.
Ela usa o arquivo `database.db` desta pasta, que é uma cópia independente do
banco do CRM Flask. O banco original não é acessado pela aplicação NiceGUI.

## Requisitos

- Python 3.10 ou mais recente
- Windows PowerShell

## Como rodar

Abra o PowerShell nesta pasta:

```powershell
cd "C:\GitHub\Python\Práticas Avulsas\CRM Consignado NiceGUI"
```

Crie e ative um ambiente virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instale a dependência:

```powershell
python -m pip install -r requirements.txt
```

Inicie o CRM:

```powershell
python main.py
```

Abra no navegador:

<http://127.0.0.1:8080>

Para encerrar, volte ao PowerShell e pressione `Ctrl+C`.

## O que esta versão mostra

- Etapas ativas cadastradas em `status_etapas`, na ordem configurada no banco.
- Propostas agrupadas pela coluna `status`.
- Nome, CPF, Valor, Comissão e Previsão de saldo em cada card.
- Quantidade e soma de comissão em cada etapa.
- Total geral de comissão no topo.
- Destaque verde discreto quando a previsão de saldo é a data atual.

O campo **Valor** corresponde à coluna `troco`, e **Previsão de saldo**
corresponde à coluna `data_retorno` do banco copiado.

## Segurança do banco original

O arquivo `database.py` resolve o banco sempre a partir desta própria pasta e
abre a cópia com `mode=ro` (somente leitura). Esta versão não contém comandos de
inserção, edição ou exclusão.

Se quiser atualizar os dados de teste no futuro, faça uma nova cópia do
`database.db` do Flask para esta pasta com os dois sistemas fechados. Nunca mova
nem renomeie o banco original.
