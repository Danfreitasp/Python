#Jogo de adivinhação de número
import random
n1 = random.randint(0, 5)
n2 = int(input("Digite um número de 0 a 5: "))

if 0 <= n2 <= 5:
    if n1 == n2:
        print("Voce acertou! O número era {}".format(n1))
    else:
        print("Voce errou! O número era {}".format(n1))
else:
    print("O número deve ser entre 0 e 5")
    print("Fim")