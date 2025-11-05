# Desafio 083 - Programa que verifica se a expressão numérica com parenteses, está correta.
exp = str(input("Digite uma expressão: "))
pilha = []
for simb in exp:
    if simb == '(':
        pilha.append('(')
    elif simb ==  ')':
        if len(pilha) > 0:
            pilha.pop()
        else:
            pilha.append(')')
            break
if len(pilha) == 0:
    print('Sua expressão está correta.')
else:
    print('Sua expressão estão incorreta.')
