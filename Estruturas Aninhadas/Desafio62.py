# Desafio 062 - Programa que lê o primeiro termo e a razão de uma PA
# Mostra os 10 primeiros termos e depois permite continuar.
i = int(input("Primeiro termo: "))
p = int(input("Razão: "))
termos = 10
cont = 0

while termos != 0:
    total = cont + termos
    while cont < total:
        print(i, end="->")
        i += p
        cont += 1
    print("Pausa")
    termos = int(input("Quantos termos você quer mostrar a mais? (0 para parar): "))

print("Fim da progressão.")