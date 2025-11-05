# Desafio 081 - Programa que lê vários números e coloca em lista, mostra quantos numeros foram digitados, 
# ordena de forma decrescente e informa se o 5 foi digitado ou não.
lista = []
while True:
    num = int(input('Digite um número: '))
    lista.append(num)
    print("Número adicionado.")
    parar = input('Deseja parar? [S/N]: ').strip().upper()
    if parar == 'S':
        break
    
if 5 in lista:
    print('O número cinco foi digitado.')
else:
    print('O número cinco não foi digitado.')

print(f'Foram digitados {len(lista)} números.')

lista.sort(reverse=True)
print(f'Os números em ordem decrescente: {lista}')