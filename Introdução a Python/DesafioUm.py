# Desafio 1 - Interação com o usuário
# Escreva um programa que solicite ao usuário seu nome, dia, mês e ano de nascimento.
# Em seguida, exiba uma mensagem personalizada confirmando as informações fornecidas.

nome = input("Digite seu nome: ")
dia = input("Digite o dia do seu nascimento: ")
mes = input("Digite o mês do seu nascimento: ")
ano = input("Digite o ano do seu nascimento: ")


print('Olá, ' + nome + '! Prazer em conhecê-lo. Você nasceu no dia ' + dia + ' do mês ' + mes + ' do ano de ' + ano + '. Correto?')

# Confirmação de dados
resposta = input("Digite s para sim e n para não.\n")

if resposta.lower() == 's':
    print('Obrigado por confirmar suas informações!\n')
else:
    print('Por favor, reinicie o programa para corrigir suas informações.')
