# Desafio 036 - Programa para verificar se a parcela do financiamento ultrapassa 30% da renda.
valor = int(input("Digite o valor da casa: "))
salario = int(input("Digite o valor do seu salário: "))
prazo = int(input("Digite em quantos anos você quer pagar o financiamento: "))
condicao = salario * 0.3
prestacao = valor / (prazo * 12)

if prestacao > condicao:
    print("Seu empréstimo foi negado porque a parcela de {:.2f} reais ultrapassa 30% da sua renda.".format(prestacao))
else:
    print("Seu empréstimo foi aprovado! Você pagará {:.2f} reais em {} parcelas.".format(prestacao, prazo * 12))