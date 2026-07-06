from __future__ import annotations

from datetime import date, datetime
import json
from typing import Any

from nicegui import app, events, ui

from database import (
    Proposta,
    atualizar_proposta,
    buscar_proposta,
    carregar_kanban,
    conectar,
    criar_proposta,
    excluir_proposta,
    listar_etapas,
    mover_proposta,
)

from simulacoes import (
    br_money as sim_br_money,
    br_pct as sim_br_pct,
    calc as calc_simulacao,
    convert_to_proposal,
    delete_simulacao,
    get_simulacao,
    list_simulacoes,
    save_simulacao,
    sim_message,
)


def moeda(valor: float) -> str:
    texto = f"{valor:,.2f}"
    return f"R$ {texto.replace(',', 'X').replace('.', ',').replace('X', '.')}"


def data_br(valor: str) -> str:
    if not valor:
        return "Sem data"
    try:
        return datetime.strptime(valor[:10], "%Y-%m-%d").strftime("%d/%m/%Y")
    except ValueError:
        return valor


def data_hora_br(valor: str) -> str:
    if not valor:
        return "Não informado"
    try:
        return datetime.fromisoformat(valor).strftime("%d/%m/%Y às %H:%M")
    except ValueError:
        return valor


def criar_linha(rotulo: str, valor: str, *, classe: str = "card-field") -> None:
    with ui.row().classes(f"{classe} items-start no-wrap"):
        ui.label(rotulo).classes("card-label")
        ui.label(valor).classes("card-value")


