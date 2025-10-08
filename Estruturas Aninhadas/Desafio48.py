# Desafio 048 - Programa que calcula a soma de números ímpares multiplos de 3 de 1 até 500.
s = 0
for c in range(1, 500):
    if c % 3 == 0:
        s += c
print(s)