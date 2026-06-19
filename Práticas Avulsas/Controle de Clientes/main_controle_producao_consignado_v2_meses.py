import os
import re
import shutil
import sqlite3
import calendar
from datetime import datetime, date
from tkinter import ttk, messagebox, filedialog
import tkinter as tk

import customtkinter as ctk
import pandas as pd


APP_NAME = "Controle de Produção Consignado"
DB_FILE = "producao.db"

STATUS_OPTIONS = [
    "AG. DESBLOQUEIO",
    "AG. AVERBAÇÃO",
    "AG. INTERAÇÃO",
    "AG. CIP",
    "AVERBADO",
    "PAGO",
    "REPROVADO",
    "CANCELADO",
    "EM ANÁLISE",
    "PENDENTE",
]

PRODUTO_OPTIONS = ["PORT", "REFIN DA PORT", "NOVO"]
BLOQUEADO_OPTIONS = ["", "BLOQUEADO", "DESBLOQUEADO"]
PROMOTORA_OPTIONS = ["", "ÚNICA", "VIEIRA", "OUTRA"]

# Ano de referência da sua produção atual.
# Se você criar uma planilha de 2027 no futuro, basta alterar aqui.
ANO_BASE = 2026

MESES_NUMERO = {
    "JANEIRO": 1,
    "FEVEREIRO": 2,
    "MARÇO": 3,
    "MARCO": 3,
    "ABRIL": 4,
    "MAIO": 5,
    "JUNHO": 6,
    "JULHO": 7,
    "AGOSTO": 8,
    "SETEMBRO": 9,
    "OUTUBRO": 10,
    "NOVEMBRO": 11,
    "DEZEMBRO": 12,
}

MESES_NOME = [
    "JANEIRO",
    "FEVEREIRO",
    "MARÇO",
    "ABRIL",
    "MAIO",
    "JUNHO",
    "JULHO",
    "AGOSTO",
    "SETEMBRO",
    "OUTUBRO",
    "NOVEMBRO",
    "DEZEMBRO",
]

MESES_REF = [f"{mes}/{ANO_BASE}" for mes in MESES_NOME]

PENDENTES = ["AG. DESBLOQUEIO", "AG. AVERBAÇÃO", "AG. INTERAÇÃO", "AG. CIP", "EM ANÁLISE", "PENDENTE", "AVERBADO"]


# ---------------------------------------------------------------------
# Banco de dados
# ---------------------------------------------------------------------
def conectar():
    return sqlite3.connect(DB_FILE)


def criar_banco():
    with conectar() as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS propostas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data_proposta TEXT NOT NULL,
                mes_referencia TEXT,
                nome TEXT NOT NULL,
                status TEXT NOT NULL,
                telefone TEXT,
                cpf TEXT,
                banco TEXT,
                produto TEXT,
                valor REAL DEFAULT 0,
                pontos REAL DEFAULT 0,
                bloqueado TEXT,
                promotora TEXT,
                saldo_pmt TEXT,
                acerto TEXT,
                motivo TEXT,
                observacoes TEXT,
                criado_em TEXT NOT NULL,
                alterado_em TEXT NOT NULL
            )
            """
        )

        # Atualização leve para bancos antigos já criados sem a coluna mes_referencia.
        cursor.execute("PRAGMA table_info(propostas)")
        colunas_existentes = [col[1] for col in cursor.fetchall()]
        if "mes_referencia" not in colunas_existentes:
            cursor.execute("ALTER TABLE propostas ADD COLUMN mes_referencia TEXT")

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS historico_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                proposta_id INTEGER NOT NULL,
                status_anterior TEXT,
                status_novo TEXT NOT NULL,
                data_hora TEXT NOT NULL,
                observacao TEXT,
                FOREIGN KEY (proposta_id) REFERENCES propostas(id)
            )
            """
        )

        conn.commit()


# ---------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------
def somente_digitos(texto):
    return re.sub(r"\D", "", str(texto or ""))


def parse_moeda(valor):
    """
    Aceita:
    R$ 1.500,00
    1500,00
    1500.00
    1,500.00
    vazio
    """
    if valor is None:
        return 0.0

    if isinstance(valor, (int, float)):
        return float(valor)

    texto = str(valor).strip()
    if not texto:
        return 0.0

    texto = texto.replace("R$", "").replace(" ", "")

    # Caso brasileiro: 1.500,00
    if "," in texto and "." in texto:
        if texto.rfind(",") > texto.rfind("."):
            texto = texto.replace(".", "").replace(",", ".")
        else:
            texto = texto.replace(",", "")
    elif "," in texto:
        texto = texto.replace(".", "").replace(",", ".")

    try:
        return float(texto)
    except ValueError:
        raise ValueError(f"Valor monetário inválido: {valor}")


def formatar_moeda(valor):
    try:
        valor = float(valor or 0)
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "R$ 0,00"


def normalizar_data(valor):
    """
    Salva internamente como YYYY-MM-DD.
    Aceita DD/MM/YYYY, YYYY-MM-DD, datetime/date e datas vindas do Excel.
    """
    if valor is None or str(valor).strip() == "":
        return ""

    if isinstance(valor, datetime):
        return valor.strftime("%Y-%m-%d")

    if isinstance(valor, date):
        return valor.strftime("%Y-%m-%d")

    texto = str(valor).strip()

    formatos = ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d"]
    for fmt in formatos:
        try:
            return datetime.strptime(texto, fmt).strftime("%Y-%m-%d")
        except ValueError:
            pass

    # Datas numéricas do Excel, caso venham como número
    try:
        convertido = pd.to_datetime(valor, dayfirst=True, errors="coerce")
        if not pd.isna(convertido):
            return convertido.strftime("%Y-%m-%d")
    except Exception:
        pass

    raise ValueError(f"Data inválida: {valor}")


def data_br(data_iso):
    if not data_iso:
        return ""
    try:
        return datetime.strptime(str(data_iso), "%Y-%m-%d").strftime("%d/%m/%Y")
    except ValueError:
        return str(data_iso)


def mes_referencia_por_data(data_iso):
    try:
        dt = datetime.strptime(str(data_iso), "%Y-%m-%d")
        return f"{MESES_NOME[dt.month - 1]}/{dt.year}"
    except Exception:
        return ""


