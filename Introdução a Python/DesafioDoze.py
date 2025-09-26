#Programa para ler o nome completo, transformar para letra maiúsculas, minúsculas, quantidade de letras
#Quantas letras tem o primeiro nome.

nome = input("Digite seu nome: ")

print("\nNome maiúsculo:")
print(nome.upper())

print("\nNome minúsculo:")
print(nome.lower())

sem_espaco = nome.replace(' ', '')
print("\nQuantidade de letras sem contar espaços")
print(len(sem_espaco.strip()))

nome_dividido = nome.split()
print("\nQuantidade de letras no primeiro nome:")
print(len(nome_dividido[0]))