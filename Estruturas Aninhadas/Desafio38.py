# Desafio 038 - Comparador de números
num1 = int(input("Digite o primeiro número inteiro: "))
num2 = int(input("Digite o segundo número inteiro: "))

if num1 > num2:
    print("O primeiro número \033[35m{}\033[m é maior que o segundo número \033[35m{}\033[m.".format(num1, num2))
elif num2 > num1:
    print("O segundo número \033[34m{}\033[m é maior que o primeiro número \033[34m{}\033[m.".format(num2, num1))
else:
    print("\033[31mOs números são iguais.")