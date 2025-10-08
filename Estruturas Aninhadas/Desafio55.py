# Desafio 055 - Verificar entre 5 pessoas, quem tem o maior e o menor peso.
pesado = 0
leve = 0
for c in range (1,6):
    peso = float(input("Digite o peso em kg da {}ª pessoa: ".format(c)))
    if c == 1:
        pesado = peso
        leve = peso
    else:
        if peso > pesado:
            pesado = peso
        if peso < leve:
            leve = peso

print("A pessoa mais leve pesa {:.2f}kg e a mais pesada pesa {:.2f}kg".format(leve, pesado))