def normalizar_nome_aba(nome_aba):
    return (
        str(nome_aba or "")
        .strip()
        .upper()
        .replace("Ç", "C")
        .replace("Ã", "A")
        .replace("Á", "A")
        .replace("À", "A")
        .replace("Â", "A")
        .replace("É", "E")
        .replace("Ê", "E")
        .replace("Í", "I")
        .replace("Ó", "O")
        .replace("Ô", "O")
        .replace("Õ", "O")
        .replace("Ú", "U")
    )


def mes_referencia_por_aba(nome_aba):
    aba = normalizar_nome_aba(nome_aba)
    for mes in MESES_NOME:
        mes_normalizado = normalizar_nome_aba(mes)
        if aba == mes_normalizado or aba.startswith(mes_normalizado):
            return f"{mes}/{ANO_BASE}"
    return ""


def ajustar_data_para_mes_ref(data_iso, mes_ref):
    """
    Quando a proposta vem da aba JUNHO, por exemplo, força a data para JUNHO/2026
    preservando o dia. Isso resolve planilhas em que o Excel guardou ano/mês antigo.
    """
    if not data_iso or not mes_ref:
        return data_iso

    try:
        mes_nome, ano_txt = mes_ref.split("/")
        mes = MESES_NUMERO.get(mes_nome.upper())
        ano = int(ano_txt)
        dt = datetime.strptime(str(data_iso), "%Y-%m-%d")
        ultimo_dia = calendar.monthrange(ano, mes)[1]
        dia = min(dt.day, ultimo_dia)
        return datetime(ano, mes, dia).strftime("%Y-%m-%d")
    except Exception:
        return data_iso


def agora():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def normalizar_coluna(coluna):
    return (
        str(coluna)
        .strip()
        .upper()
        .replace(".", "")
        .replace("_", " ")
        .replace("-", " ")
        .replace("  ", " ")
    )


def limpar_nan(valor):
    if pd.isna(valor):
        return ""
    return valor


