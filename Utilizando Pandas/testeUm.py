import pandas as pd

# Criando um DataFrame
df = pd.DataFrame({
    "nome": ["Ana", "Bruno", "Carla"],
    "idade": [28, 35, 22],
    "salario": [4500, 7200, 3800]
})

# Filtrar quem ganha mais de 4000
df[df["salario"] > 4000]

# Média de idade
df["idade"].mean()  # → 28.33

print(df)