@ui.page("/")
def pagina_inicial() -> None:
    filtro = {"texto": ""}
    menu_lateral("home")

    def notificar_erro(error: Exception) -> None:
        ui.notify(str(error), type="negative", position="top")

    def abrir_formulario(proposta: Proposta | None = None) -> None:
        etapas = [etapa.nome for etapa in listar_etapas()]
        editando = proposta is not None
        dialog = ui.dialog().props("persistent")

        with dialog, ui.card().classes("form-dialog"):
            with ui.row().classes("dialog-title-row items-center justify-between no-wrap"):
                ui.label("Editar proposta" if editando else "Nova proposta").classes("dialog-title")
                ui.button(icon="close", on_click=dialog.close).props(
                    "flat round dense aria-label=Fechar"
                )

            ui.label(
                "Preencha os dados principais usados no Kanban."
            ).classes("dialog-subtitle")

            nome = ui.input(
                "Nome *",
                value=proposta.nome if proposta else "",
            ).props("outlined dense autofocus data-testid=field-name").classes("full-width")

            cpf = ui.input(
                "CPF",
                value=proposta.cpf if proposta else "",
            ).props("outlined dense data-testid=field-cpf").classes("full-width")

            with ui.row().classes("form-grid"):
                valor = ui.number(
                    "Valor",
                    value=proposta.valor if proposta else 0,
                    min=0,
                    step=0.01,
                ).props("outlined dense data-testid=field-value")
                comissao = ui.number(
                    "Comissão",
                    value=proposta.comissao if proposta else 0,
                    min=0,
                    step=0.01,
                ).props("outlined dense data-testid=field-commission")

            with ui.row().classes("form-grid"):
                previsao = ui.input(
                    "Previsão de saldo",
                    value=proposta.previsao_saldo if proposta else "",
                ).props("outlined dense type=date data-testid=field-date")
                status = ui.select(
                    etapas,
                    label="Etapa *",
                    value=proposta.status if proposta else etapas[0],
                ).props("outlined dense options-dense data-testid=field-status")

            def salvar() -> None:
                dados: dict[str, Any] = {
                    "nome": nome.value,
                    "cpf": cpf.value,
                    "valor": valor.value,
                    "comissao": comissao.value,
                    "previsao_saldo": previsao.value,
                    "status": status.value,
                }
                try:
                    if proposta:
                        atualizar_proposta(proposta.id, dados)
                        mensagem = "Proposta atualizada."
                    else:
                        criar_proposta(dados)
                        mensagem = "Proposta criada."
                except (ValueError, OSError) as error:
                    notificar_erro(error)
                    return

                dialog.close()
                conteudo.refresh()
                ui.notify(mensagem, type="positive", position="top")

            with ui.row().classes("dialog-actions justify-end"):
                ui.button("Cancelar", on_click=dialog.close).props("flat")
                ui.button(
                    "Salvar proposta",
                    icon="save",
                    on_click=salvar,
                ).props("unelevated data-testid=save-proposal").classes("primary-button")

        dialog.open()

    def confirmar_exclusao(proposta: Proposta, detalhe_dialog: Any) -> None:
        confirmacao = ui.dialog()
        with confirmacao, ui.card().classes("confirm-dialog"):
            ui.label("Excluir proposta?").classes("dialog-title")
            ui.label(
                f'A proposta de "{proposta.nome}" será removida apenas do banco copiado do NiceGUI.'
            ).classes("dialog-subtitle")

            def excluir() -> None:
                try:
                    removida = excluir_proposta(proposta.id)
                except OSError as error:
                    notificar_erro(error)
                    return

                confirmacao.close()
                detalhe_dialog.close()
                conteudo.refresh()
                ui.notify(
                    "Proposta excluída." if removida else "A proposta já não existia.",
                    type="positive" if removida else "warning",
                    position="top",
                )

            with ui.row().classes("dialog-actions justify-end"):
                ui.button("Cancelar", on_click=confirmacao.close).props("flat")
                ui.button(
                    "Excluir definitivamente",
                    icon="delete",
                    on_click=excluir,
                ).props("unelevated color=negative data-testid=confirm-delete")
        confirmacao.open()

    def abrir_detalhes(proposta_id: int) -> None:
        proposta = buscar_proposta(proposta_id)
        if proposta is None:
            ui.notify("A proposta não foi encontrada.", type="warning", position="top")
            conteudo.refresh()
            return

        etapas = [etapa.nome for etapa in listar_etapas()]
        dialog = ui.dialog()
        with dialog, ui.card().classes("detail-dialog"):
            with ui.row().classes("dialog-title-row items-center justify-between no-wrap"):
                with ui.column().classes("gap-0"):
                    ui.label(proposta.nome).classes("dialog-title")
                    ui.label(f"Proposta #{proposta.id}").classes("dialog-subtitle")
                ui.button(icon="close", on_click=dialog.close).props(
                    "flat round dense aria-label=Fechar"
                )

            with ui.column().classes("detail-fields"):
                criar_linha("CPF", proposta.cpf or "Não informado", classe="detail-field")
                criar_linha("Valor", moeda(proposta.valor), classe="detail-field")
                criar_linha("Comissão", moeda(proposta.comissao), classe="detail-field")
                criar_linha(
                    "Previsão de saldo",
                    data_br(proposta.previsao_saldo),
                    classe="detail-field",
                )
                criar_linha("Etapa atual", proposta.status, classe="detail-field")
                criar_linha(
                    "Última atualização",
                    data_hora_br(proposta.data_atualizacao),
                    classe="detail-field",
                )

            ui.separator()
            ui.label("Mover para outra etapa").classes("section-label")
            destino = ui.select(
                etapas,
                value=proposta.status,
            ).props("outlined dense options-dense data-testid=detail-status").classes(
                "full-width"
            )

            def salvar_etapa() -> None:
                try:
                    mudou = mover_proposta(proposta.id, str(destino.value))
                except (ValueError, OSError) as error:
                    notificar_erro(error)
                    return

                dialog.close()
                conteudo.refresh()
                ui.notify(
                    "Etapa atualizada." if mudou else "A proposta já está nessa etapa.",
                    type="positive" if mudou else "info",
                    position="top",
                )

            def editar() -> None:
                dialog.close()
                abrir_formulario(proposta)

            with ui.row().classes("detail-actions items-center justify-between"):
                ui.button(
                    "Excluir",
                    icon="delete_outline",
                    on_click=lambda: confirmar_exclusao(proposta, dialog),
                ).props("flat color=negative data-testid=delete-proposal")
                with ui.row().classes("gap-2"):
                    ui.button("Editar", icon="edit", on_click=editar).props(
                        "outline data-testid=edit-proposal"
                    )
                    ui.button(
                        "Salvar etapa",
                        icon="drive_file_move",
                        on_click=salvar_etapa,
                    ).props("unelevated data-testid=save-status").classes("primary-button")

        dialog.open()

    def tratar_movimento(evento: events.GenericEventArguments, destino: str) -> None:
        try:
            proposta_id = int(evento.args["proposal_id"])
            mudou = mover_proposta(proposta_id, destino)
        except (KeyError, TypeError, ValueError, OSError) as error:
            notificar_erro(error)
            return

        if mudou:
            conteudo.refresh()
            ui.notify(f"Proposta movida para {destino}.", type="positive", position="top")

    def criar_card(proposta: Proposta, hoje: str) -> None:
        classes = "proposal-card"
        if proposta.previsao_saldo[:10] == hoje:
            classes += " balance-today"

        card = (
            ui.card()
            .classes(classes)
            .props(f"draggable=true data-proposta-id={proposta.id}")
        )
        card.on(
            "dragstart",
            js_handler=(
                f'(event) => {{ event.dataTransfer.setData("text/plain", "{proposta.id}"); '
                'event.dataTransfer.effectAllowed = "move"; '
                'event.currentTarget.classList.add("dragging"); }'
            ),
        )
        card.on(
            "dragend",
            js_handler='(event) => event.currentTarget.classList.remove("dragging")',
        )

        with card:
            with ui.row().classes("card-title-row items-start justify-between no-wrap"):
                ui.label(proposta.nome).classes("proposal-name")
                ui.button(
                    icon="open_in_new",
                    on_click=lambda proposta_id=proposta.id: abrir_detalhes(proposta_id),
                ).props(
                    f"flat round dense aria-label=Detalhes data-testid=details-{proposta.id}"
                ).classes("detail-button")
            criar_linha("CPF", proposta.cpf or "Não informado")
            criar_linha("Valor", moeda(proposta.valor))
            criar_linha("Comissão", moeda(proposta.comissao))
            criar_linha("Previsão de saldo", data_br(proposta.previsao_saldo))

    @ui.refreshable
    def conteudo() -> None:
        try:
            etapas, propostas_por_etapa = carregar_kanban(filtro["texto"])
        except (FileNotFoundError, OSError) as error:
            with ui.column().classes("error-state"):
                ui.label("Não foi possível carregar o CRM").classes("text-h5")
                ui.label(str(error))
            return

        total_propostas = sum(len(itens) for itens in propostas_por_etapa.values())
        total_comissao = sum(
            proposta.comissao
            for itens in propostas_por_etapa.values()
            for proposta in itens
        )
        hoje = date.today().isoformat()

        with ui.row().classes("summary-bar items-center justify-between no-wrap"):
            with ui.column().classes("gap-0"):
                ui.label(
                    "Resultado da busca" if filtro["texto"] else "Visão geral"
                ).classes("summary-label")
                ui.label(f"{total_propostas} proposta(s)").classes("result-count")
            with ui.column().classes("commission-summary items-end gap-0"):
                ui.label("Total geral de comissão").classes("summary-label")
                ui.label(moeda(total_comissao)).classes("summary-value")

        if total_propostas == 0 and filtro["texto"]:
            with ui.column().classes("no-results items-center"):
                ui.icon("search_off", size="38px")
                ui.label("Nenhuma proposta encontrada.")
            return

        with ui.row().classes("kanban-board no-wrap items-start"):
            for etapa in etapas:
                propostas = propostas_por_etapa[etapa.nome]
                comissao_etapa = sum(proposta.comissao for proposta in propostas)

                with ui.column().classes("kanban-column no-wrap"):
                    with ui.column().classes("column-header gap-1"):
                        ui.label(etapa.nome).classes("column-title")
                        with ui.row().classes("column-totals items-center justify-between"):
                            ui.label(f"{len(propostas)} proposta(s)")
                            ui.label(moeda(comissao_etapa))

                    lista = ui.column().classes("card-list")
                    lista.on(
                        "dragover",
                        js_handler=(
                            '(event) => { event.preventDefault(); '
                            'event.dataTransfer.dropEffect = "move"; }'
                        ),
                    )
                    lista.on(
                        "dragenter",
                        js_handler=(
                            '(event) => { event.preventDefault(); '
                            'event.currentTarget.classList.add("drag-over"); }'
                        ),
                    )
                    lista.on(
                        "dragleave",
                        js_handler=(
                            '(event) => { if (!event.currentTarget.contains(event.relatedTarget)) '
                            'event.currentTarget.classList.remove("drag-over"); }'
                        ),
                    )
                    lista.on(
                        "drop",
                        handler=lambda evento, destino=etapa.nome: tratar_movimento(
                            evento, destino
                        ),
                        js_handler=(
                            '(event) => { event.preventDefault(); '
                            'event.currentTarget.classList.remove("drag-over"); '
                            'emit({proposal_id: event.dataTransfer.getData("text/plain")}); }'
                        ),
                    )

                    with lista:
                        for proposta in propostas:
                            criar_card(proposta, hoje)
                        if not propostas:
                            ui.label("Solte uma proposta aqui").classes("empty-column")

    def atualizar_busca(evento: events.ValueChangeEventArguments) -> None:
        filtro["texto"] = str(evento.value or "")
        conteudo.refresh()

    with ui.column().classes("page-shell"):
        with ui.row().classes("topbar items-center justify-between no-wrap"):
            with ui.column().classes("gap-0"):
                ui.label("CRM Consignado").classes("page-title")
                ui.label("Kanban local · banco independente do Flask").classes("page-subtitle")
            ui.button(
                "Nova proposta",
                icon="add",
                on_click=lambda: abrir_formulario(),
            ).props("unelevated data-testid=new-proposal").classes("primary-button")

        with ui.row().classes("toolbar items-center"):
            ui.input(
                placeholder="Buscar por nome ou CPF",
                on_change=atualizar_busca,
            ).props(
                "outlined dense clearable debounce=250 data-testid=search-input"
            ).classes("search-input").add_slot(
                "prepend", '<q-icon name="search" />'
            )
            ui.label("Arraste os cards para mudar de etapa.").classes("drag-hint")

        conteudo()


