# Desafio 056 - Dasenvolva um programa qua leia o noma, idada a saxo da 4 passoas.
# No final do programa. mostra:  A média da idada do grupo.
# Qual e o noma do homem mais velho. Quantas mulheres têm manos da 20 anos.

id = 0
mulher = 0
homem = str()
idhomem = 0

for c in range(1,5):
    nome = str(input("Informe seu nome: "))
    idade = int(input("Informe sua idade: "))
    sexo = str(input("Informe seu sexo (M/F): "))

    id += idade

    if sexo == "F" or sexo == "f":
        if idade < 20:
            mulher += 1
    if c == 1:
        if sexo == "M" or sexo == "m":
            homem = nome
            idhomem = idade
    else:
        if sexo == "M" or sexo == "m":
            if idade > idhomem:
                homem = nome
                idhomem = idade

print("A média de idade é {} anos.".format(int(id/4)))
print("A quantiade de mulheres com menos de 20 anos é {}.".format(mulher))
print("O homem mais velho é {} e ele tem {} anos.".format(homem, idhomem))