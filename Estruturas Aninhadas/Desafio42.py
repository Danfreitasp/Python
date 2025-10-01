# Desafio 042 - Verificador de triângulo
r1 = float(input("\33[36mDigite o comprimento da primeira reta: "))
r2 = float(input("\33[35mDigite o comprimento da segunda reta: "))
r3 = float(input("\33[34mDigite o comprimento da terceira reta: "))

if r1 + r2 > r3 and r1 + r3 > r2 and r2 + r3 > r1:
    print("\33[32;40mUm triângulo pode ser formado com essas medidas.\033[m")
    if r1 == r2 and r1 == r3 and r3 == r2:
        print("Triângulo equilátero.")
    elif r1 == r2 or r1 == r3 or r3 == r2:
        print("Triângulo isoceles.")
    elif r1 != r2 and r1 != r3 and r1 != r2:
        print("Triangulo escaleno.")
else:
    print("\33[31;40mUm triângulo não pode ser formado com essas medidas.\033[m")