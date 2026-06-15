# Consulta de Regras de Portabilidade

Programa em Python para consultar regras de portabilidade usando Excel editável.

## Como instalar

```bash
pip install -r requirements.txt
```

## Como executar

```bash
python main.py
```

## Como usar

1. Digite o banco de origem.
2. Escolha a sugestão exibida.
3. Informe a quantidade de parcelas pagas.
4. Escolha o tipo da origem:
   - `BANCO_DE_REDE`
   - `BANCO_ORIGEM_CORBAN`
5. Clique em `Consultar Bancos Disponíveis`.

## Importante

- Não use código junto ao nome do banco.
- Use `AGIBANK`, não `121 AGIBANK`.
- Use `OLÉ`, não `169 OLÉ`.
- Use `C6`, não `C6 BANK`.
- O programa remove códigos bancários do começo do nome automaticamente.
- O programa não mostra o mesmo banco como destino. Ex.: se a origem for C6, destino C6 não aparece.

## Excel inválido

Se o arquivo `regras_portabilidade.xlsx` estiver quebrado, o programa faz backup automaticamente e recria um modelo correto.

## Gerar EXE

```bash
pyinstaller --onefile --windowed --name ConsultaPortabilidade main.py
```

Depois coloque o `regras_portabilidade.xlsx` na mesma pasta do `.exe`.
