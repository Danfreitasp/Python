# Desafio 058 - Jogo de adivinhação 0 a 10.

import random
n1 = random.randint(0, 10)
n2 = int(input("Digite um número de 0 a 10: "))
tentativas = 0

while n1 != n2:
    n2 = int(input("Você errou, tente novamente: "))
    tentativas += 1
print("Você acertou depois de {} tentativas, o número era {}.".format(tentativas, n1))