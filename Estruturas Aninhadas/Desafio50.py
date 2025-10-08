# Desafio 050 - Programa para ler seis números inteiros, mostra a soma apenas dos números pares.
s = 0
for c in range(0, 6):
    n = int(input("Digite um número: "))
    if n % 2 == 0:
        s += n
print("A somatória dos números pares é: {}".format(s))