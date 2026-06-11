import customtkinter as ctk
from tkinter import messagebox
import os


ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


MENSAGEM_PADRAO_INICIAL = """Olá, {nome},

Meu nome é {atendente} e entrei em contato para falar sobre a portabilidade do seu contrato, com redução da taxa de juros e liberação de troco.

Além disso, atualmente o INSS está permitindo uma carência de até 90 dias para o início do desconto da parcela após a realização da portabilidade.

Tenho uma proposta para o seu contrato do Banco {banco}:

✅ Parcela reduzida de {parcela_antiga} para {parcela_nova}
✅ Economia mensal de {economia}
✅ Liberação de troco no valor de {troco}
✅ Carência de 90 dias, ficando até 3 meses sem o desconto dessa parcela
✅ Sua conta de recebimento permanece a mesma, pois somos conveniados ao INSS

Podemos dar prosseguimento e garantir essa redução na sua parcela?"""


ARQUIVO_MENSAGEM = "mensagem_padrao.txt"


def carregar_mensagem_padrao():
    if not os.path.exists(ARQUIVO_MENSAGEM):
        with open(ARQUIVO_MENSAGEM, "w", encoding="utf-8") as arquivo:
            arquivo.write(MENSAGEM_PADRAO_INICIAL)

    with open(ARQUIVO_MENSAGEM, "r", encoding="utf-8") as arquivo:
        return arquivo.read()


mensagem_padrao = carregar_mensagem_padrao()


def converter_para_float(valor):
    try:
        return float(valor.replace(".", "").replace(",", "."))
    except ValueError:
        return None


