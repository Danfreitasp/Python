# Desafio 051 - Programa que lê uma o primeiro termo e a razão de uma PA e no final mostra os 10 primeiros termos.
primeiro = int(input("Digite o início da progressão: "))
razao = int(input("Digite a razão da progressão: "))

for c in range(1, 11):
    termo = primeiro + (c - 1) * razao
    print(termo, end="->")
print("Fim.")