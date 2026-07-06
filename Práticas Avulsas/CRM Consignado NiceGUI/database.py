from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


DATABASE_PATH = Path(__file__).with_name("database.db")


@dataclass(frozen=True, slots=True)
class Etapa:
    nome: str
    ordem: int


@dataclass(frozen=True, slots=True)
class Proposta:
    id: int
    nome: str
    cpf: str
    valor: float
    comissao: float
    previsao_saldo: str
    status: str
    data_criacao: str
    data_atualizacao: str


def conectar(*, somente_leitura: bool = True) -> sqlite3.Connection:
    """Abre sempre a cópia de database.db desta pasta."""
    if not DATABASE_PATH.is_file():
        raise FileNotFoundError(f"Banco copiado não encontrado em: {DATABASE_PATH}")

    if somente_leitura:
        connection = sqlite3.connect(
            f"{DATABASE_PATH.as_uri()}?mode=ro",
            uri=True,
            timeout=10,
        )
    else:
        connection = sqlite3.connect(DATABASE_PATH, timeout=10)

    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def agora_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def listar_etapas() -> list[Etapa]:
    with conectar() as connection:
        rows = connection.execute(
            """
            SELECT nome, ordem
            FROM status_etapas
            WHERE ativo = 1
            ORDER BY ordem ASC, id ASC
            """
        ).fetchall()
    return [Etapa(nome=row["nome"], ordem=row["ordem"]) for row in rows]


def nomes_etapas() -> list[str]:
    return [etapa.nome for etapa in listar_etapas()]


def _row_para_proposta(row: sqlite3.Row) -> Proposta:
    return Proposta(
        id=int(row["id"]),
        nome=row["nome"],
        cpf=row["cpf"] or "",
        valor=float(row["valor"] or 0),
        comissao=float(row["comissao"] or 0),
        previsao_saldo=row["previsao_saldo"] or "",
        status=row["status"],
        data_criacao=row["data_criacao"] or "",
        data_atualizacao=row["data_atualizacao"] or "",
    )


def listar_propostas(busca: str = "") -> list[Proposta]:
    termo = busca.strip()
    filtro = ""
    parametros: tuple[Any, ...] = ()
    if termo:
        filtro = "WHERE nome LIKE ? COLLATE NOCASE OR cpf LIKE ?"
        curinga = f"%{termo}%"
        parametros = (curinga, curinga)

    with conectar() as connection:
        rows = connection.execute(
            f"""
            SELECT
                id,
                nome,
                COALESCE(cpf, '') AS cpf,
                COALESCE(troco, 0) AS valor,
                COALESCE(comissao, 0) AS comissao,
                COALESCE(data_retorno, '') AS previsao_saldo,
                status,
                data_criacao,
                data_atualizacao
            FROM propostas
            {filtro}
            ORDER BY nome COLLATE NOCASE ASC, id ASC
            """,
            parametros,
        ).fetchall()
    return [_row_para_proposta(row) for row in rows]


def buscar_proposta(proposta_id: int) -> Proposta | None:
    with conectar() as connection:
        row = connection.execute(
            """
            SELECT
                id,
                nome,
                COALESCE(cpf, '') AS cpf,
                COALESCE(troco, 0) AS valor,
                COALESCE(comissao, 0) AS comissao,
                COALESCE(data_retorno, '') AS previsao_saldo,
                status,
                data_criacao,
                data_atualizacao
            FROM propostas
            WHERE id = ?
            """,
            (proposta_id,),
        ).fetchone()
    return _row_para_proposta(row) if row else None


def carregar_kanban(busca: str = "") -> tuple[list[Etapa], dict[str, list[Proposta]]]:
    etapas = listar_etapas()
    propostas_por_etapa = {etapa.nome: [] for etapa in etapas}
    for proposta in listar_propostas(busca):
        if proposta.status in propostas_por_etapa:
            propostas_por_etapa[proposta.status].append(proposta)
    return etapas, propostas_por_etapa


def _validar_dados(dados: dict[str, Any]) -> dict[str, Any]:
    nome = str(dados.get("nome") or "").strip()
    status = str(dados.get("status") or "").strip()
    if not nome:
        raise ValueError("Informe o nome da proposta.")
    if status not in nomes_etapas():
        raise ValueError("Selecione uma etapa ativa.")

    return {
        "nome": nome,
        "cpf": str(dados.get("cpf") or "").strip(),
        "troco": max(0.0, float(dados.get("valor") or 0)),
        "comissao": max(0.0, float(dados.get("comissao") or 0)),
        "data_retorno": str(dados.get("previsao_saldo") or "").strip(),
        "status": status,
    }


def criar_proposta(dados: dict[str, Any]) -> int:
    valores = _validar_dados(dados)
    agora = agora_iso()
    with conectar(somente_leitura=False) as connection:
        cursor = connection.execute(
            """
            INSERT INTO propostas (
                nome, cpf, troco, comissao, data_retorno, status,
                data_criacao, data_atualizacao
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                valores["nome"],
                valores["cpf"],
                valores["troco"],
                valores["comissao"],
                valores["data_retorno"],
                valores["status"],
                agora,
                agora,
            ),
        )
        proposta_id = int(cursor.lastrowid)
        connection.execute(
            """
            INSERT INTO historico (
                proposta_id, data_hora, status_anterior, status_novo, observacao
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (proposta_id, agora, None, valores["status"], "Proposta criada no NiceGUI"),
        )
    return proposta_id


def atualizar_proposta(proposta_id: int, dados: dict[str, Any]) -> None:
    valores = _validar_dados(dados)
    atual = buscar_proposta(proposta_id)
    if atual is None:
        raise ValueError("Proposta não encontrada.")

    agora = agora_iso()
    with conectar(somente_leitura=False) as connection:
        connection.execute(
            """
            UPDATE propostas
            SET nome = ?, cpf = ?, troco = ?, comissao = ?, data_retorno = ?,
                status = ?, data_atualizacao = ?
            WHERE id = ?
            """,
            (
                valores["nome"],
                valores["cpf"],
                valores["troco"],
                valores["comissao"],
                valores["data_retorno"],
                valores["status"],
                agora,
                proposta_id,
            ),
        )
        if atual.status != valores["status"]:
            connection.execute(
                """
                INSERT INTO historico (
                    proposta_id, data_hora, status_anterior, status_novo, observacao
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    proposta_id,
                    agora,
                    atual.status,
                    valores["status"],
                    "Etapa alterada no NiceGUI",
                ),
            )


def mover_proposta(proposta_id: int, novo_status: str) -> bool:
    if novo_status not in nomes_etapas():
        raise ValueError("A etapa de destino não está ativa.")
    atual = buscar_proposta(proposta_id)
    if atual is None:
        raise ValueError("Proposta não encontrada.")
    if atual.status == novo_status:
        return False

    agora = agora_iso()
    with conectar(somente_leitura=False) as connection:
        connection.execute(
            "UPDATE propostas SET status = ?, data_atualizacao = ? WHERE id = ?",
            (novo_status, agora, proposta_id),
        )
        connection.execute(
            """
            INSERT INTO historico (
                proposta_id, data_hora, status_anterior, status_novo, observacao
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (
                proposta_id,
                agora,
                atual.status,
                novo_status,
                "Card movido no Kanban NiceGUI",
            ),
        )
    return True


def excluir_proposta(proposta_id: int) -> bool:
    with conectar(somente_leitura=False) as connection:
        cursor = connection.execute("DELETE FROM propostas WHERE id = ?", (proposta_id,))
    return cursor.rowcount > 0
