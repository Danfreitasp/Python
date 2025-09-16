#Programa que lê um número e mostra antecessor e sucessor.
#Mostra o dobro, triplo e raiz quadrada
num1 = int(input('Digite um número:'))
print("O número é {}, seu antecessor é {} e seu sucessor é {}." .format(num1, num1 - 1, num1 + 1))
print("Seu dobro é {}, o triplo é {} e a raíz quadrada é {:.2f}.".format(num1 * 2, num1 * 3, num1 ** (1/2) ))