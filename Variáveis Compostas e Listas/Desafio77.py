# Desafio 077 - Programa que lê uma tupla e mostra as vogais.
palavras = ('cachorro', 'camisa', 'caixa', 'mochila', 'caneta', 'sapato', 'celular')
for p in palavras:
    print(f'\nNa palavra {p} temos as vogais: ', end='')
    for letra in p:
        if letra.lower() in 'aeiou':
            print(letra, end=' ')