def formatar_moeda_numero(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def formatar_moeda(valor):
    numero = converter_para_float(valor)

    if numero is None:
        return None

    return formatar_moeda_numero(numero)


def gerar_mensagem():
    nome = entrada_nome.get().strip()
    banco = entrada_banco.get().strip()

    valor_parcela_antiga = converter_para_float(entrada_parcela_antiga.get().strip())
    valor_parcela_nova = converter_para_float(entrada_parcela_nova.get().strip())
    valor_troco = converter_para_float(entrada_troco.get().strip())

    atendente = entrada_atendente.get().strip()

    if (
        not nome
        or not banco
        or valor_parcela_antiga is None
        or valor_parcela_nova is None
        or valor_troco is None
        or not atendente
    ):
        messagebox.showerror("Erro", "Preencha todos os campos corretamente.")
        return

    economia = valor_parcela_antiga - valor_parcela_nova

    if economia <= 0:
        messagebox.showwarning(
            "Aviso",
            "A nova parcela não é menor que a parcela antiga. Verifique os valores informados."
        )
        return

    parcela_antiga = formatar_moeda_numero(valor_parcela_antiga)
    parcela_nova = formatar_moeda_numero(valor_parcela_nova)
    troco = formatar_moeda_numero(valor_troco)
    economia_formatada = formatar_moeda_numero(economia)

    try:
        mensagem = mensagem_padrao.format(
            nome=nome,
            banco=banco,
            parcela_antiga=parcela_antiga,
            parcela_nova=parcela_nova,
            troco=troco,
            economia=economia_formatada,
            atendente=atendente
        )
    except KeyError as erro:
        messagebox.showerror(
            "Erro na mensagem padrão",
            f"A variável {erro} não existe.\n\nUse apenas:\n"
            "{nome}\n"
            "{banco}\n"
            "{parcela_antiga}\n"
            "{parcela_nova}\n"
            "{troco}\n"
            "{economia}\n"
            "{atendente}"
        )
        return

    caixa_mensagem.delete("1.0", "end")
    caixa_mensagem.insert("end", mensagem)


def copiar_mensagem():
    mensagem = caixa_mensagem.get("1.0", "end").strip()

    if not mensagem:
        messagebox.showwarning("Aviso", "Gere uma mensagem antes de copiar.")
        return

    janela.clipboard_clear()
    janela.clipboard_append(mensagem)
    messagebox.showinfo("Copiado", "Mensagem copiada para a área de transferência.")


def limpar_campos():
    entrada_nome.delete(0, "end")
    entrada_banco.delete(0, "end")
    entrada_parcela_antiga.delete(0, "end")
    entrada_parcela_nova.delete(0, "end")
    entrada_troco.delete(0, "end")

    entrada_atendente.delete(0, "end")
    entrada_atendente.insert(0, "Poliana")

    caixa_mensagem.delete("1.0", "end")


def alterar_mensagem_padrao():
    global mensagem_padrao

    janela_edicao = ctk.CTkToplevel(janela)
    janela_edicao.title("Alterar Mensagem Padrão")
    janela_edicao.geometry("850x650")
    janela_edicao.grab_set()

    titulo_edicao = ctk.CTkLabel(
        janela_edicao,
        text="Alterar Mensagem Padrão",
        font=("Arial", 20, "bold")
    )
    titulo_edicao.pack(pady=15)

    instrucoes = ctk.CTkLabel(
        janela_edicao,
        text=(
            "Variáveis disponíveis:\n"
            "{nome} | {banco} | {parcela_antiga} | {parcela_nova} | "
            "{troco} | {economia} | {atendente}"
        ),
        font=("Arial", 14)
    )
    instrucoes.pack(pady=5)

    caixa_edicao = ctk.CTkTextbox(
        janela_edicao,
        width=780,
        height=450
    )
    caixa_edicao.pack(pady=10)
    caixa_edicao.insert("end", mensagem_padrao)

    def salvar_mensagem_padrao():
        global mensagem_padrao

        novo_modelo = caixa_edicao.get("1.0", "end").strip()

        if not novo_modelo:
            messagebox.showwarning("Aviso", "A mensagem padrão não pode ficar vazia.")
            return

        mensagem_padrao = novo_modelo

        with open(ARQUIVO_MENSAGEM, "w", encoding="utf-8") as arquivo:
            arquivo.write(novo_modelo)

        messagebox.showinfo("Salvo", "Mensagem padrão salva com sucesso.")
        janela_edicao.destroy()

    frame_edicao_botoes = ctk.CTkFrame(janela_edicao)
    frame_edicao_botoes.pack(pady=10)

    botao_salvar = ctk.CTkButton(
        frame_edicao_botoes,
        text="Salvar Mensagem",
        width=180,
        command=salvar_mensagem_padrao
    )
    botao_salvar.pack(side="left", padx=10, pady=10)

    botao_cancelar = ctk.CTkButton(
        frame_edicao_botoes,
        text="Cancelar",
        width=180,
        command=janela_edicao.destroy
    )
    botao_cancelar.pack(side="left", padx=10, pady=10)


janela = ctk.CTk()
janela.title("Gerador de Mensagens - Portabilidade INSS")
janela.geometry("980x780")


titulo = ctk.CTkLabel(
    janela,
    text="Gerador de Mensagens - Portabilidade INSS",
    font=("Arial", 22, "bold")
)
titulo.pack(pady=20)


def criar_campo(texto):
    label = ctk.CTkLabel(janela, text=texto)
    label.pack(pady=(8, 0))

    entrada = ctk.CTkEntry(janela, width=450)
    entrada.pack(pady=3)

    return entrada


entrada_nome = criar_campo("Nome do Cliente")
entrada_banco = criar_campo("Banco")
entrada_parcela_antiga = criar_campo("Parcela Antiga")
entrada_parcela_nova = criar_campo("Nova Parcela")
entrada_troco = criar_campo("Valor do Troco")
entrada_atendente = criar_campo("Nome do Atendente")
entrada_atendente.insert(0, "Poliana")


frame_botoes = ctk.CTkFrame(janela)
frame_botoes.pack(pady=15)


botao_gerar = ctk.CTkButton(
    frame_botoes,
    text="Gerar Mensagem",
    width=160,
    command=gerar_mensagem
)
botao_gerar.pack(side="left", padx=8, pady=10)


botao_limpar = ctk.CTkButton(
    frame_botoes,
    text="Limpar Campos",
    width=160,
    command=limpar_campos
)
botao_limpar.pack(side="left", padx=8, pady=10)


botao_copiar = ctk.CTkButton(
    frame_botoes,
    text="Copiar Mensagem",
    width=160,
    command=copiar_mensagem
)
botao_copiar.pack(side="left", padx=8, pady=10)


botao_alterar = ctk.CTkButton(
    frame_botoes,
    text="Alterar Mensagem Padrão",
    width=210,
    command=alterar_mensagem_padrao
)
botao_alterar.pack(side="left", padx=8, pady=10)


caixa_mensagem = ctk.CTkTextbox(
    janela,
    width=850,
    height=240
)
caixa_mensagem.pack(pady=10)


janela.mainloop()