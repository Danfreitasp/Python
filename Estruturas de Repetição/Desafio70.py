# Desafio 070 - Programa que lê preço de vários produtos.
valor = 0
mil = 0
barato = str
barato1 = 0
primeira = 0
while True:
    produto = str(input("Digite o nome do produto: "))
    preco = float(input("Digite o preço do produto: "))
    if primeira == 0:
        barato = produto
        barato1 = preco
        primeira = 1
    if preco > 1000:
        mil += 1
    valor += preco
    if preco < barato1:
        barato = produto
    continuar = str(input("Deseja continuar? [S/N]: ")).strip().upper()
    if continuar == "N":
        break
print(f"Você gastou {valor:.2f} reais, {mil} produtos foram mais de 1000.00 reais e o produto mais barato foi {barato}.")