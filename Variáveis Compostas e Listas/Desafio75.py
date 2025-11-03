# Desafio 075 - Programa que lê 4 valores e mostra quantas vezes apareceu o número 9, em que posição foi digitado o primeiro valor 3 e quais foram os números pares.
num1 = int(input("Digite um número: "))
num2 = int(input("Digite outro número: "))
num3 = int(input("Digite outro número: "))
num4 = int(input("Digite outro número: "))
conjunto = (num1, num2, num3, num4)

print(f"Você digitou os números {conjunto}.")
print(conjunto.count(9))
print(conjunto.index(3))