ui.add_css(
    """
    :root {
        --page-bg: #f4f6f8;
        --surface: #ffffff;
        --border: #dfe4ea;
        --text: #202a35;
        --muted: #697586;
        --accent: #2f6f66;
        --accent-hover: #255a53;
        --today: #eef7e9;
        --today-border: #9fc58d;
    }

    body {
        background: var(--page-bg);
        color: var(--text);
        font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    .q-page { min-height: 100vh; }

    .page-shell {
        width: 100%;
        min-height: 100vh;
        padding: 24px;
        gap: 14px;
    }

    .topbar, .summary-bar, .toolbar {
        width: 100%;
        border: 1px solid var(--border);
        background: var(--surface);
        box-shadow: 0 5px 20px rgba(32, 42, 53, 0.04);
    }

    .topbar {
        padding: 18px 22px;
        border-radius: 16px;
    }

    .toolbar {
        padding: 10px 14px;
        border-radius: 12px;
        gap: 16px;
    }

    .summary-bar {
        padding: 13px 18px;
        border-radius: 12px;
    }

    .page-title {
        font-size: 1.55rem;
        line-height: 1.2;
        font-weight: 750;
    }

    .page-subtitle, .dialog-subtitle, .drag-hint {
        color: var(--muted);
        font-size: 0.84rem;
    }

    .search-input { width: min(420px, 100%); }
    .drag-hint { margin-left: auto; }

    .primary-button {
        background: var(--accent) !important;
        color: white !important;
    }

    .primary-button:hover { background: var(--accent-hover) !important; }

    .summary-label, .section-label {
        color: var(--muted);
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.045em;
        text-transform: uppercase;
    }

    .summary-value {
        color: var(--accent);
        font-size: 1.35rem;
        line-height: 1.2;
        font-weight: 800;
    }

    .result-count {
        color: var(--text);
        font-size: 1.05rem;
        font-weight: 750;
    }

    .kanban-board {
        width: 100%;
        gap: 14px;
        overflow-x: auto;
        overflow-y: hidden;
        padding: 2px 2px 18px;
        scroll-snap-type: x proximity;
    }

    .kanban-column {
        flex: 0 0 292px;
        width: 292px;
        min-height: 245px;
        gap: 10px;
        padding: 12px;
        border: 1px solid var(--border);
        border-radius: 14px;
        background: #eef1f4;
        scroll-snap-align: start;
    }

    .column-header {
        width: 100%;
        padding: 3px 4px 9px;
        border-bottom: 1px solid #d6dce2;
    }

    .column-title {
        min-height: 2.5rem;
        font-size: 0.95rem;
        line-height: 1.25;
        font-weight: 750;
    }

    .column-totals {
        width: 100%;
        color: var(--muted);
        font-size: 0.75rem;
        font-weight: 650;
    }

    .card-list {
        width: 100%;
        min-height: 145px;
        gap: 10px;
        border: 1px dashed transparent;
        border-radius: 11px;
        transition: background 120ms ease, border-color 120ms ease;
    }

    .card-list.drag-over {
        border-color: #74a79e;
        background: #dfecea;
    }

    .proposal-card {
        width: 100%;
        gap: 9px;
        padding: 13px;
        border: 1px solid var(--border);
        border-radius: 12px;
        background: var(--surface);
        box-shadow: 0 2px 7px rgba(32, 42, 53, 0.05);
        cursor: grab;
        transition: opacity 120ms ease, transform 120ms ease;
    }

    .proposal-card:active { cursor: grabbing; }
    .proposal-card.dragging { opacity: 0.55; transform: rotate(1deg); }

    .proposal-card.balance-today {
        border-color: var(--today-border);
        background: var(--today);
        box-shadow: inset 3px 0 0 #79a867, 0 2px 7px rgba(32, 42, 53, 0.05);
    }

    .card-title-row { width: 100%; gap: 5px; }

    .proposal-name {
        flex: 1 1 auto;
        padding-top: 3px;
        font-size: 0.96rem;
        line-height: 1.3;
        font-weight: 750;
        overflow-wrap: anywhere;
    }

    .detail-button { color: var(--muted) !important; }

    .card-field, .detail-field {
        width: 100%;
        gap: 8px;
        font-size: 0.78rem;
        line-height: 1.3;
    }

    .detail-field {
        padding: 7px 0;
        border-bottom: 1px solid #edf0f2;
        font-size: 0.86rem;
    }

    .card-label {
        flex: 0 0 42%;
        color: var(--muted);
    }

    .card-value {
        flex: 1 1 auto;
        color: var(--text);
        font-weight: 650;
        text-align: right;
        overflow-wrap: anywhere;
    }

    .empty-column {
        width: 100%;
        padding: 32px 8px;
        color: #8993a0;
        font-size: 0.78rem;
        text-align: center;
        pointer-events: none;
    }

    .no-results {
        width: 100%;
        padding: 60px 20px;
        color: var(--muted);
    }

    .form-dialog, .detail-dialog, .confirm-dialog {
        width: min(620px, calc(100vw - 28px));
        max-width: 620px;
        padding: 22px;
        gap: 16px;
        border-radius: 16px;
    }

    .detail-dialog { max-width: 560px; }
    .confirm-dialog { max-width: 480px; }

    .dialog-title-row, .dialog-actions, .detail-actions {
        width: 100%;
    }

    .dialog-title {
        font-size: 1.2rem;
        line-height: 1.25;
        font-weight: 750;
    }

    .form-grid {
        display: grid !important;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        width: 100%;
        gap: 12px;
    }

    .form-grid > * { width: 100%; }
    .detail-fields { width: 100%; gap: 0; }

    .error-state {
        max-width: 680px;
        margin: 70px auto;
        padding: 28px;
        border: 1px solid #efc6c6;
        border-radius: 14px;
        background: #fff;
        color: #8f2f2f;
    }

    @media (max-width: 700px) {
        .page-shell { padding: 11px; gap: 10px; }
        .topbar { align-items: flex-start; padding: 15px; }
        .page-title { font-size: 1.28rem; }
        .toolbar { align-items: stretch; flex-direction: column; gap: 7px; }
        .drag-hint { margin-left: 0; }
        .summary-value { font-size: 1.12rem; }
        .kanban-column { flex-basis: 270px; width: 270px; }
        .form-grid { grid-template-columns: 1fr; }
        .detail-actions { align-items: stretch; flex-direction: column-reverse; }
    }
    """,
    shared=True,
)


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        title="CRM Consignado",
        favicon="📋",
        host="127.0.0.1",
        port=8080,
        reload=False,
        show=False,
    )
