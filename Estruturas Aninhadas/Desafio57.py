# Desafio 057 - Programa que lê o sexo de uma pessoa mas só aceita M ou F.

sexo = str(input("Digite o seu sexo (M/F): "))
sexo = sexo.upper()

while sexo != "F" and sexo != "M":
    print('Só é aceito M ou F, por favor, tente novamente.')
    sexo = str(input("Digite o seu sexo (M/F): "))
    sexo = sexo.upper()
if sexo == "M":
    print("Você selecionou o sexo Masculino")
else:
    print("Você selecionou o sexo Feminino")