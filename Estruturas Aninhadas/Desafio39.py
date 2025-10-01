# Desafio 039 - Comparador de idade.

from datetime import datetime

nascimento = int(input("Digite o ano de seu nascimento: "))
agora = datetime.today()
ano = agora.year
idade = ano - nascimento

if idade > 18:
    prazo = idade - 18
    print("Você já passou da idade para alistamento militar em {} anos.".format(prazo))
elif idade < 18:
    prazo = 18 - idade
    print("Você ainda vai se alistar daqui à {} anos.".format(prazo))
else:
    print("Você deve se alistar imediatamente.")