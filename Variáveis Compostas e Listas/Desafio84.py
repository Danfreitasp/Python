# Desafio 084 - Progrma que lê o nome e peso de pessoas, mostra quantas fora cadastradas, pessoas mais pesadas e pessoas mais leves.
pessoas = []
total = []
leves = []
pesados = []
quantidade = primeira = 0

while True:
    pessoas.append(str(input('Nome: ')))
    pessoas.append(float(input('Peso: ')))
    total.append(pessoas[:])  # copia os dados pra lista total
    quantidade += 1

    if primeira == 0:
        # primeira pessoa define o peso base
        leves.append(pessoas[:])
        pesados.append(pessoas[:])
        maior = menor = pessoas[1]
    else:
        if pessoas[1] > maior:
            maior = pessoas[1]
            pesados.clear()
            pesados.append(pessoas[:])
        elif pessoas[1] == maior:
            pesados.append(pessoas[:])
        elif pessoas[1] < menor:
            menor = pessoas[1]
            leves.clear()
            leves.append(pessoas[:])
        elif pessoas[1] == menor:
            leves.append(pessoas[:])
    primeira += 1
    pessoas.clear()  # limpa pra próxima entrada

    continuar = input('Deseja continuar? [S/N] ').strip().upper()
    if continuar == 'N':
        break

print(f'\nForam cadastradas {quantidade} pessoas.')
print(f'O maior peso foi {maior}kg. Peso de ', end='')
for p in pesados:
    print(f'[{p[0]}]', end=' ')
print(f'\nO menor peso foi {menor}kg. Peso de ', end='')
for p in leves:
    print(f'[{p[0]}]', end=' ')
print()
