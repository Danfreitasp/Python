# Desafio 065 - Programa que lê vários números inteiros e depois mostra a média, qual foi o menor e o maior número.
continuar = "S"
soma = 0
quantidade = 0
maior = None
menor = None

while continuar == "S":
    num = int(input("Digite um número inteiro: "))
    soma += num
    quantidade += 1

    if quantidade == 1:
        maior = menor = num
    if num > maior:
        maior = num
    if num < menor:
        menor = num
    continuar = str(input("Deseja continuar? [S/N]: ")).upper()

print("O maior número foi {}, o menor número foi {} e a média entre eles é {:.2f}.".format(maior, menor, soma/quantidade))