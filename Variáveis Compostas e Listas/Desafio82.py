# Desafio 082 - Programa que lê vários números e coloca em lista, cria duas listas extras com os números pares e outra com os ímpares.
lista = []
par=[]
impar=[]
while True:
    num = int(input('Digite um número: '))
    lista.append(num)
    if num %2 == 0:
        par.append(num)
    else:
        impar.append(num)
    print("Número adicionado.")
    parar = input('Deseja parar? [S/N]: ').strip().upper()
    if parar == 'S':
        break


print(f'A lista completa é {lista}')
print(f'A lista ímpar é {impar}')
print(f'A lista par é {par}')