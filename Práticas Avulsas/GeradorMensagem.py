import tkinter as tk
from tkinter import messagebox


def formatar_moeda(valor):
    try:
        valor = float(valor.replace(".", "").replace(",", "."))
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except ValueError:
        return None


def gerar_mensagem():
    nome = entrada_nome.get().strip()
    banco = entrada_banco.get().strip()
    parcela_antiga = formatar_moeda(entrada_parcela_antiga.get().strip())
    parcela_nova = formatar_moeda(entrada_parcela_nova.get().strip())
    troco = formatar_moeda(entrada_troco.get().strip())
    atendente = entrada_atendente.get().strip()

    if not nome or not banco or not parcela_antiga or not parcela_nova or not troco or not atendente:
        messagebox.showerror("Erro", "Preencha todos os campos corretamente.")
        return

    mensagem = f"""Olá, {nome},

Meu nome é {atendente} e entrei em contato para falar sobre a portabilidade do seu contrato, com redução da taxa de juros e liberação de troco.

Além disso, atualmente o INSS está permitindo uma carência de até 90 dias para o início do desconto da parcela após a realização da portabilidade.

Tenho uma proposta para o seu contrato do Banco {banco}:

✅ Parcela reduzida de {parcela_antiga} para {parcela_nova}
✅ Liberação de troco no valor de {troco}
✅ Carência de 90 dias, ficando até 3 meses sem o desconto dessa parcela
✅ Sua conta de recebimento permanece a mesma, pois somos conveniados ao INSS

Podemos dar prosseguimento e garantir essa redução na sua parcela?"""

    caixa_mensagem.delete("1.0", tk.END)
    caixa_mensagem.insert(tk.END, mensagem)


def copiar_mensagem():
    mensagem = caixa_mensagem.get("1.0", tk.END).strip()

    if not mensagem:
        messagebox.showwarning("Aviso", "Gere uma mensagem antes de copiar.")
        return

    janela.clipboard_clear()
    janela.clipboard_append(mensagem)

    messagebox.showinfo(
        "Copiado",
        "Mensagem copiada para a área de transferência."
    )


def limpar_campos():
    entrada_nome.delete(0, tk.END)
    entrada_banco.delete(0, tk.END)
    entrada_parcela_antiga.delete(0, tk.END)
    entrada_parcela_nova.delete(0, tk.END)
    entrada_troco.delete(0, tk.END)

    entrada_atendente.delete(0, tk.END)
    entrada_atendente.insert(0, "Poliana")

    caixa_mensagem.delete("1.0", tk.END)


janela = tk.Tk()
janela.title("Gerador de Mensagens - Portabilidade INSS")
janela.geometry("750x700")

tk.Label(janela, text="Nome do Cliente").pack(pady=(10, 0))
entrada_nome = tk.Entry(janela, width=60)
entrada_nome.pack()

tk.Label(janela, text="Banco").pack(pady=(10, 0))
entrada_banco = tk.Entry(janela, width=60)
entrada_banco.pack()

tk.Label(janela, text="Parcela Antiga").pack(pady=(10, 0))
entrada_parcela_antiga = tk.Entry(janela, width=60)
entrada_parcela_antiga.pack()

tk.Label(janela, text="Nova Parcela").pack(pady=(10, 0))
entrada_parcela_nova = tk.Entry(janela, width=60)
entrada_parcela_nova.pack()

tk.Label(janela, text="Valor do Troco").pack(pady=(10, 0))
entrada_troco = tk.Entry(janela, width=60)
entrada_troco.pack()

tk.Label(janela, text="Nome do Atendente").pack(pady=(10, 0))
entrada_atendente = tk.Entry(janela, width=60)
entrada_atendente.insert(0, "Poliana")
entrada_atendente.pack()

tk.Button(
    janela,
    text="Gerar Mensagem",
    command=gerar_mensagem
).pack(pady=15)

caixa_mensagem = tk.Text(
    janela,
    width=85,
    height=18
)
caixa_mensagem.pack()

tk.Button(
    janela,
    text="Copiar Mensagem",
    command=copiar_mensagem
).pack(pady=5)

tk.Button(
    janela,
    text="Limpar Campos",
    command=limpar_campos
).pack(pady=5)

janela.mainloop()