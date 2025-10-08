#Utilizando laços
#Contagem de 1 a 10 com "fim" no final.
for c in range(1, 11):
    print(c)
print("Fim")
#Contagem de 10 a 1 com "Início" no final.
for g in range(10,0,-1):
    print(g)
print("Início")
#Contagem com input até o número digitado.
n = int(input('Digite um número\n'))
for c in range(1,n+1):
    print(c)