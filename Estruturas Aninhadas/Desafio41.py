#Desafio 041 - Categoria de Natação de acordo com a idade
from datetime import datetime
nascimento = int(input("Digite o ano de seu nascimento: "))
agora = datetime.today()
ano = agora.year
idade = int(ano - nascimento)

if idade <= 9:
    print("A categoria deste atleta é Mirim.")

elif idade <= 14 and idade > 9:
    print("A categoria deste atleta é Infantil.")

elif idade <= 19 and idade > 14:
    print("A categoria deste atleta é Junior.")

elif idade == 20:
    print("A categoria deste atleta é Sênior.")

elif idade > 20:
    print("A categoria deste atleta é Master.")