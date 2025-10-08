# Desafio 049 - Tabuada de acordo com imputs em laço.
num1 = int(input("Digite o número a ser multiplicado: "))

for c in range(0, 11):
    print("{} x {} = {}".format(num1, c, num1 * c))