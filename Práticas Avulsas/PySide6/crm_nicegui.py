from nicegui import ui
from datetime import date


propostas = [
    {
        "nome": "Maria Silva",
        "cpf": "123.456.789-00",
        "telefone": "(27) 99999-0001",
        "valor": 4500.00,
        "comissao": 315.00,
        "previsao_saldo": "2026-06-22",
        "etapa": "Inserção",
    },
    {
        "nome": "João Pereira",
        "cpf": "987.654.321-00",
        "telefone": "(27) 99999-0002",
        "valor": 8200.00,
        "comissao": 574.00,
        "previsao_saldo": "2026-06-22",
        "etapa": "Em análise",
    },
    {
        "nome": "Ana Costa",
        "cpf": "111.222.333-44",
        "telefone": "(27) 99999-0003",
        "valor": 12000.00,
        "comissao": 840.00,
        "previsao_saldo": "2026-06-25",
        "etapa": "Aguardando CIP",
    },
]

etapas = [
    "Inserção",
    "Aguardando interação",
    "Em análise",
    "Aguardando CIP",
    "Aguardando averbação",
    "Pago",
    "Cancelado",
]


def moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def total_comissao():
    return sum(p["comissao"] for p in propostas)


def contar_por_etapa(etapa):
    return len([p for p in propostas if p["etapa"] == etapa])


def somar_comissao_etapa(etapa):
    return sum(p["comissao"] for p in propostas if p["etapa"] == etapa)


def card_proposta(proposta):
    hoje = date.today().isoformat()
    saldo_hoje = proposta["previsao_saldo"] == hoje

    classes_card = "w-full p-3 rounded-xl shadow-sm border bg-white"
    if saldo_hoje:
        classes_card += " border-orange-400 bg-orange-50"
    else:
        classes_card += " border-gray-200"

    with ui.card().classes(classes_card):
        with ui.row().classes("w-full items-center justify-between"):
            ui.label(proposta["nome"]).classes("font-bold text-gray-800")
            if saldo_hoje:
                ui.badge("Saldo hoje", color="orange")

        ui.label(f"CPF: {proposta['cpf']}").classes("text-xs text-gray-500")
        ui.label(f"Tel: {proposta['telefone']}").classes("text-xs text-gray-500")

        ui.separator()

        with ui.row().classes("w-full justify-between"):
            ui.label("Valor").classes("text-xs text-gray-500")
            ui.label(moeda(proposta["valor"])).classes("text-sm font-medium")

        with ui.row().classes("w-full justify-between"):
            ui.label("Comissão").classes("text-xs text-gray-500")
            ui.label(moeda(proposta["comissao"])).classes("text-sm font-medium text-green-700")

        with ui.row().classes("w-full justify-between"):
            ui.label("Previsão saldo").classes("text-xs text-gray-500")
            ui.label(proposta["previsao_saldo"]).classes("text-sm")

        with ui.row().classes("w-full gap-2 mt-2"):
            ui.button("Abrir", on_click=lambda: abrir_proposta(proposta)).props("flat dense")
            ui.button("Copiar CPF", on_click=lambda: ui.clipboard.write(proposta["cpf"])).props("flat dense")


def abrir_proposta(proposta):
    with ui.dialog() as dialog, ui.card().classes("w-[520px] p-4"):
        ui.label(proposta["nome"]).classes("text-xl font-bold")
        ui.label(f"CPF: {proposta['cpf']}")
        ui.label(f"Telefone: {proposta['telefone']}")
        ui.label(f"Valor: {moeda(proposta['valor'])}")
        ui.label(f"Comissão: {moeda(proposta['comissao'])}")
        ui.label(f"Previsão de saldo: {proposta['previsao_saldo']}")

        ui.separator()

        ui.textarea("Observações").classes("w-full")

        with ui.row().classes("w-full justify-end"):
            ui.button("Fechar", on_click=dialog.close)
            ui.button("Salvar", color="positive", on_click=lambda: ui.notify("Alterações salvas"))

    dialog.open()


def criar_dashboard():
    ui.dark_mode(False)

    with ui.header().classes("bg-blue-900 text-white"):
        ui.label("Confia CRM").classes("text-xl font-bold")
        ui.space()
        ui.input(placeholder="Pesquisar cliente, CPF ou telefone").props("outlined dense").classes("w-80 bg-white rounded-lg")
        ui.button("Nova proposta", color="orange", on_click=lambda: ui.notify("Abrir cadastro de proposta"))

    with ui.column().classes("w-full p-4 gap-4 bg-gray-100 min-h-screen"):
        with ui.row().classes("w-full gap-4"):
            with ui.card().classes("p-4 flex-1"):
                ui.label("Total de comissão").classes("text-gray-500")
                ui.label(moeda(total_comissao())).classes("text-2xl font-bold text-green-700")

            with ui.card().classes("p-4 flex-1"):
                ui.label("Propostas ativas").classes("text-gray-500")
                ui.label(str(len(propostas))).classes("text-2xl font-bold")

            with ui.card().classes("p-4 flex-1"):
                ui.label("Saldo do dia").classes("text-gray-500")
                qtd_saldo_hoje = len([p for p in propostas if p["previsao_saldo"] == date.today().isoformat()])
                ui.label(str(qtd_saldo_hoje)).classes("text-2xl font-bold text-orange-600")

        with ui.row().classes("w-full gap-3 items-start no-wrap overflow-x-auto"):
            for etapa in etapas:
                with ui.column().classes("min-w-[280px] max-w-[280px] gap-2"):
                    with ui.card().classes("w-full p-3 bg-blue-50 border border-blue-100"):
                        ui.label(etapa).classes("font-bold text-blue-900")
                        ui.label(
                            f"{contar_por_etapa(etapa)} propostas • {moeda(somar_comissao_etapa(etapa))}"
                        ).classes("text-xs text-gray-600")

                    propostas_etapa = [p for p in propostas if p["etapa"] == etapa]

                    with ui.column().classes("w-full gap-2"):
                        for proposta in propostas_etapa:
                            card_proposta(proposta)


criar_dashboard()
ui.run(title="Confia CRM", port=8080, reload=False)