TIPOS_CLIENTE = ['INSS', 'SIAPE']
PRODUTOS = ['Portabilidade', 'Refinanciamento', 'Novo', 'Cartão', 'Saque Complementar', 'Outro']
BANCOS = [
    'Banco do Brasil', 'Caixa', 'Bradesco', 'Itaú', 'Santander', 'Banrisul',
    'Sicredi', 'Sicoob', 'BMG', 'Daycoval', 'PAN', 'Olé', 'C6', 'Inter',
    'Mercantil', 'Nubank', 'Outro',
]
MODELOS = ['INSS', 'FEDERAL SIAPE', 'GOV SP', 'Portabilidade', 'estado SP', 'estado MG', 'estado RJ', 'aeronautica', 'marinha', 'exercito']


def menu_lateral(ativo: str) -> None:
    with ui.left_drawer(value=True).props('show-if-above').classes('crm-drawer'):
        with ui.column().classes('drawer-panel'):
            ui.label('CRM Consignado').classes('drawer-title')
            ui.label('Navegação').classes('drawer-subtitle')
            itens = [
                ('home', 'Kanban', '/'),
                ('simulacoes', 'Simulações', '/simulacoes'),
            ]
            for chave, rotulo, rota in itens:
                ativo_item = chave == ativo
                ui.button(
                    rotulo,
                    icon='dashboard' if chave == 'home' else 'calculate',
                    on_click=lambda rota=rota: ui.navigate.to(rota),
                ).props('flat align=left').classes('drawer-item' + (' is-active' if ativo_item else ''))
            ui.separator()
            ui.label('Banco SQLite local').classes('drawer-footnote')


