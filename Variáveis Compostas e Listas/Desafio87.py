# Desafio 087 - Programa que cria uma matriz 3x3 e mostra:
# A) A soma de todos os valores pares digitados.
# B) A soma dos valores da terceira coluna.
# C) O maior valor da segunda linha.

matriz = [[], [], []]
soma_pares = soma_coluna3 = maior_linha2 = 0

for l in range(3):
    for c in range(3):
        valor = int(input(f'Digite um valor para [{l}, {c}]: '))
        matriz[l].append(valor)

print('-=' * 20)
for l in range(3):
    for c in range(3):
        print(f'[{matriz[l][c]:^5}]', end='')
        if matriz[l][c] % 2 == 0:
            soma_pares += matriz[l][c]
    print()

soma_coluna3 = matriz[0][2] + matriz[1][2] + matriz[2][2]
maior_linha2 = max(matriz[1])

print('-=' * 20)
print(f'A soma dos valores pares é {soma_pares}')
print(f'A soma dos valores da terceira coluna é {soma_coluna3}')
print(f'O maior valor da segunda linha é {maior_linha2}')