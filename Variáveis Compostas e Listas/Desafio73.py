# Desafio 074 - Tupla de times do Brasileirão 2013.
brasileirao = (
    "Cruzeiro",
    "Grêmio",
    "Atlético Paranaense",
    "Botafogo",
    "Goiás",
    "Vitória",
    "Santos",
    "São Paulo",
    "Atlético Mineiro",
    "Corinthians",
    "Internacional",
    "Fluminense",
    "Flamengo",
    "Coritiba",
    "Bahia",
    "Portuguesa",
    "Vasco da Gama",
    "Ponte Preta",
    "Náutico",
    "Criciúma"
)
print("Os 5 primeiros colocados foram:", brasileirao[:5])
print("Os 4 ultimos colocados foram:", brasileirao[16:])
print("Brasileirão 2013 em ordem alfabética:",sorted(brasileirao))
print("E o Bahia ficou na posição",brasileirao.index("Bahia"))