def _script_simulacao(prefixo: str) -> None:
    ui.add_body_html(f'''
    <script>
    (() => {{
      const prefix = {json.dumps(prefixo)};
      const brMoney = (value) => new Intl.NumberFormat('pt-BR', {{ style: 'currency', currency: 'BRL' }}).format(Number.isFinite(value) ? value : 0);
      const parse = (value) => {{
        const raw = String(value ?? '').trim().replace(/R\\$/g, '').replace(/%/g, '').replace(/\\s/g, '');
        if (!raw) return 0;
        const normalized = raw.includes(',') && raw.includes('.') ? raw.replace(/\\./g, '').replace(',', '.') : raw.replace(',', '.');
        const num = Number(normalized);
        return Number.isFinite(num) ? num : 0;
      }};
      const field = (name) => document.getElementById(prefix + name);
      const inputValue = (name) => {{
        const root = field(name);
        if (!root) return '';
        const input = root.querySelector('input, textarea');
        return input ? input.value : root.textContent || '';
      }};
      const setText = (name, value) => {{
        const root = field(name);
        if (root) root.textContent = value;
      }};
      const calc = () => {{
        const parcelaAtual = parse(inputValue('parcela_atual'));
        const novaParcela = parse(inputValue('nova_parcela'));
        const novoPrazo = parse(inputValue('novo_prazo'));
        const valorEstimado = parse(inputValue('valor_estimado'));
        const comissaoPercentual = parse(inputValue('comissao_percentual'));
        const economiaMensal = parcelaAtual - novaParcela;
        const economiaTotal = economiaMensal * novoPrazo;
        const comissao = valorEstimado * comissaoPercentual / 100;
        setText('economia_mensal', brMoney(economiaMensal));
        setText('economia_total', brMoney(economiaTotal));
        setText('valor_estimado_saida', brMoney(valorEstimado));
        setText('comissao_calculada', brMoney(comissao));
      }};
      ['parcela_atual', 'nova_parcela', 'novo_prazo', 'valor_estimado', 'comissao_percentual'].forEach((name) => {{
        const root = field(name);
        if (!root) return;
        const input = root.querySelector('input, textarea');
        if (input && !input.dataset.crmBound) {{
          input.dataset.crmBound = '1';
          input.addEventListener('input', calc);
          input.addEventListener('change', calc);
        }}
      }});
      calc();
    }})();
    </script>
    ''')


def _campo_select(rotulo: str, value: str, options: list[str], prefixo: str, nome: str) -> ui.select:
    componente = ui.select(options, label=rotulo, value=value or None).props('outlined dense use-input new-value-mode=add-unique')
    componente.props(f'id={prefixo}{nome}')
    return componente


def _campo_texto(rotulo: str, value: str, prefixo: str, nome: str, *, placeholder: str = '') -> ui.input:
    componente = ui.input(rotulo, value=value, placeholder=placeholder).props('outlined dense')
    componente.props(f'id={prefixo}{nome}')
    return componente


def _campo_numero(rotulo: str, value: Any, prefixo: str, nome: str, *, step: str = '1', placeholder: str = '') -> ui.input:
    componente = ui.input(rotulo, value=value, placeholder=placeholder).props('outlined dense inputmode=decimal')
    componente.props(f'id={prefixo}{nome}')
    return componente


