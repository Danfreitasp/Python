#Calculo de quantidade de tinta de acordo com a área, cada litro de tinta pinta 2m².
alt = float(input("Digite a altura da parede: "))
larg = float(input("Digite a largura da parede: "))
area = alt * larg
tinta = area / 2

print("A área da parede é {:.2f} m², ". format(area), end='')
print("você vai precisar de {:.2f} litros de tinta para pintar tudo.".format(tinta))