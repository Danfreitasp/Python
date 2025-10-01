# Desafio 044 - Calcular o valor a ser pago pelo produto.

valor = float(input("Digite o valor do produto: "))
pagamento = input("* Digite \33[36m1\33[m para pagamento à vista (dinheiro/cheque).\n"
                  "* Digite \33[36m2\33[m para pagamento à vista no cartão.\n"
                  "* Digite \33[36m3\33[m para pagamento à prazo até 2 parcelas.\n"
                  "* Digite \33[36m4\33[m para pagamento à prazo com 3 parcelas ou mais.\n"
                  )
if pagamento == "1":
    valor = valor - (valor * 0.1)
    print("Valor final do produto: R${:.2f}".format(valor))
elif pagamento == "2":
    valor = valor - (valor * 0.05)
    print("Valor final do produto: R${:.2f}".format(valor))
elif pagamento == "3":
    print("Valor final do produto: R${:.2f}".format(valor))
elif pagamento == "4":
    valor = valor + (valor * 0.2)
    print("Valor final do produto: R${:.2f}".format(valor))