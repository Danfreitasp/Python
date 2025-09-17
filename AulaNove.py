#Texto completo pulando linha
#print("""Testando a funcionalidade de texto com três aspas,
#aprendendo Python com aulas de vídeo,
#é mais fácil do que se imagina.""")

frase = "Aula em vídeo de Python"

#Fatiando a string: início, fim e pulando letras;
print(frase[1:5:2])

#Contando a quantidade específica de um caractere;
print(frase.count('o'))

#Transformando a frase completamente em maiúscula;
print(frase.upper())

#Verificando o tamanho da frase;
print(len(frase))

#Verificando o tamanho da frase, excluindo espaços antes e depois;
print(len(frase.strip()))

#Alterando elemento da frase;
frase = frase.replace('Python', 'Android')
print(frase)

#Verifica se tem o elemento na string;
print("Aula" in frase)

#Procura o elemento na string e devolve a posição;
print(frase.find('Android'))

#Cortando a frase em pedaços (listas em colchetes);
print(frase.split())

#Exibindo apenas um elemento da string;
dividido = frase.split()
print(dividido[4])
