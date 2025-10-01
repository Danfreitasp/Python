# Desafio 037 - Conversão de Bases
num = int(input("Digite um número inteiro: "))

print("\nEscolha a base de conversão:")
print("[1] Binário")
print("[2] Octal")
print("[3] Hexadecimal")

opcao = int(input("Sua opção: "))

if opcao == 1:
    print(f"O número {num} convertido para BINÁRIO é {bin(num)[2:]}")
elif opcao == 2:
    print(f"O número {num} convertido para OCTAL é {oct(num)[2:]}")
elif opcao == 3:
    print(f"O número {num} convertido para HEXADECIMAL é {hex(num)[2:]}")
else:
    print("Opção inválida!")
