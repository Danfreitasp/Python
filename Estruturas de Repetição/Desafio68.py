# Desafio 068 - Desafio de par ou ímpar que conta a quantidade de vitórias até perder.
import random

contador = 0

while True:
    print("Vamos jogar par ou ímpar?")
    computador = random.randint(1, 20)
    jogador = int(input("Digite um número: "))
    escolha = input("Par ou ímpar? [P/I]: ").strip().upper()

    soma = jogador + computador
    resultado = "P" if soma % 2 == 0 else "I"
    tipo = "Par" if resultado == "P" else "Ímpar"

    print(f"Você jogou {jogador} e o computador {computador}. Total = {soma} → {tipo}")

    if escolha == resultado:
        print("Você venceu!\n")
        contador += 1
    else:
        print(f"Você perdeu! Vitórias consecutivas: {contador}")
        break