def _simulacao_formulario(simulacao: dict[str, Any] | None = None, *, sim_id: int | None = None, titulo: str = 'Nova simulação') -> None:
    sim = simulacao or {}
    prefixo = f'sim_{sim_id or "novo"}_'
    _script_simulacao(prefixo)
    menu_lateral('simulacoes')

    campos: dict[str, Any] = {}
    with ui.column().classes('page-shell sim-page'):
        with ui.row().classes('topbar items-center justify-between no-wrap'):
            with ui.column().classes('gap-0'):
                ui.label(titulo).classes('page-title')
                ui.label('Use os modelos do simulador como apoio para pré-atendimento.').classes('page-subtitle')
            with ui.row().classes('gap-2'):
                ui.button('Voltar', icon='arrow_back', on_click=lambda: ui.navigate.to('/simulacoes')).props('flat')
                ui.button('Salvar', icon='save', on_click=lambda: salvar()).props('unelevated').classes('primary-button')

        with ui.row().classes('toolbar items-center justify-between no-wrap'):
            ui.label('Campos selecionáveis e cálculo em tempo real.').classes('drag-hint')

        with ui.card().classes('sim-section-card'):
            ui.label('Dados do cliente').classes('section-label')
            with ui.row().classes('form-grid'):
                campos['nome'] = _campo_texto('Nome do cliente *', txt(sim.get('nome')), prefixo, 'nome', placeholder='Nome completo')
                campos['cpf'] = _campo_texto('CPF', txt(sim.get('cpf')), prefixo, 'cpf', placeholder='000.000.000-00')
                campos['telefone'] = _campo_texto('Telefone', txt(sim.get('telefone')), prefixo, 'telefone', placeholder='(00) 00000-0000')
                campos['nb_matricula'] = _campo_texto('NB / Matrícula', txt(sim.get('nb_matricula')), prefixo, 'nb_matricula')
                campos['tipo_cliente'] = _campo_select('Tipo de cliente', txt(sim.get('tipo_cliente')), TIPOS_CLIENTE, prefixo, 'tipo_cliente')
                campos['modelo'] = _campo_select('Modelo base', '', MODELOS, prefixo, 'modelo')

        with ui.card().classes('sim-section-card'):
            ui.label('Dados da operação').classes('section-label')
            with ui.row().classes('form-grid'):
                campos['produto'] = _campo_select('Produto', txt(sim.get('produto')), PRODUTOS, prefixo, 'produto')
                campos['promotora'] = _campo_texto('Promotora', txt(sim.get('promotora')), prefixo, 'promotora')
                campos['banco_atual'] = _campo_select('Banco atual', txt(sim.get('banco_atual')), BANCOS, prefixo, 'banco_atual')
                campos['banco_destino'] = _campo_select('Banco destino', txt(sim.get('banco_destino')), BANCOS, prefixo, 'banco_destino')
                campos['banco_digitado'] = _campo_select('Banco digitado', txt(sim.get('banco_digitado')), BANCOS, prefixo, 'banco_digitado')
                campos['observacoes'] = ui.textarea('Observações', value=txt(sim.get('observacoes'))).props('outlined dense autogrow').classes('full-width')
                campos['observacoes'].props(f'id={prefixo}observacoes')

        with ui.card().classes('sim-section-card'):
            ui.label('Valores e cálculo').classes('section-label')
            with ui.row().classes('form-grid'):
                campos['valor_estimado'] = _campo_numero('Valor estimado', sim_br_money(sim.get('valor_estimado')), prefixo, 'valor_estimado', placeholder='R$ 0,00')
                campos['parcela_atual'] = _campo_numero('Parcela atual', sim_br_money(sim.get('parcela_atual')), prefixo, 'parcela_atual', placeholder='R$ 0,00')
                campos['nova_parcela'] = _campo_numero('Nova parcela', sim_br_money(sim.get('nova_parcela')), prefixo, 'nova_parcela', placeholder='R$ 0,00')
                campos['prazo_atual'] = _campo_numero('Prazo atual', sim.get('prazo_atual') or 0, prefixo, 'prazo_atual', placeholder='Ex.: 84')
                campos['novo_prazo'] = _campo_numero('Novo prazo', sim.get('novo_prazo') or 0, prefixo, 'novo_prazo', placeholder='Ex.: 84')
                campos['taxa_atual'] = _campo_numero('Taxa atual', sim.get('taxa_atual') or 0, prefixo, 'taxa_atual', placeholder='2,5%')
                campos['nova_taxa'] = _campo_numero('Nova taxa', sim.get('nova_taxa') or 0, prefixo, 'nova_taxa', placeholder='2,5%')
                campos['comissao_percentual'] = _campo_numero('Comissão %', sim_br_pct(sim.get('comissao_percentual')), prefixo, 'comissao_percentual', placeholder='2,5%')

        with ui.card().classes('sim-section-card'):
            ui.label('Resultado').classes('section-label')
            with ui.row().classes('sim-result-grid'):
                for rotulo, nome in [
                    ('Economia mensal', 'economia_mensal'),
                    ('Economia estimada total', 'economia_total'),
                    ('Valor estimado', 'valor_estimado_saida'),
                    ('Comissão calculada', 'comissao_calculada'),
                ]:
                    with ui.card().classes('sim-result-box'):
                        ui.label(rotulo).classes('summary-label')
                        ui.label('R$ 0,00').classes('sim-result-value').props(f'id={prefixo}{nome}')

        with ui.row().classes('dialog-actions justify-end'):
            ui.button('Cancelar', on_click=lambda: ui.navigate.to('/simulacoes')).props('flat')
            ui.button('Salvar simulação', icon='save', on_click=lambda: salvar()).props('unelevated').classes('primary-button')

    def salvar() -> None:
        dados = {k: v.value for k, v in campos.items() if hasattr(v, 'value')}
        dados['observacoes'] = campos['observacoes'].value
        try:
            sid = save_simulacao(dados, sim_id)
        except Exception as exc:
            ui.notify(str(exc), type='negative')
            return
        ui.notify('Simulação salva.', type='positive')
        ui.navigate.to(f'/simulacao/{sid}')


@ui.page('/simulacoes')
def pagina_simulacoes() -> None:
    menu_lateral('simulacoes')
    filtros = {'nome': '', 'cpf': '', 'produto': '', 'banco': '', 'convertida': ''}

    def refresh_lista() -> None:
        lista.refresh()

    @ui.refreshable
    def lista() -> None:
        sims = list_simulacoes(filtros)
        if not sims:
            with ui.column().classes('no-results items-center'):
                ui.icon('search_off', size='38px')
                ui.label('Nenhuma simulação encontrada.')
            return
        for sim in sims:
            with ui.card().classes('sim-card'):
                with ui.row().classes('items-start justify-between no-wrap'):
                    with ui.column().classes('gap-0'):
                        ui.label(sim['nome']).classes('proposal-name')
                        ui.label(f"{sim.get('produto') or 'Sem produto'} · {sim.get('cpf') or 'Sem CPF'}").classes('page-subtitle')
                    ui.label('Convertida' if sim.get('convertida_em_proposta') else 'Pendente').classes('summary-label')
                with ui.row().classes('sim-meta-grid'):
                    for rotulo, valor in [
                        ('Banco atual', sim.get('banco_atual') or '-'),
                        ('Banco destino', sim.get('banco_destino') or sim.get('banco_digitado') or '-'),
                        ('Valor estimado', sim_br_money(sim.get('valor_estimado'))),
                        ('Economia mensal', sim_br_money(sim.get('economia_mensal'))),
                        ('Comissão', sim_br_money(sim.get('comissao'))),
                        ('Data', data_br(sim.get('data_criacao'))),
                    ]:
                        with ui.column().classes('sim-meta-box'):
                            ui.label(rotulo).classes('summary-label')
                            ui.label(valor).classes('card-value')
                with ui.row().classes('gap-2 justify-end'):
                    ui.button('Ver', icon='visibility', on_click=lambda sid=sim['id']: ui.navigate.to(f'/simulacao/{sid}')).props('outline')
                    ui.button('Editar', icon='edit', on_click=lambda sid=sim['id']: ui.navigate.to(f'/simulacao/{sid}/editar')).props('outline')
                    if not sim.get('convertida_em_proposta'):
                        ui.button('Converter', icon='sync_alt', on_click=lambda sid=sim['id']: _converter_simulacao(sid)).props('unelevated').classes('primary-button')
                    ui.button('Excluir', icon='delete', on_click=lambda sid=sim['id']: _confirmar_exclusao_simulacao(sid)).props('flat').classes('negative-text')

    def _converter_simulacao(sim_id: int) -> None:
        try:
            proposta_id = convert_to_proposal(sim_id)
        except Exception as exc:
            ui.notify(str(exc), type='negative')
            return
        ui.notify('Simulação convertida em proposta.', type='positive')
        ui.navigate.to(f'/proposta/{proposta_id}')

    def _confirmar_exclusao_simulacao(sim_id: int) -> None:
        sim = get_simulacao(sim_id)
        dialog = ui.dialog()
        with dialog, ui.card().classes('confirm-dialog'):
            ui.label('Excluir simulação?').classes('dialog-title')
            ui.label(f'A simulação de "{sim.get("nome") if sim else ""}" será removida.').classes('dialog-subtitle')
            with ui.row().classes('dialog-actions justify-end'):
                ui.button('Cancelar', on_click=dialog.close).props('flat')
                ui.button('Excluir definitivamente', icon='delete', on_click=lambda: _excluir()).props('unelevated color=negative')
        def _excluir() -> None:
            delete_simulacao(sim_id)
            dialog.close()
            lista.refresh()
            ui.notify('Simulação excluída.', type='positive')
        dialog.open()

    with ui.column().classes('page-shell'):
        with ui.row().classes('topbar items-center justify-between no-wrap'):
            with ui.column().classes('gap-0'):
                ui.label('Simulações').classes('page-title')
                ui.label('Pré-atendimento com cálculo automático e mensagem pronta.').classes('page-subtitle')
            with ui.row().classes('gap-2'):
                ui.button('Nova simulação', icon='add', on_click=lambda: ui.navigate.to('/simulacao/nova')).props('unelevated').classes('primary-button')
                ui.button('Kanban', icon='dashboard', on_click=lambda: ui.navigate.to('/')).props('outline')
        with ui.row().classes('toolbar items-center'):
            ui.input('Nome', on_change=lambda e: _set('nome', e.value)).props('outlined dense clearable').classes('search-input')
            ui.input('CPF', on_change=lambda e: _set('cpf', e.value)).props('outlined dense clearable').classes('search-input')
            ui.input('Produto', on_change=lambda e: _set('produto', e.value)).props('outlined dense clearable').classes('search-input')
            ui.input('Banco', on_change=lambda e: _set('banco', e.value)).props('outlined dense clearable').classes('search-input')
            ui.select(['', 'sim', 'nao'], value='', label='Convertida', on_change=lambda e: _set('convertida', e.value)).props('outlined dense').classes('search-input')
        lista()

    def _set(chave: str, valor: Any) -> None:
        filtros[chave] = str(valor or '')
        refresh_lista()


