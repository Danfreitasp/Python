import flet as ft
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


def propostas_por_etapa(etapa):
    return [p for p in propostas if p["etapa"] == etapa]


def abrir_proposta(page, proposta):
    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text(proposta["nome"], weight=ft.FontWeight.BOLD),
        content=ft.Column(
            controls=[
                ft.Text(f"CPF: {proposta['cpf']}"),
                ft.Text(f"Telefone: {proposta['telefone']}"),
                ft.Text(f"Valor: {moeda(proposta['valor'])}"),
                ft.Text(f"Comissão: {moeda(proposta['comissao'])}"),
                ft.Text(f"Previsão de saldo: {proposta['previsao_saldo']}"),
                ft.Divider(),
                ft.TextField(
                    label="Observações",
                    multiline=True,
                    min_lines=3,
                    max_lines=5,
                ),
            ],
            tight=True,
            width=420,
        ),
        actions=[
            ft.TextButton("Fechar", on_click=lambda e: fechar_dialog(page, dlg)),
            ft.FilledButton("Salvar", on_click=lambda e: page.open(
                ft.SnackBar(ft.Text("Alterações salvas."))
            )),
        ],
    )

    page.open(dlg)


def fechar_dialog(page, dlg):
    dlg.open = False
    page.update()


def copiar_cpf(page, cpf):
    page.set_clipboard(cpf)
    page.open(ft.SnackBar(ft.Text("CPF copiado.")))


def card_proposta(page, proposta):
    hoje = date.today().isoformat()
    saldo_hoje = proposta["previsao_saldo"] == hoje

    cor_borda = ft.Colors.ORANGE_400 if saldo_hoje else ft.Colors.BLUE_GREY_100
    cor_fundo = ft.Colors.ORANGE_50 if saldo_hoje else ft.Colors.WHITE

    badge_saldo = (
        ft.Container(
            content=ft.Text("Saldo hoje", size=11, color=ft.Colors.WHITE),
            bgcolor=ft.Colors.ORANGE_600,
            padding=ft.Padding.symmetric(horizontal=8, vertical=4),
            border_radius=20,
        )
        if saldo_hoje
        else ft.Container(
            content=ft.Text(proposta["previsao_saldo"], size=11, color=ft.Colors.BLUE_GREY_600),
            bgcolor=ft.Colors.BLUE_GREY_50,
            padding=ft.Padding.symmetric(horizontal=8, vertical=4),
            border_radius=20,
        )
    )

    return ft.Container(
        bgcolor=cor_fundo,
        border=ft.Border.all(1, cor_borda),
        border_radius=16,
        padding=14,
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=12,
            color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
            offset=ft.Offset(0, 3),
        ),
        content=ft.Column(
            spacing=8,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(
                            proposta["nome"],
                            weight=ft.FontWeight.BOLD,
                            size=15,
                            color=ft.Colors.BLUE_GREY_900,
                        ),
                        badge_saldo,
                    ],
                ),
                ft.Text(f"CPF: {proposta['cpf']}", size=12, color=ft.Colors.BLUE_GREY_500),
                ft.Text(f"Tel: {proposta['telefone']}", size=12, color=ft.Colors.BLUE_GREY_500),
                ft.Divider(height=12),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text("Valor", size=12, color=ft.Colors.BLUE_GREY_500),
                        ft.Text(moeda(proposta["valor"]), size=13, weight=ft.FontWeight.W_500),
                    ],
                ),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text("Comissão", size=12, color=ft.Colors.BLUE_GREY_500),
                        ft.Text(
                            moeda(proposta["comissao"]),
                            size=13,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.GREEN_700,
                        ),
                    ],
                ),
                ft.Row(
                    spacing=6,
                    controls=[
                        ft.TextButton(
                            "Abrir",
                            icon=ft.Icons.OPEN_IN_NEW,
                            on_click=lambda e: abrir_proposta(page, proposta),
                        ),
                        ft.TextButton(
                            "Copiar CPF",
                            icon=ft.Icons.CONTENT_COPY,
                            on_click=lambda e: copiar_cpf(page, proposta["cpf"]),
                        ),
                    ],
                ),
            ],
        ),
    )


