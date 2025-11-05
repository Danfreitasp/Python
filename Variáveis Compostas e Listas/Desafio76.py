# Desafio 077 - Programa que faz uma listagem itens com preços tabulados.
itens = ('Pao', 'R$ 0.50', 'Leite', 'R$ 2.50', 'Café', 'R$ 2.00', 'Água', 'R$ 3.00', 'Bolo', 'R$ 2.50')
print("-" * 40)
print('{:^40}'.format("Listagem de Preços:"))
print("-" * 40)
for pos in range(0, len(itens)):
    if pos % 2 == 0:
        print(f'{itens[pos]:.<30}', end='')
    else:
        print(f'{itens[pos]}')