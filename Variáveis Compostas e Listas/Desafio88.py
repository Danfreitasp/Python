# Desafio 088 - Programa que gera palpites para a Mega Sena.
# O programa pergunta quantos jogos serão gerados e sorteia 6 números por jogo, sem repetição.

from random import sample
from time import sleep

print('-' * 30)
print('      JOGA NA MEGA SENA')
print('-' * 30)

quant = int(input('Quantos jogos você quer que eu sorteie? '))
print(f'-=-=-= SORTEANDO {quant} JOGOS -=-=-=')

for i in range(quant):
    jogo = sorted(sample(range(1, 61), 6))
    print(f'Jogo {i+1}: {jogo}')
    sleep(1)

print('-=-=-= < BOA SORTE! > -=-=-=')
