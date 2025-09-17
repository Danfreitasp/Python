#Programa que lê nome completo e depois apresenta primeiro e ultimo.
nome = input("Digite seu nome: ")

print("Seu primeiro nome é: ", nome.split()[0])
print("Seu último nome é: ", nome.split()[-1])

#lista[-1] → último elemento
#lista[-2] → penúltimo elemento

#lista[0] → primeiro elemento
#lista[1] → segundo elemento