galera = [['Joao', 19], ['Ana', 33], ['Marcos', 90], ['Maria', 40]]
print(galera[2][1])
print(galera[3])
print(galera)

for p in galera:
    print(p)

#Printar somente nomes:
for p in galera:
    print(f'Nome: {p[0]}')

#Printar somente idades:
for p in galera:
    print(f'Idade: {p[1]}')

#Printar nomes e idades:
for p in galera:
    print(f'O(A) {p[0]} tem {p[1]} anos.')