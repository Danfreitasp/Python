#Programa para conversão de câmbio com cotação de 3,27
saldo = float(input("Digite o saldo: "))
print("Seu saldo é de R${:.2f}, você pode comprar {:.2f} dólares".format(saldo, saldo / 3.27))