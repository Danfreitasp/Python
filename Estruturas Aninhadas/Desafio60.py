# Desafio 060 - Programa que lê o número e mostra o seu fatorial.
num1 = int(input("Digite o número a ser fatorado: "))
fatorial = 1
contador = num1

while contador > 0:
    fatorial *= contador
    contador -= 1

print(f"O fatorial de {num1} é {fatorial}")