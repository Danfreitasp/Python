# Desafio 086 - Programa que cria uma Matriz 3x3 e imprime em tela, usando uma única lista:
matriz = []

for i in range(9):
    matriz.append(int(input(f'Digite um valor para [{i // 3}, {i % 3}]: ')))

print('-=' * 20)

for i in range(9):
    print(f'[{matriz[i]:^5}]', end='')
    if (i + 1) % 3 == 0:  # quebra a linha a cada 3 números
        print()
