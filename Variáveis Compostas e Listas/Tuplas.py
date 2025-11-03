lanche = ('Sanduiche', 'Suco', 'Pudim', 'Cafe')
#Tuplas são imutáveis.

for comida in lanche:
    print("Hoje eu comi", comida)
print("Enchi a pança.")
print("Comi", len(comida), "lanches:")

for pos, comida in enumerate(lanche):
    print(f"Comi {comida} na posição {pos}")

print(sorted(lanche))

for cont in range(0, len(lanche)):
    print(lanche[cont])