#Programa para ler 3 números e indicar qual é o maior e menor.
num1 = input("\033[36mDigite o primeiro número: ")
num2 = input("\033[32mDigite o segundo número: ")
num3 = input("\033[35mDigite o terceiro número: ")

if num1 > num2 and num1 > num3:
    print("O primeiro número é o maior.")
elif num2 > num1 and num2 > num3:
    print("O segundo número é o maior.")
else:
    print("O terceiro número é o maior.")

if num1 < num2 and num1 < num3:
    print("O primeiro número é o menor.")
elif num2 < num1 and num2 < num3:
    print("O segundo número é o menor.")
else:
    print("O terceiro número é o menor.")