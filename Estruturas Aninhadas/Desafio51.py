# Desafio 051 - Programa que lê uma o primeiro termo e a razão de uma PA e no final mostra os 10 primeiros termos.
i = int(input("Termo: "))
p = int(input("Razão: "))
for c in range(i, 10, p):
    print(c)
print("Fim")