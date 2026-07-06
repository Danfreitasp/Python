# CRM Consignado

Aplicacao local em Python com NiceGUI e SQLite para controle de propostas e simulacoes.

## Como rodar

```powershell
cd "C:\GitHub\Python\Práticas Avulsas\CRM Consignado NiceGUI"
python app.py
```

Abra no navegador:

<http://127.0.0.1:8080>

## O que o projeto inclui

- Kanban local de propostas.
- Cadastro, edicao, exclusao e detalhes de propostas.
- Nova area de Simulacao com calculo em tempo real.
- Conversao de simulacao em proposta.
- Mensagem pronta para WhatsApp.
- Banco SQLite local com migracao automatica da tabela `simulacoes`.

## Banco de dados

O projeto usa um arquivo SQLite de trabalho local gerado a partir da base existente. O arquivo principal do CRM continua dentro da pasta do projeto e nao precisa ser publicado no GitHub.

## Observacao tecnica

Este checkout usa NiceGUI no lugar de Flask/templates. Por isso a interface principal esta em `main.py`, e `app.py` e apenas um wrapper de inicializacao.
