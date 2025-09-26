#Programa que verifica a velocidade e gera multa
velocidade = int(input("Digite a velocidade em Km/h: "))
#Para cada km/h acima do limite, é adicionado 7 reais na multa
multa = (velocidade - 80) * 7

if velocidade > 80:
    print("Você está acima do limite de velocidade, sua multa é de {} reais.".format(multa))
else:
    print("Você está dentro do limite de velocidade.")