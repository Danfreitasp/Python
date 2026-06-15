# Consulta de Regras de Portabilidade

Programa em Python para consultar regras de portabilidade de bancos usando um Excel editável como base de dados.

As regras foram organizadas a partir do PDF enviado: `REGRA DE PMT PAGA (6) (1).pdf`.

## Arquivos do projeto

- `main.py`: programa principal com interface gráfica.
- `regras_portabilidade.xlsx`: base editável com as regras.
- `requirements.txt`: dependências.
- `README.md`: instruções.

## Como instalar

No terminal, dentro da pasta do projeto, rode:

```bash
pip install -r requirements.txt
```

## Como executar

```bash
python main.py
```

## Como usar

1. Digite ou selecione o banco de origem.
2. Informe a quantidade de parcelas pagas.
3. Escolha o tipo da origem:
   - `BANCO_DE_REDE`
   - `BANCO_ORIGEM_CORBAN`
4. Clique em `Consultar Bancos Disponíveis`.

O campo `Banco de origem` é pesquisável: comece a digitar o nome do banco e clique em uma sugestão.

O programa mostrará:
- Banco destino
- Status
- Parcelas mínimas
- Regra
- Observação

## Como editar as regras

Abra o arquivo `regras_portabilidade.xlsx` e edite a aba `Regras`.

Cada linha representa uma regra.

Colunas principais:

| Coluna | Uso |
|---|---|
| Banco_Destino | Banco onde você pode digitar a proposta |
| Banco_Origem | Banco de onde o contrato está vindo |
| Categoria_Origem | Tipo de regra |
| Minimo_Parcelas_Pagas | Quantidade mínima de parcelas pagas |
| Status | SIM, NAO ou CONDICIONAL |
| Regra_Descricao | Descrição da regra |
| Observacao | Observação adicional |

Depois de editar o Excel, salve e clique em `Recarregar Regras` no programa.

## Como transformar em .exe

No terminal, dentro da pasta do projeto:

```bash
pyinstaller --onefile --windowed --name ConsultaPortabilidade main.py
```

O executável será criado na pasta:

```bash
dist
```

Importante: deixe o arquivo `regras_portabilidade.xlsx` na mesma pasta do `.exe`, pois o programa lê esse arquivo como base editável.

## Observações

- O programa trata diferenças de acento, maiúsculas/minúsculas, espaços e algumas variações de nomes, como `121 AGIBANK` e `AGIBANK`.
- Regras específicas têm prioridade sobre regras genéricas.
- Bancos com status `NAO` só aparecem se a opção `Mostrar recusados/insuficientes` estiver marcada.
- Regras condicionais aparecem como `CONDICIONAL`, indicando necessidade de consultar gerente/comercial/suporte.
