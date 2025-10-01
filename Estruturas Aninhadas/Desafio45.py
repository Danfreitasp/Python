# Desafio 045 - Jogo de Jokenpo
import random

print("=== JOKENPÔ ===")
print("Escolha uma opção:\n"
      "1 - Para Pedra\n" "2 - Para Papel\n" "3 - Para Tesoura")
humano = int(input("Sua escolha: "))
computador = random.randint(1, 3)

if computador == 1:
    print("Computador selecionou Pedra.")
elif computador == 2:
    print("Computador selecionou Papel.")
elif computador == 3:
    print("Computador selecionou Tesoura.")

if humano == computador:
    print("Empate.")

elif (humano == 1 and computador == 3) or \
     (humano == 2 and computador == 1) or \
     (humano == 3 and computador == 2):
    print("Você venceu!")
else:
    print("Computador venceu!")