# ---------------------------------------------------------------------
# Aplicação
# ---------------------------------------------------------------------
class ControleProducaoApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        criar_banco()

        self.title(APP_NAME)
        self.geometry("1500x830")
        self.minsize(1250, 720)

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.proposta_selecionada_id = None
        self.dados_atual_tabela = []

        self._montar_layout()
        self.carregar_tabela()
        self.atualizar_resumo()

    # -----------------------------------------------------------------
    # Layout
    # -----------------------------------------------------------------
    def _montar_layout(self):
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

        titulo = ctk.CTkLabel(self, text=APP_NAME, font=ctk.CTkFont(size=24, weight="bold"))
        titulo.grid(row=0, column=0, columnspan=2, padx=15, pady=(10, 5), sticky="w")

        self._montar_resumo()
        self._montar_formulario()
        self._montar_filtros()
        self._montar_tabela()
        self._montar_botoes_inferiores()

    def _montar_resumo(self):
        self.frame_resumo = ctk.CTkFrame(self)
        self.frame_resumo.grid(row=1, column=0, columnspan=2, padx=15, pady=5, sticky="ew")

        for i in range(8):
            self.frame_resumo.grid_columnconfigure(i, weight=1)

        self.lbl_total = self._card_resumo("Total", "0", 0)
        self.lbl_pagas = self._card_resumo("Pagas", "0", 1)
        self.lbl_reprovadas = self._card_resumo("Reprovadas", "0", 2)
        self.lbl_andamento = self._card_resumo("Em andamento", "0", 3)
        self.lbl_valor_total = self._card_resumo("Valor total", "R$ 0,00", 4)
        self.lbl_valor_pago = self._card_resumo("Valor pago", "R$ 0,00", 5)
        self.lbl_pontos_total = self._card_resumo("Pontos total", "R$ 0,00", 6)
        self.lbl_pontos_pago = self._card_resumo("Pontos pagos", "R$ 0,00", 7)

    def _card_resumo(self, titulo, valor, coluna):
        frame = ctk.CTkFrame(self.frame_resumo)
        frame.grid(row=0, column=coluna, padx=5, pady=8, sticky="ew")

        ctk.CTkLabel(frame, text=titulo, font=ctk.CTkFont(size=12)).pack(pady=(6, 0))
        lbl = ctk.CTkLabel(frame, text=valor, font=ctk.CTkFont(size=16, weight="bold"))
        lbl.pack(pady=(0, 6))
        return lbl

    def _montar_formulario(self):
        self.frame_form = ctk.CTkFrame(self)
        self.frame_form.grid(row=2, column=0, padx=(15, 8), pady=5, sticky="ns")
        self.frame_form.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.frame_form, text="Cadastro / Edição", font=ctk.CTkFont(size=18, weight="bold")).grid(
            row=0, column=0, columnspan=2, padx=10, pady=(10, 8), sticky="w"
        )

        self.campos = {}

        linha = 1
        self._add_entry("Data", "data_proposta", linha, placeholder="DD/MM/AAAA")
        linha += 1
        self._add_entry("Nome", "nome", linha)
        linha += 1
        self._add_combo("Status", "status", STATUS_OPTIONS, linha)
        linha += 1
        self._add_entry("Telefone", "telefone", linha)
        linha += 1
        self._add_entry("CPF", "cpf", linha)
        linha += 1
        self._add_entry("Banco", "banco", linha)
        linha += 1
        self._add_combo("Produto", "produto", PRODUTO_OPTIONS, linha)
        linha += 1
        self._add_entry("Valor", "valor", linha, placeholder="R$ 0,00")
        linha += 1
        self._add_entry("Pontos", "pontos", linha, placeholder="R$ 0,00")
        linha += 1
        self._add_combo("Bloqueado", "bloqueado", BLOQUEADO_OPTIONS, linha)
        linha += 1
        self._add_combo("Promotora", "promotora", PROMOTORA_OPTIONS, linha)
        linha += 1
        self._add_entry("Saldo PMT", "saldo_pmt", linha)
        linha += 1
        self._add_entry("Acerto", "acerto", linha)
        linha += 1
        self._add_entry("Motivo", "motivo", linha)
        linha += 1

        ctk.CTkLabel(self.frame_form, text="Observações").grid(row=linha, column=0, padx=10, pady=5, sticky="w")
        self.txt_observacoes = ctk.CTkTextbox(self.frame_form, height=80, width=280)
        self.txt_observacoes.grid(row=linha, column=1, padx=10, pady=5, sticky="ew")
        linha += 1

        frame_botoes = ctk.CTkFrame(self.frame_form, fg_color="transparent")
        frame_botoes.grid(row=linha, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        frame_botoes.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(frame_botoes, text="Salvar", command=self.salvar_proposta).grid(row=0, column=0, padx=4, pady=4, sticky="ew")
        ctk.CTkButton(frame_botoes, text="Limpar", command=self.limpar_formulario).grid(row=0, column=1, padx=4, pady=4, sticky="ew")

        ctk.CTkButton(frame_botoes, text="Excluir", fg_color="#9b1c1c", hover_color="#7f1717", command=self.excluir_proposta).grid(
            row=1, column=0, padx=4, pady=4, sticky="ew"
        )
        ctk.CTkButton(frame_botoes, text="Ver histórico", command=self.ver_historico).grid(row=1, column=1, padx=4, pady=4, sticky="ew")

        ctk.CTkButton(frame_botoes, text="Copiar telefone", command=self.copiar_telefone).grid(row=2, column=0, padx=4, pady=4, sticky="ew")
        ctk.CTkButton(frame_botoes, text="Copiar CPF", command=self.copiar_cpf).grid(row=2, column=1, padx=4, pady=4, sticky="ew")

        ctk.CTkButton(frame_botoes, text="Copiar resumo", command=self.copiar_resumo_proposta).grid(
            row=3, column=0, columnspan=2, padx=4, pady=4, sticky="ew"
        )

        self.limpar_formulario()

    def _add_entry(self, label, key, row, placeholder=""):
        ctk.CTkLabel(self.frame_form, text=label).grid(row=row, column=0, padx=10, pady=5, sticky="w")
        entry = ctk.CTkEntry(self.frame_form, placeholder_text=placeholder, width=220)
        entry.grid(row=row, column=1, padx=10, pady=5, sticky="ew")
        self.campos[key] = entry

    def _add_combo(self, label, key, values, row):
        ctk.CTkLabel(self.frame_form, text=label).grid(row=row, column=0, padx=10, pady=5, sticky="w")
        combo = ctk.CTkComboBox(self.frame_form, values=values, width=220)
        combo.grid(row=row, column=1, padx=10, pady=5, sticky="ew")
        combo.set(values[0] if values else "")
        self.campos[key] = combo

    def _montar_filtros(self):
        self.frame_direito = ctk.CTkFrame(self)
        self.frame_direito.grid(row=2, column=1, padx=(8, 15), pady=5, sticky="nsew")
        self.frame_direito.grid_columnconfigure(0, weight=1)
        self.frame_direito.grid_rowconfigure(1, weight=1)

        self.frame_filtros = ctk.CTkFrame(self.frame_direito)
        self.frame_filtros.grid(row=0, column=0, padx=8, pady=8, sticky="ew")

        for i in range(11):
            self.frame_filtros.grid_columnconfigure(i, weight=1)

        ctk.CTkLabel(self.frame_filtros, text="Busca rápida").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.f_busca = ctk.CTkEntry(self.frame_filtros, placeholder_text="Nome, CPF ou telefone")
        self.f_busca.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(self.frame_filtros, text="Banco").grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.f_banco = ctk.CTkEntry(self.frame_filtros)
        self.f_banco.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(self.frame_filtros, text="Status").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.f_status = ctk.CTkComboBox(self.frame_filtros, values=["TODOS"] + STATUS_OPTIONS)
        self.f_status.grid(row=1, column=2, padx=5, pady=5, sticky="ew")
        self.f_status.set("TODOS")

        ctk.CTkLabel(self.frame_filtros, text="Produto").grid(row=0, column=3, padx=5, pady=5, sticky="w")
        self.f_produto = ctk.CTkComboBox(self.frame_filtros, values=["TODOS"] + PRODUTO_OPTIONS)
        self.f_produto.grid(row=1, column=3, padx=5, pady=5, sticky="ew")
        self.f_produto.set("TODOS")

        ctk.CTkLabel(self.frame_filtros, text="Promotora").grid(row=0, column=4, padx=5, pady=5, sticky="w")
        self.f_promotora = ctk.CTkEntry(self.frame_filtros)
        self.f_promotora.grid(row=1, column=4, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(self.frame_filtros, text="Bloqueio").grid(row=0, column=5, padx=5, pady=5, sticky="w")
        self.f_bloqueado = ctk.CTkComboBox(self.frame_filtros, values=["TODOS", "BLOQUEADO", "DESBLOQUEADO"])
        self.f_bloqueado.grid(row=1, column=5, padx=5, pady=5, sticky="ew")
        self.f_bloqueado.set("TODOS")

        ctk.CTkLabel(self.frame_filtros, text="Mês").grid(row=0, column=6, padx=5, pady=5, sticky="w")
        self.f_mes = ctk.CTkComboBox(self.frame_filtros, values=["TODOS"] + MESES_REF)
        self.f_mes.grid(row=1, column=6, padx=5, pady=5, sticky="ew")
        self.f_mes.set("TODOS")

        ctk.CTkLabel(self.frame_filtros, text="Data inicial").grid(row=0, column=7, padx=5, pady=5, sticky="w")
        self.f_data_ini = ctk.CTkEntry(self.frame_filtros, placeholder_text="DD/MM/AAAA")
        self.f_data_ini.grid(row=1, column=7, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(self.frame_filtros, text="Data final").grid(row=0, column=8, padx=5, pady=5, sticky="w")
        self.f_data_fim = ctk.CTkEntry(self.frame_filtros, placeholder_text="DD/MM/AAAA")
        self.f_data_fim.grid(row=1, column=8, padx=5, pady=5, sticky="ew")

        self.f_somente = ctk.CTkComboBox(self.frame_filtros, values=["TODAS", "SOMENTE PAGAS", "SOMENTE PENDENTES", "SOMENTE REPROVADAS"])
        self.f_somente.grid(row=1, column=9, padx=5, pady=5, sticky="ew")
        self.f_somente.set("TODAS")

        frame_btn = ctk.CTkFrame(self.frame_filtros, fg_color="transparent")
        frame_btn.grid(row=1, column=10, padx=5, pady=5, sticky="ew")
        frame_btn.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(frame_btn, text="Filtrar", command=self.carregar_tabela).grid(row=0, column=0, padx=2, sticky="ew")
        ctk.CTkButton(frame_btn, text="Limpar filtros", command=self.limpar_filtros).grid(row=0, column=1, padx=2, sticky="ew")

        self.f_busca.bind("<Return>", lambda e: self.carregar_tabela())

    def _montar_tabela(self):
        frame_tabela = ctk.CTkFrame(self.frame_direito)
        frame_tabela.grid(row=1, column=0, padx=8, pady=8, sticky="nsew")
        frame_tabela.grid_columnconfigure(0, weight=1)
        frame_tabela.grid_rowconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", rowheight=26, font=("Calibri", 10))
        style.configure("Treeview.Heading", font=("Calibri", 10, "bold"))

        self.colunas = [
            "ID",
            "DIA",
            "MÊS",
            "NOME",
            "STATUS",
            "TELEFONE",
            "CPF",
            "BANCO",
            "PRODUTO",
            "VALOR",
            "PONTOS",
            "BLOQUEADO",
            "PROMOTORA",
            "SALDO PMT",
            "ACERTO",
            "MOTIVO",
        ]

        self.tree = ttk.Treeview(frame_tabela, columns=self.colunas, show="headings")
        self.tree.grid(row=0, column=0, sticky="nsew")

        scrollbar_y = ttk.Scrollbar(frame_tabela, orient="vertical", command=self.tree.yview)
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar_y.set)

        scrollbar_x = ttk.Scrollbar(frame_tabela, orient="horizontal", command=self.tree.xview)
        scrollbar_x.grid(row=1, column=0, sticky="ew")
        self.tree.configure(xscrollcommand=scrollbar_x.set)

        larguras = {
            "ID": 50,
            "DIA": 90,
            "MÊS": 110,
            "NOME": 230,
            "STATUS": 130,
            "TELEFONE": 110,
            "CPF": 120,
            "BANCO": 90,
            "PRODUTO": 110,
            "VALOR": 100,
            "PONTOS": 100,
            "BLOQUEADO": 110,
            "PROMOTORA": 110,
            "SALDO PMT": 100,
            "ACERTO": 90,
            "MOTIVO": 180,
        }

        for col in self.colunas:
            self.tree.heading(col, text=col, command=lambda c=col: self.ordenar_por_coluna(c))
            self.tree.column(col, width=larguras.get(col, 100), anchor="center")

        self.tree.column("NOME", anchor="w")
        self.tree.column("MOTIVO", anchor="w")

        self.tree.tag_configure("pago", background="#d9ead3")
        self.tree.tag_configure("reprovado", background="#f4cccc")
        self.tree.tag_configure("andamento", background="#fff2cc")
        self.tree.tag_configure("averbado", background="#cfe2f3")
        self.tree.tag_configure("bloqueado", background="#eadcf8")

        self.tree.bind("<<TreeviewSelect>>", self.ao_selecionar_linha)

    def _montar_botoes_inferiores(self):
        frame = ctk.CTkFrame(self)
        frame.grid(row=3, column=0, columnspan=2, padx=15, pady=(5, 12), sticky="ew")

        for i in range(6):
            frame.grid_columnconfigure(i, weight=1)

        ctk.CTkButton(frame, text="Atualizar tabela", command=self.carregar_tabela).grid(row=0, column=0, padx=5, pady=8, sticky="ew")
        ctk.CTkButton(frame, text="Importar Excel", command=self.importar_excel).grid(row=0, column=1, padx=5, pady=8, sticky="ew")
        ctk.CTkButton(frame, text="Exportar Excel", command=self.exportar_excel).grid(row=0, column=2, padx=5, pady=8, sticky="ew")
        ctk.CTkButton(frame, text="Gerar backup", command=self.gerar_backup).grid(row=0, column=3, padx=5, pady=8, sticky="ew")
        ctk.CTkButton(frame, text="Total por banco", command=self.ver_total_por_banco).grid(row=0, column=4, padx=5, pady=8, sticky="ew")
        ctk.CTkButton(frame, text="Total por promotora", command=self.ver_total_por_promotora).grid(row=0, column=5, padx=5, pady=8, sticky="ew")

    # -----------------------------------------------------------------
    # CRUD
    # -----------------------------------------------------------------
    def pegar_dados_formulario(self):
        observacoes = self.txt_observacoes.get("1.0", "end").strip()

        data_proposta = self.campos["data_proposta"].get().strip()
        if not data_proposta:
            data_proposta = datetime.now().strftime("%d/%m/%Y")

        data_normalizada = normalizar_data(data_proposta)

        dados = {
            "data_proposta": data_normalizada,
            "mes_referencia": mes_referencia_por_data(data_normalizada),
            "nome": self.campos["nome"].get().strip().upper(),
            "status": self.campos["status"].get().strip().upper(),
            "telefone": self.campos["telefone"].get().strip(),
            "cpf": self.campos["cpf"].get().strip(),
            "banco": self.campos["banco"].get().strip().upper(),
            "produto": self.campos["produto"].get().strip().upper(),
            "valor": parse_moeda(self.campos["valor"].get()),
            "pontos": parse_moeda(self.campos["pontos"].get()),
            "bloqueado": self.campos["bloqueado"].get().strip().upper(),
            "promotora": self.campos["promotora"].get().strip().upper(),
            "saldo_pmt": self.campos["saldo_pmt"].get().strip().upper(),
            "acerto": self.campos["acerto"].get().strip().upper(),
            "motivo": self.campos["motivo"].get().strip().upper(),
            "observacoes": observacoes,
        }
        return dados

    def validar_dados(self, dados):
        if not dados["nome"]:
            raise ValueError("O nome do cliente é obrigatório.")

        if not dados["status"]:
            raise ValueError("O status é obrigatório.")

        if dados["cpf"] and len(somente_digitos(dados["cpf"])) < 11:
            raise ValueError("O CPF precisa ter pelo menos 11 dígitos.")

        if not dados["data_proposta"]:
            raise ValueError("A data é obrigatória.")

    def salvar_proposta(self):
        try:
            dados = self.pegar_dados_formulario()
            self.validar_dados(dados)
        except Exception as e:
            messagebox.showerror("Erro de validação", str(e))
            return

        try:
            with conectar() as conn:
                cursor = conn.cursor()

                if self.proposta_selecionada_id:
                    cursor.execute("SELECT status FROM propostas WHERE id = ?", (self.proposta_selecionada_id,))
                    resultado = cursor.fetchone()
                    status_anterior = resultado[0] if resultado else ""

                    cursor.execute(
                        """
                        UPDATE propostas
                        SET data_proposta = ?, mes_referencia = ?, nome = ?, status = ?, telefone = ?, cpf = ?,
                            banco = ?, produto = ?, valor = ?, pontos = ?, bloqueado = ?,
                            promotora = ?, saldo_pmt = ?, acerto = ?, motivo = ?,
                            observacoes = ?, alterado_em = ?
                        WHERE id = ?
                        """,
                        (
                            dados["data_proposta"],
                            dados["mes_referencia"],
                            dados["nome"],
                            dados["status"],
                            dados["telefone"],
                            dados["cpf"],
                            dados["banco"],
                            dados["produto"],
                            dados["valor"],
                            dados["pontos"],
                            dados["bloqueado"],
                            dados["promotora"],
                            dados["saldo_pmt"],
                            dados["acerto"],
                            dados["motivo"],
                            dados["observacoes"],
                            agora(),
                            self.proposta_selecionada_id,
                        ),
                    )

                    if status_anterior != dados["status"]:
                        cursor.execute(
                            """
                            INSERT INTO historico_status
                            (proposta_id, status_anterior, status_novo, data_hora, observacao)
                            VALUES (?, ?, ?, ?, ?)
                            """,
                            (
                                self.proposta_selecionada_id,
                                status_anterior,
                                dados["status"],
                                agora(),
                                dados["motivo"] or dados["observacoes"],
                            ),
                        )
                    mensagem = "Proposta atualizada com sucesso."

                else:
                    criado = agora()
                    cursor.execute(
                        """
                        INSERT INTO propostas (
                            data_proposta, mes_referencia, nome, status, telefone, cpf, banco, produto,
                            valor, pontos, bloqueado, promotora, saldo_pmt, acerto,
                            motivo, observacoes, criado_em, alterado_em
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            dados["data_proposta"],
                            dados["mes_referencia"],
                            dados["nome"],
                            dados["status"],
                            dados["telefone"],
                            dados["cpf"],
                            dados["banco"],
                            dados["produto"],
                            dados["valor"],
                            dados["pontos"],
                            dados["bloqueado"],
                            dados["promotora"],
                            dados["saldo_pmt"],
                            dados["acerto"],
                            dados["motivo"],
                            dados["observacoes"],
                            criado,
                            criado,
                        ),
                    )

                    proposta_id = cursor.lastrowid
                    cursor.execute(
                        """
                        INSERT INTO historico_status
                        (proposta_id, status_anterior, status_novo, data_hora, observacao)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (proposta_id, "", dados["status"], agora(), "Cadastro inicial"),
                    )
                    mensagem = "Proposta cadastrada com sucesso."

                conn.commit()

            messagebox.showinfo("Sucesso", mensagem)
            self.limpar_formulario()
            self.carregar_tabela()

        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível salvar a proposta:\n{e}")

    def excluir_proposta(self):
        if not self.proposta_selecionada_id:
            messagebox.showwarning("Atenção", "Selecione uma proposta para excluir.")
            return

        confirmar = messagebox.askyesno("Confirmar exclusão", "Deseja excluir a proposta selecionada?")
        if not confirmar:
            return

        try:
            with conectar() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM historico_status WHERE proposta_id = ?", (self.proposta_selecionada_id,))
                cursor.execute("DELETE FROM propostas WHERE id = ?", (self.proposta_selecionada_id,))
                conn.commit()

            messagebox.showinfo("Sucesso", "Proposta excluída.")
            self.limpar_formulario()
            self.carregar_tabela()

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao excluir:\n{e}")

    # -----------------------------------------------------------------
    # Tabela e filtros
    # -----------------------------------------------------------------
    def montar_where_filtros(self):
        where = []
        params = []

        busca = self.f_busca.get().strip()
        if busca:
            where.append("(nome LIKE ? OR cpf LIKE ? OR telefone LIKE ?)")
            params.extend([f"%{busca}%", f"%{busca}%", f"%{busca}%"])

        banco = self.f_banco.get().strip()
        if banco:
            where.append("banco LIKE ?")
            params.append(f"%{banco.upper()}%")

        status = self.f_status.get()
        if status and status != "TODOS":
            where.append("status = ?")
            params.append(status)

        produto = self.f_produto.get()
        if produto and produto != "TODOS":
            where.append("produto = ?")
            params.append(produto)

        promotora = self.f_promotora.get().strip()
        if promotora:
            where.append("promotora LIKE ?")
            params.append(f"%{promotora.upper()}%")

        bloqueado = self.f_bloqueado.get()
        if bloqueado and bloqueado != "TODOS":
            where.append("bloqueado = ?")
            params.append(bloqueado)

        mes = self.f_mes.get()
        if mes and mes != "TODOS":
            where.append("mes_referencia = ?")
            params.append(mes)

        if self.f_data_ini.get().strip():
            where.append("data_proposta >= ?")
            params.append(normalizar_data(self.f_data_ini.get().strip()))

        if self.f_data_fim.get().strip():
            where.append("data_proposta <= ?")
            params.append(normalizar_data(self.f_data_fim.get().strip()))

        somente = self.f_somente.get()
        if somente == "SOMENTE PAGAS":
            where.append("status = 'PAGO'")
        elif somente == "SOMENTE REPROVADAS":
            where.append("status = 'REPROVADO'")
        elif somente == "SOMENTE PENDENTES":
            placeholders = ",".join(["?"] * len(PENDENTES))
            where.append(f"status IN ({placeholders})")
            params.extend(PENDENTES)

        sql_where = ""
        if where:
            sql_where = "WHERE " + " AND ".join(where)

        return sql_where, params

    def carregar_tabela(self):
        try:
            sql_where, params = self.montar_where_filtros()
        except Exception as e:
            messagebox.showerror("Erro nos filtros", str(e))
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        query = f"""
            SELECT id, data_proposta, mes_referencia, nome, status, telefone, cpf, banco, produto,
                   valor, pontos, bloqueado, promotora, saldo_pmt, acerto, motivo,
                   observacoes, criado_em, alterado_em
            FROM propostas
            {sql_where}
            ORDER BY data_proposta DESC, id DESC
        """

        with conectar() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            linhas = cursor.fetchall()

        self.dados_atual_tabela = linhas

        for row in linhas:
            (
                id_,
                data_proposta,
                mes_referencia,
                nome,
                status,
                telefone,
                cpf,
                banco,
                produto,
                valor,
                pontos,
                bloqueado,
                promotora,
                saldo_pmt,
                acerto,
                motivo,
                *_,
            ) = row

            valores = (
                id_,
                data_br(data_proposta),
                mes_referencia or mes_referencia_por_data(data_proposta),
                nome,
                status,
                telefone,
                cpf,
                banco,
                produto,
                formatar_moeda(valor),
                formatar_moeda(pontos),
                bloqueado,
                promotora,
                saldo_pmt,
                acerto,
                motivo,
            )

            tag = self.definir_tag(status, bloqueado)
            self.tree.insert("", "end", values=valores, tags=(tag,))

        self.atualizar_resumo()

    def definir_tag(self, status, bloqueado):
        status = (status or "").upper()
        bloqueado = (bloqueado or "").upper()

        if bloqueado == "BLOQUEADO":
            return "bloqueado"
        if status == "PAGO":
            return "pago"
        if status == "REPROVADO":
            return "reprovado"
        if status == "AVERBADO":
            return "averbado"
        if status.startswith("AG.") or status in ["EM ANÁLISE", "PENDENTE"]:
            return "andamento"
        return ""

    def ao_selecionar_linha(self, event=None):
        selecionado = self.tree.selection()
        if not selecionado:
            return

        valores = self.tree.item(selecionado[0], "values")
        proposta_id = valores[0]

        with conectar() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, data_proposta, mes_referencia, nome, status, telefone, cpf, banco, produto,
                       valor, pontos, bloqueado, promotora, saldo_pmt, acerto, motivo,
                       observacoes
                FROM propostas
                WHERE id = ?
                """,
                (proposta_id,),
            )
            row = cursor.fetchone()

        if not row:
            return

        (
            id_,
            data_proposta,
            mes_referencia,
            nome,
            status,
            telefone,
            cpf,
            banco,
            produto,
            valor,
            pontos,
            bloqueado,
            promotora,
            saldo_pmt,
            acerto,
            motivo,
            observacoes,
        ) = row

        self.proposta_selecionada_id = id_

        self._set_entry("data_proposta", data_br(data_proposta))
        self._set_entry("nome", nome)
        self._set_combo("status", status)
        self._set_entry("telefone", telefone)
        self._set_entry("cpf", cpf)
        self._set_entry("banco", banco)
        self._set_combo("produto", produto)
        self._set_entry("valor", formatar_moeda(valor))
        self._set_entry("pontos", formatar_moeda(pontos))
        self._set_combo("bloqueado", bloqueado)
        self._set_combo("promotora", promotora)
        self._set_entry("saldo_pmt", saldo_pmt)
        self._set_entry("acerto", acerto)
        self._set_entry("motivo", motivo)

        self.txt_observacoes.delete("1.0", "end")
        self.txt_observacoes.insert("1.0", observacoes or "")

    def _set_entry(self, key, value):
        self.campos[key].delete(0, "end")
        self.campos[key].insert(0, value or "")

    def _set_combo(self, key, value):
        self.campos[key].set(value or "")

    def limpar_formulario(self):
        self.proposta_selecionada_id = None

        for key, widget in self.campos.items():
            if isinstance(widget, ctk.CTkEntry):
                widget.delete(0, "end")
            elif isinstance(widget, ctk.CTkComboBox):
                if key == "status":
                    widget.set("PENDENTE")
                elif key == "bloqueado":
                    widget.set("DESBLOQUEADO")
                elif key == "produto":
                    widget.set("PORT")
                elif key == "promotora":
                    widget.set("")
                else:
                    widget.set("")

        self.campos["data_proposta"].insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.txt_observacoes.delete("1.0", "end")

        # Na inicialização, o formulário é montado antes da tabela.
        # Por isso, self.tree ainda pode não existir nesse momento.
        if hasattr(self, "tree"):
            for item in self.tree.selection():
                self.tree.selection_remove(item)

    def limpar_filtros(self):
        self.f_busca.delete(0, "end")
        self.f_banco.delete(0, "end")
        self.f_status.set("TODOS")
        self.f_produto.set("TODOS")
        self.f_promotora.delete(0, "end")
        self.f_bloqueado.set("TODOS")
        self.f_mes.set("TODOS")
        self.f_data_ini.delete(0, "end")
        self.f_data_fim.delete(0, "end")
        self.f_somente.set("TODAS")
        self.carregar_tabela()

    def ordenar_por_coluna(self, coluna):
        # Ordenação visual simples da Treeview.
        itens = [(self.tree.set(k, coluna), k) for k in self.tree.get_children("")]

        def chave(item):
            valor = item[0]
            if coluna in ["VALOR", "PONTOS"]:
                try:
                    return parse_moeda(valor)
                except Exception:
                    return 0
            if coluna == "DIA":
                try:
                    return datetime.strptime(valor, "%d/%m/%Y")
                except Exception:
                    return datetime.min
            return str(valor).upper()

        itens.sort(key=chave)

        for index, (_, k) in enumerate(itens):
            self.tree.move(k, "", index)

    # -----------------------------------------------------------------
    # Resumos
    # -----------------------------------------------------------------
    def atualizar_resumo(self):
        try:
            sql_where, params = self.montar_where_filtros()
        except Exception:
            sql_where, params = "", []

        query = f"""
            SELECT status, valor, pontos, banco, promotora
            FROM propostas
            {sql_where}
        """

        with conectar() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()

        total = len(rows)
        pagas = sum(1 for r in rows if r[0] == "PAGO")
        reprovadas = sum(1 for r in rows if r[0] == "REPROVADO")
        andamento = sum(1 for r in rows if r[0] in PENDENTES)
        valor_total = sum(float(r[1] or 0) for r in rows)
        valor_pago = sum(float(r[1] or 0) for r in rows if r[0] == "PAGO")
        pontos_total = sum(float(r[2] or 0) for r in rows)
        pontos_pago = sum(float(r[2] or 0) for r in rows if r[0] == "PAGO")

        self.lbl_total.configure(text=str(total))
        self.lbl_pagas.configure(text=str(pagas))
        self.lbl_reprovadas.configure(text=str(reprovadas))
        self.lbl_andamento.configure(text=str(andamento))
        self.lbl_valor_total.configure(text=formatar_moeda(valor_total))
        self.lbl_valor_pago.configure(text=formatar_moeda(valor_pago))
        self.lbl_pontos_total.configure(text=formatar_moeda(pontos_total))
        self.lbl_pontos_pago.configure(text=formatar_moeda(pontos_pago))

    def ver_total_por_banco(self):
        self._mostrar_agrupamento("banco", "Total por banco")

    def ver_total_por_promotora(self):
        self._mostrar_agrupamento("promotora", "Total por promotora")

    def _mostrar_agrupamento(self, campo, titulo):
        with conectar() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"""
                SELECT COALESCE(NULLIF({campo}, ''), 'NÃO INFORMADO') AS grupo,
                       COUNT(*),
                       SUM(valor),
                       SUM(pontos),
                       SUM(CASE WHEN status = 'PAGO' THEN valor ELSE 0 END),
                       SUM(CASE WHEN status = 'PAGO' THEN pontos ELSE 0 END)
                FROM propostas
                GROUP BY grupo
                ORDER BY SUM(valor) DESC
                """
            )
            rows = cursor.fetchall()

        janela = ctk.CTkToplevel(self)
        janela.title(titulo)
        janela.geometry("650x420")
        janela.grab_set()

        texto = ctk.CTkTextbox(janela, width=620, height=380)
        texto.pack(padx=15, pady=15, fill="both", expand=True)

        linhas = []
        for grupo, qtd, valor, pontos, valor_pago, pontos_pago in rows:
            linhas.append(
                f"{grupo}\n"
                f"  Propostas: {qtd}\n"
                f"  Valor total: {formatar_moeda(valor)}\n"
                f"  Pontos total: {formatar_moeda(pontos)}\n"
                f"  Valor pago: {formatar_moeda(valor_pago)}\n"
                f"  Pontos pagos: {formatar_moeda(pontos_pago)}\n"
            )

        texto.insert("1.0", "\n".join(linhas) if linhas else "Nenhum registro encontrado.")
        texto.configure(state="disabled")

    # -----------------------------------------------------------------
    # Excel
    # -----------------------------------------------------------------
    def importar_excel(self):
        caminho = filedialog.askopenfilename(
            title="Selecione a planilha",
            filetypes=[("Arquivos Excel", "*.xlsx *.xls"), ("Todos os arquivos", "*.*")]
        )

        if not caminho:
            return

        try:
            xls = pd.ExcelFile(caminho)

            # Importa automaticamente somente as abas mensais.
            # Isso evita puxar a primeira aba "AUMENTO" ou "Dash" por engano.
            abas_mensais = [aba for aba in xls.sheet_names if mes_referencia_por_aba(aba)]

            if not abas_mensais:
                abas_para_importar = [xls.sheet_names[0]]
            else:
                abas_para_importar = abas_mensais

            confirmar = messagebox.askyesno(
                "Importação por mês",
                "Encontrei estas abas mensais na planilha:\n\n"
                + ", ".join(abas_para_importar)
                + "\n\nDeseja importar essas abas e usar o nome da aba como mês de referência?"
            )

            if not confirmar:
                return

            importados = 0
            duplicados = 0
            ignorados = 0
            abas_importadas = []

            with conectar() as conn:
                cursor = conn.cursor()

                for aba in abas_para_importar:
                    df = pd.read_excel(caminho, sheet_name=aba)

                    if df.empty:
                        continue

                    abas_importadas.append(aba)
                    mes_ref_aba = mes_referencia_por_aba(aba)

                    mapa = {normalizar_coluna(col): col for col in df.columns}

                    def get_col(row, nome):
                        col = mapa.get(normalizar_coluna(nome))
                        if col is None:
                            return ""
                        return limpar_nan(row.get(col, ""))

                    for _, row in df.iterrows():
                        valores_brutos = [limpar_nan(v) for v in row.values]
                        if all(str(v).strip() == "" for v in valores_brutos):
                            ignorados += 1
                            continue

                        nome = str(get_col(row, "NOME")).strip().upper()
                        if not nome:
                            ignorados += 1
                            continue

                        try:
                            data_proposta = normalizar_data(get_col(row, "DIA") or datetime.now().strftime("%d/%m/%Y"))
                        except Exception:
                            data_proposta = datetime.now().strftime("%Y-%m-%d")

                        # Se a aba é "JUNHO", por exemplo, a data vira JUNHO/2026,
                        # preservando o dia. Assim a planilha não cai em 2025 por acidente.
                        if mes_ref_aba:
                            data_proposta = ajustar_data_para_mes_ref(data_proposta, mes_ref_aba)
                            mes_referencia = mes_ref_aba
                        else:
                            mes_referencia = mes_referencia_por_data(data_proposta)

                        status = str(get_col(row, "STATUS") or "PENDENTE").strip().upper()
                        telefone = str(get_col(row, "TELEFONE")).strip()
                        cpf = str(get_col(row, "CPF")).strip()
                        banco = str(get_col(row, "BANCO")).strip().upper()
                        produto = str(get_col(row, "PRODUTO")).strip().upper()
                        valor = parse_moeda(get_col(row, "VALOR"))
                        pontos = parse_moeda(get_col(row, "PONTOS"))
                        bloqueado = str(get_col(row, "BLOQUEADO")).strip().upper()
                        promotora = str(get_col(row, "PROMOTORA")).strip().upper()
                        saldo_pmt = str(get_col(row, "SALDO PMT") or get_col(row, "SALDO PMT.")).strip().upper()
                        acerto = str(get_col(row, "ACERTO")).strip().upper()
                        motivo = str(get_col(row, "MOTIVO")).strip().upper()

                        cursor.execute(
                            """
                            SELECT id FROM propostas
                            WHERE data_proposta = ? AND mes_referencia = ? AND nome = ? AND cpf = ? AND banco = ?
                                  AND produto = ? AND valor = ? AND pontos = ?
                            """,
                            (data_proposta, mes_referencia, nome, cpf, banco, produto, valor, pontos),
                        )

                        if cursor.fetchone():
                            duplicados += 1
                            continue

                        criado = agora()
                        cursor.execute(
                            """
                            INSERT INTO propostas (
                                data_proposta, mes_referencia, nome, status, telefone, cpf, banco, produto,
                                valor, pontos, bloqueado, promotora, saldo_pmt, acerto,
                                motivo, observacoes, criado_em, alterado_em
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            (
                                data_proposta,
                                mes_referencia,
                                nome,
                                status,
                                telefone,
                                cpf,
                                banco,
                                produto,
                                valor,
                                pontos,
                                bloqueado,
                                promotora,
                                saldo_pmt,
                                acerto,
                                motivo,
                                "",
                                criado,
                                criado,
                            ),
                        )

                        proposta_id = cursor.lastrowid
                        cursor.execute(
                            """
                            INSERT INTO historico_status
                            (proposta_id, status_anterior, status_novo, data_hora, observacao)
                            VALUES (?, ?, ?, ?, ?)
                            """,
                            (proposta_id, "", status, agora(), f"Importado do Excel - aba {aba}"),
                        )

                        importados += 1

                conn.commit()

            messagebox.showinfo(
                "Importação concluída",
                "Abas importadas: "
                + (", ".join(abas_importadas) if abas_importadas else "nenhuma")
                + f"\n\nImportados: {importados}\nDuplicados ignorados: {duplicados}\nLinhas ignoradas: {ignorados}"
            )
            self.carregar_tabela()

        except Exception as e:
            messagebox.showerror("Erro ao importar", f"Não foi possível importar a planilha:\n{e}")

    def exportar_excel(self):
        if not self.dados_atual_tabela:
            messagebox.showwarning("Atenção", "Não há dados para exportar.")
            return

        nome_padrao = f"producao_exportada_{datetime.now().strftime('%Y_%m_%d')}.xlsx"
        caminho = filedialog.asksaveasfilename(
            title="Salvar exportação",
            defaultextension=".xlsx",
            initialfile=nome_padrao,
            filetypes=[("Arquivos Excel", "*.xlsx")]
        )

        if not caminho:
            return

        try:
            dados = []
            for row in self.dados_atual_tabela:
                (
                    id_,
                    data_proposta,
                    mes_referencia,
                    nome,
                    status,
                    telefone,
                    cpf,
                    banco,
                    produto,
                    valor,
                    pontos,
                    bloqueado,
                    promotora,
                    saldo_pmt,
                    acerto,
                    motivo,
                    observacoes,
                    criado_em,
                    alterado_em,
                ) = row

                dados.append(
                    {
                        "ID": id_,
                        "DIA": data_br(data_proposta),
                        "MÊS": mes_referencia or mes_referencia_por_data(data_proposta),
                        "NOME": nome,
                        "STATUS": status,
                        "TELEFONE": telefone,
                        "CPF": cpf,
                        "BANCO": banco,
                        "PRODUTO": produto,
                        "VALOR": formatar_moeda(valor),
                        "PONTOS": formatar_moeda(pontos),
                        "BLOQUEADO": bloqueado,
                        "PROMOTORA": promotora,
                        "SALDO PMT": saldo_pmt,
                        "ACERTO": acerto,
                        "MOTIVO": motivo,
                        "OBSERVAÇÕES": observacoes,
                        "CRIADO EM": criado_em,
                        "ALTERADO EM": alterado_em,
                    }
                )

            df = pd.DataFrame(dados)
            df.to_excel(caminho, index=False)

            messagebox.showinfo("Sucesso", f"Exportação salva em:\n{caminho}")

        except Exception as e:
            messagebox.showerror("Erro ao exportar", f"Não foi possível exportar:\n{e}")

    # -----------------------------------------------------------------
    # Backup e histórico
    # -----------------------------------------------------------------
    def gerar_backup(self):
        if not os.path.exists(DB_FILE):
            messagebox.showwarning("Atenção", "Banco de dados ainda não existe.")
            return

        pasta = filedialog.askdirectory(title="Selecione a pasta para salvar o backup")
        if not pasta:
            return

        nome_backup = f"backup_producao_{datetime.now().strftime('%Y_%m_%d_%H_%M')}.db"
        destino = os.path.join(pasta, nome_backup)

        try:
            shutil.copy2(DB_FILE, destino)
            messagebox.showinfo("Backup concluído", f"Backup salvo em:\n{destino}")
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível gerar backup:\n{e}")

    def ver_historico(self):
        if not self.proposta_selecionada_id:
            messagebox.showwarning("Atenção", "Selecione uma proposta.")
            return

        with conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT nome FROM propostas WHERE id = ?", (self.proposta_selecionada_id,))
            proposta = cursor.fetchone()

            cursor.execute(
                """
                SELECT status_anterior, status_novo, data_hora, observacao
                FROM historico_status
                WHERE proposta_id = ?
                ORDER BY data_hora DESC, id DESC
                """,
                (self.proposta_selecionada_id,),
            )
            rows = cursor.fetchall()

        nome = proposta[0] if proposta else ""

        janela = ctk.CTkToplevel(self)
        janela.title("Histórico de status")
        janela.geometry("720x450")
        janela.grab_set()

        ctk.CTkLabel(janela, text=f"Histórico - {nome}", font=ctk.CTkFont(size=18, weight="bold")).pack(
            padx=15, pady=(15, 5), anchor="w"
        )

        texto = ctk.CTkTextbox(janela, width=680, height=360)
        texto.pack(padx=15, pady=10, fill="both", expand=True)

        if rows:
            linhas = []
            for anterior, novo, data_hora, obs in rows:
                linhas.append(
                    f"{data_hora}\n"
                    f"  De: {anterior or '-'}\n"
                    f"  Para: {novo}\n"
                    f"  Observação: {obs or '-'}\n"
                )
            texto.insert("1.0", "\n".join(linhas))
        else:
            texto.insert("1.0", "Nenhum histórico encontrado.")

        texto.configure(state="disabled")

    # -----------------------------------------------------------------
    # Copiar dados
    # -----------------------------------------------------------------
    def copiar_para_area_transferencia(self, texto, mensagem):
        self.clipboard_clear()
        self.clipboard_append(texto)
        self.update()
        messagebox.showinfo("Copiado", mensagem)

    def copiar_telefone(self):
        telefone = self.campos["telefone"].get().strip()
        if not telefone:
            messagebox.showwarning("Atenção", "Não há telefone para copiar.")
            return
        self.copiar_para_area_transferencia(telefone, "Telefone copiado.")

    def copiar_cpf(self):
        cpf = self.campos["cpf"].get().strip()
        if not cpf:
            messagebox.showwarning("Atenção", "Não há CPF para copiar.")
            return
        self.copiar_para_area_transferencia(cpf, "CPF copiado.")

    def copiar_resumo_proposta(self):
        try:
            dados = self.pegar_dados_formulario()
        except Exception:
            dados = {}

        if not dados.get("nome"):
            messagebox.showwarning("Atenção", "Não há proposta carregada para copiar.")
            return

        resumo = (
            f"Cliente: {dados['nome']}\n"
            f"CPF: {dados['cpf']}\n"
            f"Telefone: {dados['telefone']}\n"
            f"Banco: {dados['banco']}\n"
            f"Produto: {dados['produto']}\n"
            f"Status: {dados['status']}\n"
            f"Valor: {formatar_moeda(dados['valor'])}\n"
            f"Pontos: {formatar_moeda(dados['pontos'])}\n"
            f"Bloqueado: {dados['bloqueado']}\n"
            f"Promotora: {dados['promotora']}\n"
            f"Motivo: {dados['motivo']}"
        )

        self.copiar_para_area_transferencia(resumo, "Resumo da proposta copiado.")


if __name__ == "__main__":
    app = ControleProducaoApp()
    app.mainloop()
