#Listas são mutáveis, diferentemente das tuplas.
num = [3, 4, 5, 1, 9]
num[1] = 3
print(num)

#Insere um elemento na ultima posição.
num.append(8)
print(num)

#Ordena em ordem crescente.
num.sort()
print(num)

#Ordena em ordem decrescente.
num.sort(reverse=True)
print(num)

#Insere um número na posição selecionada, no exemplo, foi adicionado 0 na posição 2.
num.insert(2, 0)
print(num)

#Remove o ultimo valor caso não seja indicado nada entre parenteses.
num.pop()
print(num)

#Remove o primeiro item indicado entre parenteses da lista.
num.remove(3)
print(num)