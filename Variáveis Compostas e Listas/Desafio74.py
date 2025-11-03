# Desafio 074 - Programa que gera 5 números aleatórios e coloca em tupla, mostra o menor e o maior.
import random
from random import randint
numeros = [randint(1, 10), randint(1, 10), randint(1, 10), randint(1, 10), randint(1, 10)]
print(numeros)
print("O menor número é:",sorted(numeros)[0])
print("O maior número é:",sorted(numeros)[4])