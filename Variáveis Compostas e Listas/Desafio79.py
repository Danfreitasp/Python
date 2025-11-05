# Desafio 079 - Programa que cria lista e não aceita números duplicados.
lista = []

while True:
    num = int(input('Digite um número: '))
    if num in lista:
        print("Número repetido, não foi adicionado.")
    else:
        lista.append(num)
        print("Número adicionado.")
    parar = input('Deseja parar? [S/N]: ').strip().upper()
    if parar == 'S':
        break
print(f'Os números digitados foram: {sorted(lista)}')