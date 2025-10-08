# Desafio 052 - Programa que informa se o número é primo ou não.
num1 = int(input("Digite um número inteiro: "))
div = 0
for c in range(1, num1 + 1):
    if num1 % c == 0:
        div += 1

if div == 2:
    print("O número {} é primo".format(num1))
else:
    print("O número {} não é primo".format(num1))