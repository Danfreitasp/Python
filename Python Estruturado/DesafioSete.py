#Calculadora de aumento de acordo com salário, se >= a 1250 é 10%, se <= 1250 é 15%
salario = float(input("\033[31mDigite o valor do seu salario: "))

if salario >= 1250:
    print("\033[32mO seu aumento será de\033[m","\033[4;33m", salario * 0.1, "\033[0;32mreais.")
else:
    print("\033[34mO seu aumento será de","\033[35m",salario * 0.15, "\033[34mreais.")