# Desafio 054 - Programa que lê o ano de nascimento de sete pessoas em mostra quantas já atingiram a maioridade.
from datetime import datetime
agora = datetime.today()
nascimento = agora.year
maior = 0
menor = 0

for c in range(0, 7):
    ano = int(input("Digite o ano: "))
    if nascimento - ano >= 21:
        maior += 1
    else:
        menor += 1
print("{} pessoas são maiores de idade e {} pessoas são menores de idade.".format(maior, menor))