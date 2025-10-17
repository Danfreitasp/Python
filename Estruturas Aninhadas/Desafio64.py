# Desafio 064 - Programa que lê vários números inteiros e só para quando digitar "999".
# No final mostra a soma dos números e quantos números foram digitados, desconsiderando o 999.

num = int(input("Digite um número para somar ou 999 para sair: "))
soma = num
quantidade = 1

while num != 999:
    num = int(input("Digite um número para somar ou 999 para sair: "))
    if num != 999:
        soma += num
        quantidade += 1
print("O valor somado é {} e foram somados {} números.".format(soma, quantidade))