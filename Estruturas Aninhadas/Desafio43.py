# Desafio 043 - Cálculadora de IMC

peso = float(input('Digite o peso em Kg: '))
altura = float(input('Digite sua altura: '))

imc = float(peso / (altura * altura))

if imc < 18.5:
    print("Você está abaixo do peso.")
elif imc >= 18.5 and imc < 25:
    print("Você está com o peso ideal.")
elif imc >= 25 and imc < 30:
    print("Você está com sobrepeso.")
elif imc >= 30 and imc < 40:
    print("Você está obeso")
elif imc >= 40:
    print("Você está com obesidade mórbida.")