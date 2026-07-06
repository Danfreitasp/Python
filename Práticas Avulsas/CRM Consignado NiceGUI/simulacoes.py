from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

DB = Path(__file__).with_name('database_fresh.db')


def conn(write: bool = False) -> sqlite3.Connection:
    if not DB.is_file():
        raise FileNotFoundError(f'Banco não encontrado em: {DB}')
    c = sqlite3.connect(DB, timeout=10) if write else sqlite3.connect(f'{DB.as_uri()}?mode=ro', uri=True, timeout=10)
    if write:
        c.execute('PRAGMA journal_mode = MEMORY')
        c.execute('PRAGMA synchronous = NORMAL')
    c.row_factory = sqlite3.Row
    c.execute('PRAGMA foreign_keys = ON')
    return c


def now() -> str:
    return datetime.now().isoformat(timespec='seconds')


def txt(v: Any, d: str = '') -> str:
    return d if v is None else str(v).strip()


def num(v: Any) -> float:
    if v is None or v == '':
        return 0.0
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip().replace('R$', '').replace('%', '').replace(' ', '')
    if ',' in s and '.' in s:
        s = s.replace('.', '').replace(',', '.')
    else:
        s = s.replace(',', '.')
    try:
        return float(s)
    except ValueError:
        return 0.0


def cint(v: Any) -> int:
    return int(round(num(v)))


def br_money(v: Any) -> str:
    x = num(v)
    return f"R$ {x:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')


def br_pct(v: Any) -> str:
    x = num(v)
    txtv = f'{x:.2f}'.rstrip('0').rstrip('.')
    return f'{txtv}%'


def calc(d: dict[str, Any]) -> dict[str, float]:
    parcela_atual = num(d.get('parcela_atual'))
    nova_parcela = num(d.get('nova_parcela'))
    valor_estimado = num(d.get('valor_estimado'))
    comissao_percentual = num(d.get('comissao_percentual'))
    novo_prazo = cint(d.get('novo_prazo'))
    economia_mensal = parcela_atual - nova_parcela
    economia_total = economia_mensal * novo_prazo
    comissao = valor_estimado * comissao_percentual / 100
    return {
        'parcela_atual': parcela_atual,
        'nova_parcela': nova_parcela,
        'valor_estimado': valor_estimado,
        'comissao_percentual': comissao_percentual,
        'novo_prazo': novo_prazo,
        'economia_mensal': economia_mensal,
        'economia_total': economia_total,
        'comissao': comissao,
    }


def migrate() -> None:
    if not DB.is_file():
        return
    with conn(True) as c:
        c.execute(
            '''
            CREATE TABLE IF NOT EXISTS simulacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cpf TEXT,
                telefone TEXT,
                nb_matricula TEXT,
                tipo_cliente TEXT,
                produto TEXT,
                banco_atual TEXT,
                banco_destino TEXT,
                banco_digitado TEXT,
                promotora TEXT,
                valor_estimado REAL DEFAULT 0,
                parcela_atual REAL DEFAULT 0,
                nova_parcela REAL DEFAULT 0,
                prazo_atual INTEGER DEFAULT 0,
                novo_prazo INTEGER DEFAULT 0,
                taxa_atual REAL DEFAULT 0,
                nova_taxa REAL DEFAULT 0,
                economia_mensal REAL DEFAULT 0,
                economia_total REAL DEFAULT 0,
                comissao_percentual REAL DEFAULT 0,
                comissao REAL DEFAULT 0,
                observacoes TEXT,
                data_criacao TEXT NOT NULL,
                data_atualizacao TEXT NOT NULL,
                convertida_em_proposta INTEGER NOT NULL DEFAULT 0,
                proposta_id INTEGER
            )
            '''
        )
        c.execute('CREATE INDEX IF NOT EXISTS idx_sim_nome ON simulacoes(nome COLLATE NOCASE)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_sim_cpf ON simulacoes(cpf)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_sim_conv ON simulacoes(convertida_em_proposta)')


migrate()


def row_to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    return dict(row) if row else None


def get_simulacao(sim_id: int) -> dict[str, Any] | None:
    with conn() as c:
        return row_to_dict(c.execute('SELECT * FROM simulacoes WHERE id = ?', (sim_id,)).fetchone())