@ui.page('/simulacao/nova')
def pagina_simulacao_nova() -> None:
    _simulacao_formulario(titulo='Nova simulação')


@ui.page('/simulacao/{simulacao_id}')
def pagina_simulacao_detalhe(simulacao_id: int) -> None:
    sim = get_simulacao(simulacao_id)
    menu_lateral('simulacoes')
    if not sim:
        ui.notify('Simulação não encontrada.', type='warning')
        ui.navigate.to('/simulacoes')
        return

    mensagem = sim_message(sim)
    with ui.column().classes('page-shell'):
        with ui.row().classes('topbar items-center justify-between no-wrap'):
            with ui.column().classes('gap-0'):
                ui.label(sim['nome']).classes('page-title')
                ui.label(f"Simulação #{sim['id']} · {data_hora_br(sim.get('data_criacao'))}").classes('page-subtitle')
            with ui.row().classes('gap-2'):
                ui.button('Editar', icon='edit', on_click=lambda: ui.navigate.to(f'/simulacao/{simulacao_id}/editar')).props('outline')
                if not sim.get('convertida_em_proposta'):
                    ui.button('Converter em proposta', icon='sync_alt', on_click=lambda: _converter()).props('unelevated').classes('primary-button')
                ui.button('Voltar', icon='arrow_back', on_click=lambda: ui.navigate.to('/simulacoes')).props('flat')

        with ui.card().classes('sim-section-card'):
            ui.label('Dados da simulação').classes('section-label')
            with ui.row().classes('sim-detail-grid'):
                for rotulo, valor in [
                    ('CPF', sim.get('cpf') or '-'),
                    ('Telefone', sim.get('telefone') or '-'),
                    ('NB / Matrícula', sim.get('nb_matricula') or '-'),
                    ('Tipo de cliente', sim.get('tipo_cliente') or '-'),
                    ('Produto', sim.get('produto') or '-'),
                    ('Banco atual', sim.get('banco_atual') or '-'),
                    ('Banco destino', sim.get('banco_destino') or sim.get('banco_digitado') or '-'),
                    ('Promotora', sim.get('promotora') or '-'),
                    ('Valor estimado', sim_br_money(sim.get('valor_estimado'))),
                    ('Parcela atual', sim_br_money(sim.get('parcela_atual'))),
                    ('Nova parcela', sim_br_money(sim.get('nova_parcela'))),
                    ('Novo prazo', str(sim.get('novo_prazo') or 0)),
                    ('Economia mensal', sim_br_money(sim.get('economia_mensal'))),
                    ('Economia total', sim_br_money(sim.get('economia_total'))),
                    ('Comissão', sim_br_money(sim.get('comissao'))),
                    ('Comissão %', sim_br_pct(sim.get('comissao_percentual'))),
                ]:
                    with ui.column().classes('sim-detail-box'):
                        ui.label(rotulo).classes('summary-label')
                        ui.label(valor).classes('card-value')
        with ui.card().classes('sim-section-card'):
            ui.label('Mensagem pronta').classes('section-label')
            ui.textarea(value=mensagem).props('outlined autogrow readonly').classes('full-width')
            with ui.row().classes('justify-end'):
                ui.button('Copiar mensagem', icon='content_copy', on_click=lambda: _copiar_texto(mensagem)).props('unelevated').classes('primary-button')
        with ui.card().classes('sim-section-card'):
            ui.label('Observações').classes('section-label')
            ui.label(sim.get('observacoes') or 'Sem observações.').classes('card-value')
        if sim.get('convertida_em_proposta'):
            ui.label(f"Convertida em proposta #{sim.get('proposta_id')}").classes('summary-label')

    def _copiar_texto(texto: str) -> None:
        ui.run_javascript(f'navigator.clipboard.writeText({json.dumps(texto)})')
        ui.notify('Mensagem copiada.', type='positive')

    def _converter() -> None:
        try:
            proposta_id = convert_to_proposal(simulacao_id)
        except Exception as exc:
            ui.notify(str(exc), type='negative')
            return
        ui.notify('Simulação convertida em proposta.', type='positive')
        ui.navigate.to(f'/proposta/{proposta_id}')


