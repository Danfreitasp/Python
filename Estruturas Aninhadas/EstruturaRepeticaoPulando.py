i = int(input("Início: "))
f = int(input("Fim: "))
p = int(input("Pulo: "))
for c in range(i, f+1, p):
    print(c)
print("Fim")

s = 0
for c in range(0, 3):
    n = int(input("Digite um número: "))
    s += n
print("A somatória dos números é: {}".format(s))