def list_simulacoes(filtros: dict[str, str] | None = None) -> list[dict[str, Any]]:
    filtros = filtros or {}
    where = []
    params: list[Any] = []
    for key in ('nome', 'cpf', 'produto', 'banco'):
        value = txt(filtros.get(key))
        if value:
            if key == 'banco':
                where.append('(banco_atual LIKE ? COLLATE NOCASE OR banco_destino LIKE ? COLLATE NOCASE OR banco_digitado LIKE ? COLLATE NOCASE)')
                params.extend([f'%{value}%'] * 3)
            else:
                col = 'nome' if key == 'nome' else key
                where.append(f'{col} LIKE ? COLLATE NOCASE')
                params.append(f'%{value}%')
    conv = txt(filtros.get('convertida'))
    if conv == 'sim':
        where.append('convertida_em_proposta = 1')
    elif conv == 'nao':
        where.append('convertida_em_proposta = 0')
    sql = 'SELECT * FROM simulacoes'
    if where:
        sql += ' WHERE ' + ' AND '.join(where)
    sql += ' ORDER BY datetime(data_criacao) DESC, id DESC'
    with conn() as c:
        return [dict(r) for r in c.execute(sql, params).fetchall()]


def _upsert_cliente(d: dict[str, Any]) -> int | None:
    cpf = txt(d.get('cpf'))
    if not cpf:
        return None
    nb = txt(d.get('nb_matricula'))
    agora = now()
    with conn(True) as c:
        row = c.execute('SELECT id FROM clientes WHERE cpf = ? AND COALESCE(nb_matricula, "") = ?', (cpf, nb)).fetchone()
        if row:
            cliente_id = int(row['id'])
            c.execute(
                'UPDATE clientes SET nome = ?, telefone = ?, tipo_cliente = ?, endereco = ?, dados_bancarios = ?, data_atualizacao = ? WHERE id = ?',
                (txt(d.get('nome')) or cpf, txt(d.get('telefone')), txt(d.get('tipo_cliente')), txt(d.get('endereco')), txt(d.get('dados_bancarios')), agora, cliente_id),
            )
            return cliente_id
        cur = c.execute(
            'INSERT INTO clientes (nome, cpf, nb_matricula, telefone, tipo_cliente, endereco, dados_bancarios, data_criacao, data_atualizacao) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (txt(d.get('nome')) or cpf, cpf, nb, txt(d.get('telefone')), txt(d.get('tipo_cliente')), txt(d.get('endereco')), txt(d.get('dados_bancarios')), agora, agora),
        )
        return int(cur.lastrowid)


