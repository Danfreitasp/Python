# Desafio 066 - Crie um programa que leia vários números inteiros pelo teclado. 0 programa s6 vai parar quando o
# usuário digitar o valor 999, qua é a condição de parada. No final, mostre quantos números foram
# digitados a qual foi a soma entre elas (desconsiderando o flag).
contador = 0
while True:
    num = int(input("Digite um numero (999 para parar): "))
    if num == 999:
        break
    contador += num
print(f"A soma dos número digitados foi {contador}")