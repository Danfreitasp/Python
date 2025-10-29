# Desafio 069 - Programa que que lê idade e sexo de várias pessoas.
maiores = 0
homem = 0
mulher = 0
sexo = str
condicao = str
while True:
    print("-------------------")
    print("Cadastre uma pessoa")
    print("-------------------")

    idade = int(input("Digite a idade: "))
    if idade > 18:
        maiores += 1
    sexo = str(input("Digite o sexo [M/F]: ")).strip().upper()
    if sexo == "M":
         homem += 1
    if sexo == "F" and idade < 20:
        mulher += 1

    condicao = str(input("Deseja continuar? [S/N]: ")).strip().upper()
    if condicao == "N":
        break
print(f"Tem {maiores} maiores de 18 anos, {homem} homens cadasrados e {mulher} mulheres com menos de 20 anos.")