# CRM Consig Next

Reconstrução moderna e isolada do CRM Consignado. A aplicação usa **React 19 + TypeScript + Vite** no cliente e **FastAPI + SQLite** na API.

## Garantia de isolamento

O CRM original em `C:\GitHub\Python\Práticas Avulsas\CRM Consignado` nunca é aberto para escrita. No primeiro início, a API cria `backend/data/crm.db` como cópia do banco original; depois, trabalha somente nessa cópia. Também é possível definir `CRM_SOURCE_DB` para importar outra cópia inicial.

## Executar

```powershell
# terminal 1
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000

# terminal 2
cd frontend
npm.cmd install
npm.cmd run dev
```

Abra `http://localhost:5173`. A API fica em `http://localhost:8000/docs`.

### PowerShell com execução de scripts bloqueada

Não é necessário alterar a política de segurança, nem executar `Activate.ps1`.
Use exatamente os comandos acima: `npm.cmd` evita o `npm.ps1`, e
`.\.venv\Scripts\python.exe` usa o ambiente virtual sem ativá-lo.

## Cobertura funcional

- Propostas, clientes por CPF/matrícula, busca e filtros
- Funil configurável, atualização de status, histórico e data real de encerramento
- Detalhe da proposta, anotações, anexos, dados financeiros e vínculo Portabilidade/Refin
- Agenda/tarefas, central operacional Hoje e notificações
- Propostas encerradas, dashboard, CSV/XLSX, importação e conversor de contatos
- Modelos e gerador de mensagens
- Simulador INSS e conversão da simulação em proposta

