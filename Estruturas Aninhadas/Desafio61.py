# Desafio 061 - Programa que lê uma o primeiro termo e a razão de uma PA e no final mostra os 10 primeiros termos, usando while.
i = int(input("Termo: "))
p = int(input("Razão: "))
cont = 0
while cont < 10:
    print(i, end="->")
    i += p
    cont += 1
print("Fim")