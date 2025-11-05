valores = []
valores.append(5)
valores.append(3)
valores.append(2)

#Imprime em tela os valores usando for.
for v in valores:
    print(f'{v}...', end='')
print('\n')

for c, v in enumerate(valores):
    print(f'Na posição {c} encontrei  valor {v}!')
print('Cheguei ao final da lista.')
print('\n')

#Lista de 5 itens utilizando input.
lista2 = list()
for cont in range(0, 5):
    lista2.append(int(input('Digite um valor: ')))

for c, v in enumerate(lista2):
    print(f'Na posição {c} encontrei  valor {v}!')
print('Cheguei ao final da lista.')