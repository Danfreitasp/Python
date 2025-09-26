#Programa para gerar valor de viagem, até 200km 0,50, acima disso, 0,45.
distancia = int(input("Digite a distancia da sua viagem em km: "))

if distancia <= 200:
    print("O valor da sua viagem é: ", distancia * 0.50, "reais.")
else:
    print("O valor da sua viagem é: ", distancia * 0.45, "reais.")