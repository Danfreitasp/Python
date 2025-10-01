# Desafio 040 - Programa para ler notas e mostrar aprovação ou reprovação
nota1 = float(input("Digite a primeira nota: "))
nota2 = float(input("Digite a segunda nota: "))
media = (nota1 + nota2) / 2

if media < 5:
    print("Você foi reprovado, sua média foi {}.".format(media))
elif media >= 7:
    print("Você foi aprovado, sua média foi {}.".format(media))
elif media >= 5 and media < 7:
    print("Você está de recuperação, sua média foi {}.".format(media))