# Desafio 078 - Programa que cria lista com 5 valores, depois mostra qual foi o maior valor digitado, o menor e as posições na lista.
lista = []
maior = 0
menor = 0
for c in range(0, 5):
    lista.append(int(input(f"Digite um número para a posição {c}: ")))
    if c == 0:
        maior = menor = lista[c]
    else:
        if lista[c] > maior:
            maior = lista[c]
        if lista[c] < menor:
            menor = lista[c]

print(f'Voce digitou os valores {lista}')
print(f'O maior valor digitado foi {maior} nas posições ', end='')
for i, v in enumerate(lista):
    if v == maior:
        print(f'{i}...')
print(f'O menor valor digitado foi {menor} nas posições ', end='')
for i, v in enumerate(lista):
    if v == menor:
        print(f'{i}...', end='')
print()
