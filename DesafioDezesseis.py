#Lê a frase do teclado, verifica quantas vezes aparece a letra "a", qual a sua primeira posição.
#E qual a sua ultima posição

frase = input('Digite uma frase: ')

frase1 = frase.lower()
print("Quantas letras A na frase")
print(frase1.count('a'))

print("Primera posição da letra A na frase")
print(frase1.find('a'))

print("Ultima posição da letra A na frase")
print(frase1.rfind('a'))