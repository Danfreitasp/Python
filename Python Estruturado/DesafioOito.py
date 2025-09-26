#Calculando se três retas podem formar um triângulo.
r1 = float(input("\33[36mDigite o comprimento da primeira reta: "))
r2 = float(input("\33[35mDigite o comprimento da segunda reta: "))
r3 = float(input("\33[34mDigite o comprimento da terceira reta: "))

if r1 + r2 > r3 and r1 + r3 > r2 and r2 + r3 > r1:
    print("\33[32;40mUm triângulo pode ser formado com essas medidas.\033[m")
else:
    print("\33[31;40mUm triângulo não pode ser formado com essas medidas.\033[m")