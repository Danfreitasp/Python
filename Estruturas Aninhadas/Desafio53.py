# Desafio 053 - Programa que lê uma frase e informa se é um palíndromo.
frase = str(input("Digite uma frase: "))
fraseSem = frase.replace(' ','').lower()
fraseInv = fraseSem[::-1]

print(fraseSem)
print(fraseInv)

if fraseSem == fraseInv:
    print("A frase é um palíndromo.")
else:
    print("A frase não é um palíndromo.")