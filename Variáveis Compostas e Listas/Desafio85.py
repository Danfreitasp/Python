# Desafio 085 - Programa que pede 7 valores, cadastra em uma lista única separando números pares de ímpares; No final mostra os valores pares e ímpares em ordem crescente.
numeros = [[], []]
for n in range(0, 7):
    num = int(input('Digite um número: '))
    if num %2 == 0:
        numeros[0].append(num)
    else:
        numeros[1].append(num)

print(f'Os números ímpares são {sorted(numeros[1])}')
print(f'Os números pares são {sorted(numeros[0])}')