teste = []
teste.append('Daniel')
teste.append(40)
galera = []
# [:] Clona o conteúdo, caso não adicione, uma lista gera um vinculo com a outra.
galera.append(teste[:])
teste[0] = 'Maria'
teste[1] = 30
galera.append(teste[:])
print(galera)