@ui.page('/simulacao/{simulacao_id}/editar')
def pagina_simulacao_editar(simulacao_id: int) -> None:
    sim = get_simulacao(simulacao_id)
    if not sim:
        ui.notify('Simulação não encontrada.', type='warning')
        ui.navigate.to('/simulacoes')
        return
    _simulacao_formulario(sim, sim_id=simulacao_id, titulo='Editar simulação')


@ui.page('/proposta/{proposta_id}')
def pagina_proposta_detalhe(proposta_id: int) -> None:
    menu_lateral('home')
    with conectar() as c:
        row = c.execute('SELECT * FROM propostas WHERE id = ?', (proposta_id,)).fetchone()
    if not row:
        ui.notify('Proposta não encontrada.', type='warning')
        ui.navigate.to('/')
        return
    proposta = dict(row)
    with ui.column().classes('page-shell'):
        with ui.row().classes('topbar items-center justify-between no-wrap'):
            with ui.column().classes('gap-0'):
                ui.label(proposta.get('nome') or 'Proposta').classes('page-title')
                ui.label(f"Proposta #{proposta_id}").classes('page-subtitle')
            ui.button('Voltar ao Kanban', icon='arrow_back', on_click=lambda: ui.navigate.to('/')).props('unelevated').classes('primary-button')
        with ui.card().classes('sim-section-card'):
            ui.label('Dados da proposta').classes('section-label')
            with ui.row().classes('sim-detail-grid'):
                for rotulo, valor in [
                    ('CPF', proposta.get('cpf') or '-'),
                    ('Telefone', proposta.get('telefone') or '-'),
                    ('NB / Matrícula', proposta.get('nb_matricula') or '-'),
                    ('Tipo de cliente', proposta.get('tipo_cliente') or '-'),
                    ('Produto', proposta.get('produto') or '-'),
                    ('Banco atual', proposta.get('banco_atual') or '-'),
                    ('Banco destino', proposta.get('banco_destino') or proposta.get('banco_digitado') or '-'),
                    ('Promotora', proposta.get('promotora') or '-'),
                    ('Valor', moeda(float(proposta.get('troco') or 0))),
                    ('Comissão', moeda(float(proposta.get('comissao') or 0))),
                    ('Comissão %', sim_br_pct(proposta.get('comissao_percentual'))),
                    ('Status', proposta.get('status') or '-'),
                ]:
                    with ui.column().classes('sim-detail-box'):
                        ui.label(rotulo).classes('summary-label')
                        ui.label(valor).classes('card-value')
        with ui.card().classes('sim-section-card'):
            ui.label('Observações').classes('section-label')
            ui.label(proposta.get('observacoes') or 'Sem observações.').classes('card-value')


@app.get('/api/simular')
def api_simular(
    parcela_atual: str = '',
    nova_parcela: str = '',
    novo_prazo: str = '',
    valor_estimado: str = '',
    comissao_percentual: str = '',
) -> dict[str, Any]:
    return calc_simulacao({
        'parcela_atual': parcela_atual,
        'nova_parcela': nova_parcela,
        'novo_prazo': novo_prazo,
        'valor_estimado': valor_estimado,
        'comissao_percentual': comissao_percentual,
    })


ui.add_css(
    '''
    .crm-drawer {
        background: var(--surface);
        border-right: 1px solid var(--border);
        color: var(--text);
        width: 250px;
    }

    .drawer-panel {
        padding: 18px 14px;
        gap: 10px;
    }

    .drawer-title {
        font-size: 1.05rem;
        font-weight: 800;
    }

    .drawer-subtitle, .drawer-footnote {
        color: var(--muted);
        font-size: 0.8rem;
    }

    .drawer-item {
        justify-content: flex-start !important;
        border-radius: 12px;
        color: var(--text) !important;
    }

    .drawer-item.is-active {
        background: rgba(47, 111, 102, 0.12) !important;
        color: var(--accent) !important;
        font-weight: 700;
    }

    .sim-page { gap: 14px; }
    .sim-section-card, .sim-card {
        width: 100%;
        padding: 18px;
        gap: 14px;
        border: 1px solid var(--border);
        border-radius: 16px;
        background: var(--surface);
        box-shadow: 0 5px 20px rgba(32, 42, 53, 0.04);
    }

    .sim-result-grid, .sim-detail-grid, .sim-meta-grid {
        width: 100%;
        display: grid !important;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 12px;
    }

    .sim-result-box, .sim-meta-box, .sim-detail-box {
        gap: 6px;
        padding: 12px;
        border: 1px solid var(--border);
        border-radius: 12px;
        background: rgba(255,255,255,0.4);
    }

    .sim-result-value {
        font-size: 1.25rem;
        font-weight: 800;
        color: var(--accent);
    }

    .negative-text { color: #b3261e !important; }

    @media (max-width: 700px) {
        .sim-result-grid, .sim-detail-grid, .sim-meta-grid { grid-template-columns: 1fr; }
        .crm-drawer { width: 100%; }
    }
    ''',
    shared=True,
)
