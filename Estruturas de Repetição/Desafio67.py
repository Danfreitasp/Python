# Desafio 067 - Tabuada até o número digitado ser negativo.
while True:
    tabuada = int(input("\nQuer ver a tabuada de qual número? "))
    if tabuada < 0:
        print("Programa de tabuada encerrado")
        break
    for c in range(1, 11):
        print(f"{tabuada} x {c} = {tabuada * c}", end="||")