def coluna_etapa(page, etapa):
    lista = propostas_por_etapa(etapa)
    total = sum(p["comissao"] for p in lista)

    return ft.Container(
        width=290,
        bgcolor=ft.Colors.BLUE_GREY_50,
        border_radius=18,
        padding=12,
        content=ft.Column(
            spacing=10,
            controls=[
                ft.Container(
                    bgcolor=ft.Colors.WHITE,
                    border_radius=14,
                    padding=12,
                    content=ft.Column(
                        spacing=2,
                        controls=[
                            ft.Text(etapa, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
                            ft.Text(
                                f"{len(lista)} propostas • {moeda(total)}",
                                size=12,
                                color=ft.Colors.BLUE_GREY_500,
                            ),
                        ],
                    ),
                ),
                ft.Column(
                    spacing=10,
                    controls=[card_proposta(page, p) for p in lista],
                ),
            ],
        ),
    )


def card_resumo(titulo, valor, cor):
    return ft.Container(
        expand=True,
        bgcolor=ft.Colors.WHITE,
        border_radius=18,
        padding=18,
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=14,
            color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
            offset=ft.Offset(0, 3),
        ),
        content=ft.Column(
            spacing=6,
            controls=[
                ft.Text(titulo, size=13, color=ft.Colors.BLUE_GREY_500),
                ft.Text(valor, size=24, weight=ft.FontWeight.BOLD, color=cor),
            ],
        ),
    )


def main(page: ft.Page):
    page.title = "Confia CRM - Flet"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = ft.Colors.BLUE_GREY_50
    page.padding = 0
    page.window_width = 1280
    page.window_height = 760

    qtd_saldo_hoje = len(
        [p for p in propostas if p["previsao_saldo"] == date.today().isoformat()]
    )

    header = ft.Container(
        bgcolor=ft.Colors.BLUE_900,
        padding=ft.Padding.symmetric(horizontal=24, vertical=16),
        content=ft.Row(
            controls=[
                ft.Text(
                    "Confia CRM",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE,
                ),
                ft.Container(expand=True),
                ft.TextField(
                    hint_text="Pesquisar cliente, CPF ou telefone",
                    width=340,
                    height=42,
                    bgcolor=ft.Colors.WHITE,
                    border_radius=12,
                    prefix_icon=ft.Icons.SEARCH,
                    border_color=ft.Colors.TRANSPARENT,
                ),
                ft.FilledButton(
                    "Nova proposta",
                    icon=ft.Icons.ADD,
                    bgcolor=ft.Colors.ORANGE_600,
                    color=ft.Colors.WHITE,
                ),
            ],
        ),
    )

    resumo = ft.Row(
        spacing=16,
        controls=[
            card_resumo("Comissão total", moeda(total_comissao()), ft.Colors.GREEN_700),
            card_resumo("Propostas ativas", str(len(propostas)), ft.Colors.BLUE_900),
            card_resumo("Saldo do dia", str(qtd_saldo_hoje), ft.Colors.ORANGE_700),
        ],
    )

    kanban = ft.Row(
        spacing=14,
        scroll=ft.ScrollMode.AUTO,
        controls=[coluna_etapa(page, etapa) for etapa in etapas],
    )

    page.add(
        ft.Column(
            expand=True,
            spacing=0,
            controls=[
                header,
                ft.Container(
                    expand=True,
                    padding=24,
                    content=ft.Column(
                        expand=True,
                        spacing=20,
                        controls=[
                            resumo,
                            kanban,
                        ],
                    ),
                ),
            ],
        )
    )


ft.app(target=main)