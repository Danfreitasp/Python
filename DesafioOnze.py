#Programa que lê o salário e dá um aumento de 15%
salario = float(input("Digite o valor do salario: "))
aumento = float(salario * 0.15)
print("Seu novo salário com 15% de aumento é {:.2f}".format(salario + aumento))