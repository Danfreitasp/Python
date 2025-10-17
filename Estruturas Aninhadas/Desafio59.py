# Desafio 059 - Calculadora de 2 valores com opções.
conta = 0
while conta != "5":
    print("Olá, bem vindo a calculadora")
    valor1 = int(input("Digite o primeiro valor: "))
    valor2 = int(input("Digite o segundo valor: "))

    conta = input("Digite a operação a ser feita:"
                      "\n1 - Somar."
                      "\n2 - Multiplicar."
                      "\n3 - Qual é o maior valor."
                      "\n4 - Digitar novos números"
                      "\n5 - Sair do programa"
                      "\nSua escolha: ")
    if conta == "1":
            print("O total da soma é: {}".format(valor1 + valor2))
    elif conta == "2":
            print("A multiplicação dos dois número é: {}".format(valor1 * valor2))
    elif conta == "3":
        if valor1 > valor2:
                print("O maior valor é: {}".format(valor1))
        elif valor1 < valor2:
                print("O maior valor é: {}".format(valor2))
    elif conta == "4":
        continue
    elif conta == "5":
        print("Programa finalizado.")
    else:
        print("Escolha inválida.")