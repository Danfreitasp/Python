# Desafio 075 - Programa que lê 4 valores e mostra quantas vezes apareceu o número 9, em que posição foi digitado o primeiro valor 3 e quais foram os números pares.
num1 = int(input("Digite um número: "))
num2 = int(input("Digite outro número: "))
num3 = int(input("Digite outro número: "))
num4 = int(input("Digite outro número: "))

conjunto = (num1, num2, num3, num4)

print(f"Você digitou os números {conjunto}.")
print(f'O número 9 apareceu {conjunto.count(9)} vezes.')

if 3 in conjunto:
    print(f'O número 3 apareceu na {conjunto.index(3)+1}ª posição.')
else:
    print('O 3 não foi digitado.')
    
print('O números pares são: ', end='')
for c in conjunto:
    if c % 2 == 0:
        print(c, end=' ')