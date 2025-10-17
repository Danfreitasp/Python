num1 = int(input("Digite o primeiro número da sequência de fibonacci: "))
num2 = int(input("Digite o segundo número da sequência de fibonacci: "))
quantidade = int(input("Digite a quantidade de elementos que deseja mostrar: "))
contador = 0

while contador < quantidade:
    print(num1, end="->")
    soma = num1 + num2
    num1 = num2
    num2 = soma
    contador += 1
print("Fim.")