def save_simulacao(dados: dict[str, Any], sim_id: int | None = None) -> int:
    base = get_simulacao(sim_id) if sim_id else {}
    merged = {**(base or {}), **{k: v for k, v in dados.items() if v is not None}}
    cvals = calc(merged)
    nome = txt(merged.get('nome'))
    if not nome:
        raise ValueError('Informe o nome do cliente.')
    agora = now()
    payload = (
        nome,
        txt(merged.get('cpf')),
        txt(merged.get('telefone')),
        txt(merged.get('nb_matricula')),
        txt(merged.get('tipo_cliente')),
        txt(merged.get('produto')),
        txt(merged.get('banco_atual')),
        txt(merged.get('banco_destino')),
        txt(merged.get('banco_digitado')),
        txt(merged.get('promotora')),
        cvals['valor_estimado'],
        cvals['parcela_atual'],
        cvals['nova_parcela'],
        cint(merged.get('prazo_atual')),
        cvals['novo_prazo'],
        num(merged.get('taxa_atual')),
        num(merged.get('nova_taxa')),
        cvals['economia_mensal'],
        cvals['economia_total'],
        cvals['comissao_percentual'],
        cvals['comissao'],
        txt(merged.get('observacoes')),
        agora,
        agora,
        int(bool(merged.get('convertida_em_proposta'))),
        merged.get('proposta_id'),
    )
    with conn(True) as c:
        if sim_id:
            c.execute(
                '''
                UPDATE simulacoes SET
                    nome=?, cpf=?, telefone=?, nb_matricula=?, tipo_cliente=?, produto=?,
                    banco_atual=?, banco_destino=?, banco_digitado=?, promotora=?, valor_estimado=?,
                    parcela_atual=?, nova_parcela=?, prazo_atual=?, novo_prazo=?, taxa_atual=?, nova_taxa=?,
                    economia_mensal=?, economia_total=?, comissao_percentual=?, comissao=?, observacoes=?,
                    data_atualizacao=?, convertida_em_proposta=?, proposta_id=?
                WHERE id=?
                ''',
                (*payload[:22], *payload[23:], sim_id),
            )
            return sim_id
        cur = c.execute(
            '''
            INSERT INTO simulacoes (
                nome, cpf, telefone, nb_matricula, tipo_cliente, produto, banco_atual,
                banco_destino, banco_digitado, promotora, valor_estimado, parcela_atual,
                nova_parcela, prazo_atual, novo_prazo, taxa_atual, nova_taxa,
                economia_mensal, economia_total, comissao_percentual, comissao, observacoes,
                data_criacao, data_atualizacao, convertida_em_proposta, proposta_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            payload,
        )
        return int(cur.lastrowid)


def delete_simulacao(sim_id: int) -> bool:
    with conn(True) as c:
        cur = c.execute('DELETE FROM simulacoes WHERE id = ?', (sim_id,))
    return cur.rowcount > 0


def sim_message(sim: dict[str, Any]) -> str:
    return (
        f"Olá, {txt(sim.get('nome'))}. Fiz uma simulação para sua proposta de {txt(sim.get('produto'))}.\n\n"
        f"Parcela atual: {br_money(sim.get('parcela_atual'))}\n"
        f"Nova parcela: {br_money(sim.get('nova_parcela'))}\n"
        f"Economia mensal estimada: {br_money(sim.get('economia_mensal'))}\n"
        f"Valor estimado: {br_money(sim.get('valor_estimado'))}\n\n"
        f"Se desejar, posso seguir com a análise para confirmar as condições."
    )


def convert_to_proposal(sim_id: int) -> int:
    sim = get_simulacao(sim_id)
    if not sim:
        raise ValueError('Simulação não encontrada.')
    if sim.get('convertida_em_proposta') and sim.get('proposta_id'):
        return int(sim['proposta_id'])
    cliente_id = _upsert_cliente(sim)
    agora = now()
    with conn(True) as c:
        cur = c.execute(
            '''
            INSERT INTO propostas (
                nome, cpf, nb_matricula, tipo_cliente, banco_atual, banco_destino,
                banco_digitado, produto, promotora, parcela_atual, nova_parcela, troco,
                comissao, comissao_percentual, telefone, observacoes, status, data_criacao,
                data_atualizacao, cliente_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                txt(sim.get('nome')),
                txt(sim.get('cpf')),
                txt(sim.get('nb_matricula')),
                txt(sim.get('tipo_cliente')),
                txt(sim.get('banco_atual')),
                txt(sim.get('banco_destino')),
                txt(sim.get('banco_digitado')),
                txt(sim.get('produto')),
                txt(sim.get('promotora')),
                num(sim.get('parcela_atual')),
                num(sim.get('nova_parcela')),
                num(sim.get('valor_estimado')),
                num(sim.get('comissao')),
                num(sim.get('comissao_percentual')),
                txt(sim.get('telefone')),
                txt(sim.get('observacoes')),
                'Em atendimento',
                agora,
                agora,
                cliente_id,
            ),
        )
        proposta_id = int(cur.lastrowid)
        c.execute('INSERT INTO historico (proposta_id, data_hora, status_anterior, status_novo, observacao) VALUES (?, ?, ?, ?, ?)', (proposta_id, agora, None, 'Em atendimento', f'Proposta criada a partir da simulação #{sim_id}'))
        c.execute('INSERT INTO anotacoes (proposta_id, data_hora, texto) VALUES (?, ?, ?)', (proposta_id, agora, f'Proposta criada a partir da simulação #{sim_id}.'))
        c.execute('UPDATE simulacoes SET convertida_em_proposta = 1, proposta_id = ?, data_atualizacao = ? WHERE id = ?', (proposta_id, agora, sim_id))
    return proposta_id
