#Programa para verificar se foi aprovado usando if e else.
n1 = float(input('Digite sua primeira nota: '))
n2 = float(input('Digite sua segunda nota: '))
m = (n1 + n2) / 2
print('Sua nota média foi {:.1f}'.format(m))

#Forma simplificada
print('Você foi aprovado!' if m >=6 else 'Você foi reprovado!')

#Forma composta
if m >= 6.0:
    print("Você está aprovado!")
else:
    print("Você foi reprovado!")