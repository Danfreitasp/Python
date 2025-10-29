# Programa que simula um caixa eletrônico.
print("-" * 30)
print('{:^30}'.format("Banco Python"))
print("-" * 30)
saque = int(input("Digite o valor que deseja sacar: "))
total = saque
cedula = 100
total_cedula = 0
while True:
    if total >= cedula:
        total -= cedula
        total_cedula += 1
    else:
        if total_cedula > 0:
            print(f"Foram sacadas {total_cedula} notas de {cedula} reais.")
        if cedula == 100:
            cedula = 50
        elif cedula == 50:
            cedula = 20
        elif cedula == 20:
            cedula = 10
        elif cedula == 10:
            cedula = 5
        elif cedula == 5:
            cedula = 1
        total_cedula = 0
        if total == 0:
            break
print("-" * 30)
print('{:^30}'.format("Obrigado e volte sempre."))
print("-" * 30)