from __future__ import annotations

import csv
import io
import json
import os
import re
import sqlite3
from datetime import datetime, date
from pathlib import Path
from typing import Any

from flask import (
    Flask,
    flash,
    g,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from openpyxl import Workbook, load_workbook
from werkzeug.utils import secure_filename

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "database.db"
DATA_DIR = BASE_DIR / "data"
MODELOS_PATH = DATA_DIR / "modelos_mensagens.json"
BACKUP_DIR = BASE_DIR / "backups"
MAX_BACKUPS = 30
_backup_checked_date: str | None = None

# Pasta padrão dos documentos dos clientes.
# Pode ser alterada sem mexer no código criando a variável de ambiente CRM_ANEXOS_DIR.
ANEXOS_BASE_DIR = Path(
    os.environ.get(
        "CRM_ANEXOS_DIR",
        r"C:\Users\tatia\OneDrive\DOCUMENTOS FACILITA - VILA VELHA\DANIEL",
    )
)

app = Flask(__name__)
app.config["SECRET_KEY"] = "troque-esta-chave-em-producao-local"
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024

DEFAULT_STATUS_ETAPAS = [
    {"nome": "Novo lead", "grupo": "geral", "ordem": 1},
    {"nome": "Em atendimento", "grupo": "geral", "ordem": 2},
    {"nome": "Simulação enviada", "grupo": "geral", "ordem": 3},
    {"nome": "Aguardando documentos", "grupo": "geral", "ordem": 4},
    {"nome": "Aguardando desbloqueio", "grupo": "geral", "ordem": 5},
    {"nome": "Aguardando inserção", "grupo": "geral", "ordem": 6},
    {"nome": "Aguardando interação", "grupo": "geral", "ordem": 7},
    {"nome": "Atuação", "grupo": "geral", "ordem": 8},
    {"nome": "Em análise", "grupo": "geral", "ordem": 9},
    {"nome": "Aguardando CIP", "grupo": "geral", "ordem": 10},
    {"nome": "Aguardando Averbação", "grupo": "geral", "ordem": 11},
    {"nome": "Averbado", "grupo": "geral", "ordem": 12},
    {"nome": "Aguardando Pagamento", "grupo": "geral", "ordem": 13},
    {"nome": "Aguardando Reapresentação", "grupo": "geral", "ordem": 14},
    {"nome": "Pago", "grupo": "geral", "ordem": 15},
    {"nome": "Perdido / Cancelado", "grupo": "geral", "ordem": 16},
]

# Fallback usado antes da criação do banco. A partir da v4 o funil é único.
STATUS_LIST = [s["nome"] for s in DEFAULT_STATUS_ETAPAS]
STATUS_VENDEDOR = STATUS_LIST
STATUS_ADMINISTRATIVO = STATUS_LIST
STATUS_ENCERRADOS = ["Pago", "Perdido / Cancelado"]

TIPOS_CLIENTE = ["INSS", "SIAPE"]
PRODUTOS = ["Portabilidade", "Refinanciamento", "Novo", "Cartão", "Saque Complementar", "Outro"]

CAMPOS_PROPOSTA = [
    "nome",
    "cpf",
    "nb_matricula",
    "numero_proposta",
    "numero_port_vinculada",
    "numero_refin_vinculada",
    "tipo_cliente",
    "banco_atual",
    "banco_destino",
    "banco_digitado",
    "produto",
    "promotora",
    "beneficio_bloqueado",
    "valor_caiu_promotora",
    "valor_sacado",
    "data_verificacao",
    "parcela_atual",
    "nova_parcela",
    "troco",
    "comissao_percentual",
    "comissao",
    "margem_apos",
    "status",
    "responsavel",
    "telefone",
    "endereco",
    "dados_bancarios",
    "proxima_acao",
    "data_retorno",
    "observacoes",
]

COLUNAS_IMPORTACAO = CAMPOS_PROPOSTA.copy()


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(exception: Exception | None = None) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db() -> None:
    db = get_db()
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS propostas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            nome TEXT NOT NULL,
            cpf TEXT,
            nb_matricula TEXT,
            numero_proposta TEXT,
            numero_port_vinculada TEXT,
            numero_refin_vinculada TEXT,
            tipo_cliente TEXT,
            banco_atual TEXT,
            banco_destino TEXT,
            banco_digitado TEXT,
            produto TEXT,
            promotora TEXT,
            beneficio_bloqueado TEXT DEFAULT 'NÃO',
            valor_caiu_promotora TEXT DEFAULT 'NÃO',
            valor_sacado TEXT DEFAULT 'NÃO',
            data_verificacao TEXT,
            parcela_atual REAL DEFAULT 0,
            nova_parcela REAL DEFAULT 0,
            troco REAL DEFAULT 0,
            comissao_percentual REAL DEFAULT 0,
            comissao REAL DEFAULT 0,
            margem_apos TEXT,
            status TEXT NOT NULL DEFAULT 'Novo lead',
            responsavel TEXT,
            telefone TEXT,
            endereco TEXT,
            dados_bancarios TEXT,
            data_criacao TEXT NOT NULL,
            data_atualizacao TEXT NOT NULL,
            proxima_acao TEXT,
            data_retorno TEXT,
            observacoes TEXT
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS historico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            proposta_id INTEGER NOT NULL,
            data_hora TEXT NOT NULL,
            status_anterior TEXT,
            status_novo TEXT,
            observacao TEXT,
            FOREIGN KEY (proposta_id) REFERENCES propostas(id) ON DELETE CASCADE
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS anotacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            proposta_id INTEGER NOT NULL,
            data_hora TEXT NOT NULL,
            texto TEXT NOT NULL,
            FOREIGN KEY (proposta_id) REFERENCES propostas(id) ON DELETE CASCADE
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS anexos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            proposta_id INTEGER NOT NULL,
            nome_original TEXT NOT NULL,
            nome_arquivo TEXT NOT NULL,
            caminho TEXT NOT NULL,
            data_upload TEXT NOT NULL,
            FOREIGN KEY (proposta_id) REFERENCES propostas(id) ON DELETE CASCADE
        )
        """
    )

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS status_etapas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            grupo TEXT NOT NULL DEFAULT 'administrativo',
            ordem INTEGER NOT NULL DEFAULT 0,
            ativo INTEGER NOT NULL DEFAULT 1
        )
        """
    )

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS modelos_mensagens (
            nome TEXT PRIMARY KEY,
            texto TEXT NOT NULL,
            ordem INTEGER NOT NULL DEFAULT 0,
            data_atualizacao TEXT
        )
        """
    )

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cpf TEXT NOT NULL,
            nb_matricula TEXT NOT NULL DEFAULT '',
            telefone TEXT,
            tipo_cliente TEXT,
            endereco TEXT,
            dados_bancarios TEXT,
            data_criacao TEXT NOT NULL,
            data_atualizacao TEXT NOT NULL,
            UNIQUE(cpf, nb_matricula)
        )
        """
    )

    # Migrações incrementais: adiciona colunas em bancos criados nas versões anteriores.
    colunas_propostas = {row["name"] for row in db.execute("PRAGMA table_info(propostas)").fetchall()}
    if "cliente_id" not in colunas_propostas:
        db.execute("ALTER TABLE propostas ADD COLUMN cliente_id INTEGER")
    if "numero_proposta" not in colunas_propostas:
        db.execute("ALTER TABLE propostas ADD COLUMN numero_proposta TEXT")
    if "numero_port_vinculada" not in colunas_propostas:
        db.execute("ALTER TABLE propostas ADD COLUMN numero_port_vinculada TEXT")
    if "numero_refin_vinculada" not in colunas_propostas:
        db.execute("ALTER TABLE propostas ADD COLUMN numero_refin_vinculada TEXT")
    if "comissao" not in colunas_propostas:
        db.execute("ALTER TABLE propostas ADD COLUMN comissao REAL DEFAULT 0")
    if "comissao_percentual" not in colunas_propostas:
        db.execute("ALTER TABLE propostas ADD COLUMN comissao_percentual REAL DEFAULT 0")
    if "promotora" not in colunas_propostas:
        db.execute("ALTER TABLE propostas ADD COLUMN promotora TEXT")
    if "beneficio_bloqueado" not in colunas_propostas:
        db.execute("ALTER TABLE propostas ADD COLUMN beneficio_bloqueado TEXT DEFAULT 'NÃO'")
    if "banco_digitado" not in colunas_propostas:
        db.execute("ALTER TABLE propostas ADD COLUMN banco_digitado TEXT")
    if "valor_caiu_promotora" not in colunas_propostas:
        db.execute("ALTER TABLE propostas ADD COLUMN valor_caiu_promotora TEXT DEFAULT 'NÃO'")
    if "valor_sacado" not in colunas_propostas:
        db.execute("ALTER TABLE propostas ADD COLUMN valor_sacado TEXT DEFAULT 'NÃO'")
    if "data_verificacao" not in colunas_propostas:
        db.execute("ALTER TABLE propostas ADD COLUMN data_verificacao TEXT")
    if "endereco" not in colunas_propostas:
        db.execute("ALTER TABLE propostas ADD COLUMN endereco TEXT")
    if "dados_bancarios" not in colunas_propostas:
        db.execute("ALTER TABLE propostas ADD COLUMN dados_bancarios TEXT")

    qtd_status = db.execute("SELECT COUNT(*) AS total FROM status_etapas").fetchone()["total"]
    if qtd_status == 0:
        db.executemany(
            "INSERT INTO status_etapas (nome, grupo, ordem, ativo) VALUES (?, ?, ?, 1)",
            [(item["nome"], item["grupo"], item["ordem"]) for item in DEFAULT_STATUS_ETAPAS],
        )

    # Migrações automáticas para bases criadas nas versões anteriores.
    # Assim, propostas antigas continuam aparecendo no funil novo.
    migracoes_status = {
        "Aguardando digitação": "Aguardando inserção",
        "Inserção": "Aguardando interação",
        "Contrato em andamento": "Atuação",
        "Perdido": "Perdido / Cancelado",
        "Cancelado": "Perdido / Cancelado",
    }
    for antigo, novo in migracoes_status.items():
        db.execute("UPDATE propostas SET status = ? WHERE status = ?", (novo, antigo))
        db.execute("UPDATE historico SET status_anterior = ? WHERE status_anterior = ?", (novo, antigo))
        db.execute("UPDATE historico SET status_novo = ? WHERE status_novo = ?", (novo, antigo))

    for removido in ("Inserção", "Perdido", "Cancelado"):
        db.execute("DELETE FROM status_etapas WHERE nome = ?", (removido,))

    # A v4 usa um único funil compartilhado, sem separação por vendedor/administrativo.
    db.execute("UPDATE status_etapas SET grupo = 'geral'")

    # Garante que a etapa unificada exista mesmo em bancos antigos.
    existentes = {row["nome"] for row in db.execute("SELECT nome FROM status_etapas").fetchall()}
    for item in DEFAULT_STATUS_ETAPAS:
        if item["nome"] not in existentes:
            db.execute(
                "INSERT INTO status_etapas (nome, grupo, ordem, ativo) VALUES (?, ?, ?, 1)",
                (item["nome"], item["grupo"], item["ordem"]),
            )

    # v9: migra observações fixas para um diário/log de anotações.
    propostas_com_observacao = db.execute(
        """
        SELECT id, observacoes, data_criacao, data_atualizacao
        FROM propostas
        WHERE COALESCE(TRIM(observacoes), '') <> ''
        """
    ).fetchall()
    for proposta in propostas_com_observacao:
        ja_tem = db.execute(
            "SELECT id FROM anotacoes WHERE proposta_id = ? LIMIT 1",
            (proposta["id"],),
        ).fetchone()
        if not ja_tem:
            db.execute(
                "INSERT INTO anotacoes (proposta_id, data_hora, texto) VALUES (?, ?, ?)",
                (
                    proposta["id"],
                    proposta["data_atualizacao"] or proposta["data_criacao"] or agora_iso(),
                    proposta["observacoes"],
                ),
            )
    sincronizar_modelos_banco(db)
    migrar_clientes_a_partir_de_propostas()
    db.commit()


def modelos_padrao() -> dict[str, str]:
    return {
        "Mensagem inicial": "Olá, {nome}. Tudo bem? Tenho uma simulação de {produto} para seu contrato do banco {banco_atual}, com possibilidade de redução de parcela e liberação de valor. Posso te passar os detalhes?",
        "Solicitação de documentos": "Olá, {nome}. Para seguir com sua proposta de {produto}, preciso que me envie os documentos necessários para análise. Assim que receber, dou andamento por aqui.",
        "Proposta em andamento": "Olá, {nome}. Sua proposta de {produto} está em andamento no banco {banco_destino}. Status atual: {status}. Assim que houver atualização, te aviso.",
        "Aguardando interação": "Olá, {nome}. Sua proposta já foi digitada e agora precisamos que você conclua a assinatura digital com selfie. Assim que concluir, me avise para seguirmos acompanhando.",
        "Em análise": "Olá, {nome}. Sua proposta está em análise documental pelo banco {banco_destino}. Sigo acompanhando e te aviso assim que houver atualização.",
        "Aguardando CIP": "Olá, {nome}. Sua proposta está aguardando retorno da CIP. Essa etapa depende da comunicação entre os bancos, mas sigo acompanhando de perto.",
        "Aguardando averbação": "Olá, {nome}. Sua proposta está aguardando averbação. Essa é uma das etapas finais antes da liberação do pagamento.",
        "Aguardando pagamento": "Olá, {nome}. Sua proposta já avançou e está aguardando pagamento pelo banco {banco_destino}. Assim que constar pago, te aviso.",
        "Aguardando reapresentação": "Olá, {nome}. O pagamento retornou e precisamos ajustar os dados bancários para reapresentar. Pode me confirmar a conta para pagamento?",
        "Proposta paga": "Olá, {nome}. Sua proposta consta como paga. Verifique sua conta e me avise caso precise de mais alguma informação.",
        "Falta de margem": "Olá, {nome}. No momento, a análise indicou falta de margem para seguir com a proposta. Vou manter seu cadastro acompanhado para uma nova oportunidade.",
        "Recontato": "Olá, {nome}. Passando para saber se ainda tem interesse na simulação de {produto}. Posso atualizar as condições para você sem compromisso.",
    }


def garantir_modelos() -> None:
    """Mantém um arquivo de modelos como fallback/backup.

    A partir da v22, os modelos editados ficam salvos no database.db para não
    serem perdidos quando a pasta data/ for substituída em uma atualização.
    """
    DATA_DIR.mkdir(exist_ok=True)
    if MODELOS_PATH.exists():
        return
    MODELOS_PATH.write_text(json.dumps(modelos_padrao(), ensure_ascii=False, indent=2), encoding="utf-8")


def carregar_modelos_arquivo() -> dict[str, str]:
    garantir_modelos()
    try:
        dados = json.loads(MODELOS_PATH.read_text(encoding="utf-8"))
        if isinstance(dados, dict):
            return {str(k): str(v) for k, v in dados.items()}
    except Exception:
        pass
    return modelos_padrao()


def sincronizar_modelos_banco(db: sqlite3.Connection) -> None:
    """Cria/preserva modelos no banco.

    Regras:
    - Se o banco ainda não tem modelos, importa do arquivo data/modelos_mensagens.json.
    - Se o banco já tem modelos, mantém os textos editados pelo usuário.
    - Novos modelos padrão podem ser adicionados em versões futuras sem apagar os existentes.
    """
    existentes = db.execute("SELECT nome, texto FROM modelos_mensagens ORDER BY ordem, nome").fetchall()
    if not existentes:
        origem = carregar_modelos_arquivo()
        for ordem, (nome, texto) in enumerate(origem.items(), start=1):
            db.execute(
                """
                INSERT OR REPLACE INTO modelos_mensagens (nome, texto, ordem, data_atualizacao)
                VALUES (?, ?, ?, ?)
                """,
                (nome, texto, ordem, agora_iso()),
            )
        return

    nomes_existentes = {row["nome"] for row in existentes}
    maior_ordem = db.execute("SELECT COALESCE(MAX(ordem), 0) AS maior FROM modelos_mensagens").fetchone()["maior"]
    for nome, texto in modelos_padrao().items():
        if nome not in nomes_existentes:
            maior_ordem += 1
            db.execute(
                """
                INSERT INTO modelos_mensagens (nome, texto, ordem, data_atualizacao)
                VALUES (?, ?, ?, ?)
                """,
                (nome, texto, maior_ordem, agora_iso()),
            )


def criar_backup_automatico() -> None:
    """Cria um backup diário do database.db na pasta backups.

    O backup usa a API nativa do SQLite para reduzir risco de cópia inconsistente.
    Para não gerar centenas de arquivos, cria no máximo um backup por dia e mantém
    apenas os últimos MAX_BACKUPS arquivos.
    """
    global _backup_checked_date
    hoje = date.today().strftime("%Y-%m-%d")
    if _backup_checked_date == hoje:
        return
    _backup_checked_date = hoje

    if not DATABASE.exists():
        return

    try:
        BACKUP_DIR.mkdir(exist_ok=True)
        ja_existe_hoje = any(BACKUP_DIR.glob(f"database_{hoje}_*.db"))
        if ja_existe_hoje:
            return

        destino = BACKUP_DIR / f"database_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.db"
        origem_conn = sqlite3.connect(DATABASE)
        destino_conn = sqlite3.connect(destino)
        try:
            origem_conn.backup(destino_conn)
        finally:
            destino_conn.close()
            origem_conn.close()

        backups = sorted(BACKUP_DIR.glob("database_*.db"), key=lambda item: item.stat().st_mtime, reverse=True)
        for antigo in backups[MAX_BACKUPS:]:
            try:
                antigo.unlink()
            except OSError:
                pass
    except Exception as exc:
        # Não bloqueia o CRM caso o backup falhe; apenas informa no terminal.
        print(f"Aviso: não foi possível criar backup automático: {exc}")

@app.before_request
def preparar_app() -> None:
    init_db()
    garantir_modelos()
    criar_backup_automatico()


def agora_iso() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def hoje_iso() -> str:
    return date.today().strftime("%Y-%m-%d")


def limpar_texto(valor: Any) -> str:
    if valor is None:
        return ""
    return str(valor).strip()


def nome_pasta_cliente(nome: str) -> str:
    """Gera nome seguro para pasta local do cliente, preservando leitura humana."""
    base = remover_acentos(limpar_texto(nome)).upper()
    base = re.sub(r"[^A-Z0-9 _.-]", "", base)
    base = re.sub(r"\s+", " ", base).strip(" .")
    return base or "CLIENTE SEM NOME"


def pasta_cliente(proposta: sqlite3.Row | dict[str, Any]) -> Path:
    return ANEXOS_BASE_DIR / nome_pasta_cliente(proposta["nome"])


def arquivo_destino_unico(pasta: Path, nome_arquivo: str) -> Path:
    destino = pasta / nome_arquivo
    if not destino.exists():
        return destino
    stem = destino.stem
    suffix = destino.suffix
    contador = 2
    while True:
        candidato = pasta / f"{stem}_{contador}{suffix}"
        if not candidato.exists():
            return candidato
        contador += 1


def salvar_anexos_upload(proposta_id: int, proposta: sqlite3.Row | dict[str, Any], arquivos: list[Any]) -> int:
    """Salva arquivos enviados na pasta do cliente e registra no banco.

    Usado tanto na criação da proposta quanto na tela de detalhes.
    Retorna a quantidade de arquivos salvos com sucesso.
    """
    arquivos_validos = [arquivo for arquivo in arquivos if arquivo and arquivo.filename]
    if not arquivos_validos:
        return 0

    pasta = pasta_cliente(proposta)
    try:
        pasta.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        flash(f"Não foi possível criar a pasta de anexos: {exc}", "erro")
        return 0

    db = get_db()
    salvos = 0
    for arquivo in arquivos_validos:
        nome_original = arquivo.filename
        seguro = secure_filename(nome_original) or "arquivo"
        destino = arquivo_destino_unico(pasta, seguro)
        try:
            arquivo.save(destino)
        except OSError as exc:
            flash(f"Erro ao salvar {nome_original}: {exc}", "erro")
            continue
        db.execute(
            """
            INSERT INTO anexos (proposta_id, nome_original, nome_arquivo, caminho, data_upload)
            VALUES (?, ?, ?, ?, ?)
            """,
            (proposta_id, nome_original, destino.name, str(destino), agora_iso()),
        )
        salvos += 1

    db.commit()
    return salvos


def tamanho_arquivo(caminho: str) -> str:
    try:
        size = Path(caminho).stat().st_size
    except OSError:
        return ""
    unidades = ["B", "KB", "MB", "GB"]
    valor = float(size)
    for unidade in unidades:
        if valor < 1024 or unidade == unidades[-1]:
            if unidade == "B":
                return f"{int(valor)} {unidade}"
            return f"{valor:.1f} {unidade}".replace(".", ",")
        valor /= 1024


def formatar_cpf(valor: str) -> str:
    digitos = re.sub(r"\D", "", valor or "")
    if len(digitos) == 11:
        return f"{digitos[:3]}.{digitos[3:6]}.{digitos[6:9]}-{digitos[9:]}"
    return valor.strip()


def parse_moeda(valor: Any) -> float:
    if valor is None:
        return 0.0
    texto = str(valor).strip()
    if not texto:
        return 0.0
    texto = texto.replace("R$", "").replace(" ", "")
    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")
    try:
        return float(texto)
    except ValueError:
        return 0.0


def parse_percentual(valor: Any) -> float:
    if valor is None:
        return 0.0
    if isinstance(valor, (int, float)):
        return float(valor)
    texto = str(valor).strip().replace("%", "").replace(" ", "")
    if not texto:
        return 0.0
    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")
    try:
        return float(texto)
    except ValueError:
        return 0.0


def br_moeda(valor: Any) -> str:
    try:
        numero = float(valor or 0)
    except (TypeError, ValueError):
        numero = 0.0
    texto = f"R$ {numero:,.2f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def br_percentual(valor: Any) -> str:
    try:
        numero = float(valor or 0)
    except (TypeError, ValueError):
        numero = 0.0
    texto = f"{numero:.2f}".replace(".", ",")
    if texto.endswith(",00"):
        texto = texto[:-3]
    return f"{texto}%"


def br_data(valor: Any) -> str:
    texto = limpar_texto(valor)
    if not texto:
        return ""
    for formato in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(texto, formato).strftime("%d/%m/%Y")
        except ValueError:
            pass
    return texto


def br_data_hora(valor: Any) -> str:
    texto = limpar_texto(valor)
    if not texto:
        return ""
    try:
        return datetime.strptime(texto, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M")
    except ValueError:
        return texto




def remover_acentos(texto: str) -> str:
    mapa = str.maketrans("áàâãäéèêëíìîïóòôõöúùûüçÁÀÂÃÄÉÈÊËÍÌÎÏÓÒÔÕÖÚÙÛÜÇ", "aaaaaeeeeiiiiooooouuuucAAAAAEEEEIIIIOOOOOUUUUC")
    return texto.translate(mapa)


def normalizar_bloqueado(valor: Any) -> str:
    texto = remover_acentos(limpar_texto(valor)).upper()
    if not texto:
        return "NÃO"
    if texto in {"SIM", "S", "BLOQUEADO", "BLOCK", "TRUE", "1", "YES"}:
        return "SIM"
    if texto in {"NAO", "N", "DESBLOQUEADO", "LIBERADO", "FALSE", "0", "NO"}:
        return "NÃO"
    return "SIM" if "BLOQUE" in texto and "DES" not in texto else "NÃO"


def normalizar_sim_nao(valor: Any) -> str:
    texto = remover_acentos(limpar_texto(valor)).upper()
    if texto in {"SIM", "S", "TRUE", "1", "YES", "PAGO", "SACADO", "CAIU", "OK"}:
        return "SIM"
    return "NÃO"


def parse_data_iso(valor: Any) -> str:
    if valor is None:
        return ""
    if isinstance(valor, datetime):
        return valor.strftime("%Y-%m-%d")
    if isinstance(valor, date):
        return valor.strftime("%Y-%m-%d")
    texto = limpar_texto(valor)
    if not texto:
        return ""
    for formato in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y", "%d/%m/%y"):
        try:
            return datetime.strptime(texto, formato).strftime("%Y-%m-%d")
        except ValueError:
            pass
    return texto


def extrair_data_do_status(status_original: str, data_base: Any = None) -> str:
    texto = limpar_texto(status_original)
    match = re.search(r"(\d{1,2})[/-](\d{1,2})(?:[/-](\d{2,4}))?", texto)
    if not match:
        return ""
    dia = int(match.group(1))
    mes = int(match.group(2))
    ano_txt = match.group(3)
    if ano_txt:
        ano = int(ano_txt)
        if ano < 100:
            ano += 2000
    else:
        base_iso = parse_data_iso(data_base)
        try:
            ano = datetime.strptime(base_iso[:10], "%Y-%m-%d").year
        except ValueError:
            ano = date.today().year
    try:
        return date(ano, mes, dia).strftime("%Y-%m-%d")
    except ValueError:
        return ""


def normalizar_status_importacao(valor: Any) -> str:
    original = limpar_texto(valor)
    if not original:
        return "Novo lead"
    texto = remover_acentos(original).upper()
    texto_sem_data = re.sub(r"\b\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?\b", "", texto).strip()
    texto_sem_data = re.sub(r"\s+", " ", texto_sem_data)

    aliases = {
        "NOVO": "Novo lead",
        "NOVO LEAD": "Novo lead",
        "EM ATENDIMENTO": "Em atendimento",
        "SIMULACAO ENVIADA": "Simulação enviada",
        "AG DOCUMENTOS": "Aguardando documentos",
        "AG. DOCUMENTOS": "Aguardando documentos",
        "AG DESBLOQUEIO": "Aguardando desbloqueio",
        "AG. DESBLOQUEIO": "Aguardando desbloqueio",
        "AG INSERCAO": "Aguardando inserção",
        "AG. INSERCAO": "Aguardando inserção",
        "AG INTERACAO": "Aguardando interação",
        "AG. INTERACAO": "Aguardando interação",
        "AGUARDANDO INTERACAO": "Aguardando interação",
        "ATUACAO": "Atuação",
        "EM ANALISE": "Em análise",
        "AG CIP": "Aguardando CIP",
        "AG. CIP": "Aguardando CIP",
        "AG AVERBACAO": "Aguardando Averbação",
        "AG. AVERBACAO": "Aguardando Averbação",
        "AVERBADO": "Averbado",
        "AG PAGAMENTO": "Aguardando Pagamento",
        "AG. PAGAMENTO": "Aguardando Pagamento",
        "AG REAPRESENTACAO": "Aguardando Reapresentação",
        "AG. REAPRESENTACAO": "Aguardando Reapresentação",
        "PAGO": "Pago",
        "REPROVADO": "Perdido / Cancelado",
        "PERDIDO": "Perdido / Cancelado",
        "CANCELADO": "Perdido / Cancelado",
    }
    if texto_sem_data in aliases:
        return aliases[texto_sem_data]
    if texto_sem_data.startswith("AG CIP") or texto_sem_data.startswith("AG. CIP"):
        return "Aguardando CIP"
    if texto_sem_data.startswith("AG INTERACAO") or texto_sem_data.startswith("AG. INTERACAO"):
        return "Aguardando interação"
    if texto_sem_data.startswith("AG AVERBACAO") or texto_sem_data.startswith("AG. AVERBACAO"):
        return "Aguardando Averbação"
    if texto_sem_data.startswith("REPROV"):
        return "Perdido / Cancelado"

    # Se o texto já corresponder a uma etapa cadastrada, preserva o nome oficial.
    for status in nomes_status():
        if remover_acentos(status).upper() == texto_sem_data:
            return status
    return original


def mes_atual() -> str:
    return date.today().strftime("%Y-%m")


def status_encerrado(status: str) -> bool:
    return limpar_texto(status) in STATUS_ENCERRADOS


def produto_portabilidade(produto: Any) -> bool:
    texto = remover_acentos(limpar_texto(produto)).upper()
    return "PORT" in texto or "REFIN" in texto


def banco_digitado_exibicao(proposta: Any) -> str:
    try:
        dados = dict(proposta)
    except Exception:
        dados = proposta or {}
    banco_digitado = limpar_texto(dados.get("banco_digitado"))
    banco_destino = limpar_texto(dados.get("banco_destino"))
    banco_atual = limpar_texto(dados.get("banco_atual"))
    produto = dados.get("produto")
    if banco_digitado:
        return banco_digitado
    if produto_portabilidade(produto) and banco_destino:
        return banco_destino
    return banco_destino or banco_atual


def status_ativos() -> list[str]:
    return [status for status in nomes_status() if status not in STATUS_ENCERRADOS]


def mes_nome_para_numero(nome: str) -> int | None:
    texto = remover_acentos(limpar_texto(nome)).upper()
    mapa = {
        "JANEIRO": 1, "FEVEREIRO": 2, "MARCO": 3, "MARÇO": 3,
        "ABRIL": 4, "MAIO": 5, "JUNHO": 6, "JULHO": 7,
        "AGOSTO": 8, "SETEMBRO": 9, "OUTUBRO": 10,
        "NOVEMBRO": 11, "DEZEMBRO": 12,
    }
    return mapa.get(texto)


def nome_mes_pt(mes: str) -> str:
    nomes = [
        "JANEIRO", "FEVEREIRO", "MARÇO", "ABRIL", "MAIO", "JUNHO",
        "JULHO", "AGOSTO", "SETEMBRO", "OUTUBRO", "NOVEMBRO", "DEZEMBRO",
    ]
    try:
        numero = int((mes or "").split("-")[1])
        return nomes[numero - 1]
    except Exception:
        return ""


def linha_no_mes(row: dict[str, Any], mes_importacao: str) -> bool:
    if not mes_importacao:
        return True
    data_iso = parse_data_iso(row.get("data_criacao"))
    if not data_iso:
        # Sem data: importa para não descartar manualmente uma linha válida.
        return True
    return data_iso[:7] == mes_importacao


def normalizar_produto_importacao(valor: Any) -> str:
    original = limpar_texto(valor)
    texto = remover_acentos(original).upper()
    aliases = {
        "PORT": "Portabilidade",
        "PORTABILIDADE": "Portabilidade",
        "REFIN": "Refinanciamento",
        "REFIN DA PORT": "Refinanciamento",
        "REFINANCIAMENTO": "Refinanciamento",
        "NOVO": "Novo",
        "CARTAO": "Cartão",
        "SAQUE COMPLEMENTAR": "Saque Complementar",
    }
    return aliases.get(texto, original or "Outro")


def texto_planilha(valor: Any) -> str:
    if valor is None:
        return ""
    if isinstance(valor, float) and valor.is_integer():
        return str(int(valor))
    return limpar_texto(valor)

def registrar_historico(proposta_id: int, anterior: str | None, novo: str | None, observacao: str) -> None:
    db = get_db()
    db.execute(
        """
        INSERT INTO historico (proposta_id, data_hora, status_anterior, status_novo, observacao)
        VALUES (?, ?, ?, ?, ?)
        """,
        (proposta_id, agora_iso(), anterior, novo, observacao),
    )
    db.commit()


def registrar_anotacao(proposta_id: int, texto: str, data_hora: str | None = None) -> None:
    texto = limpar_texto(texto)
    if not texto:
        return
    db = get_db()
    db.execute(
        """
        INSERT INTO anotacoes (proposta_id, data_hora, texto)
        VALUES (?, ?, ?)
        """,
        (proposta_id, data_hora or agora_iso(), texto),
    )
    db.execute(
        "UPDATE propostas SET observacoes = ?, data_atualizacao = ? WHERE id = ?",
        (texto, agora_iso(), proposta_id),
    )
    db.commit()


def carregar_status_etapas(grupo: str | None = None) -> list[sqlite3.Row]:
    # O parâmetro grupo é mantido apenas para compatibilidade com versões anteriores.
    # Na v4 todas as etapas aparecem no mesmo funil compartilhado.
    db = get_db()
    return db.execute("SELECT * FROM status_etapas WHERE ativo = 1 ORDER BY ordem ASC, id ASC").fetchall()


def nomes_status(grupo: str | None = None) -> list[str]:
    nomes = [row["nome"] for row in carregar_status_etapas(grupo)]
    return nomes or STATUS_LIST


def status_padrao() -> str:
    lista = nomes_status()
    return lista[0] if lista else "Novo lead"


def status_valido(status: str) -> bool:
    return status in nomes_status()


def dados_formulario() -> dict[str, Any]:
    status = limpar_texto(request.form.get("status")) or "Novo lead"
    if not status_valido(status):
        status = status_padrao()

    return {
        "nome": limpar_texto(request.form.get("nome")),
        "cpf": formatar_cpf(limpar_texto(request.form.get("cpf"))),
        "nb_matricula": limpar_texto(request.form.get("nb_matricula")),
        "numero_proposta": limpar_texto(request.form.get("numero_proposta")),
        "numero_port_vinculada": limpar_texto(request.form.get("numero_port_vinculada")),
        "numero_refin_vinculada": limpar_texto(request.form.get("numero_refin_vinculada")),
        "tipo_cliente": limpar_texto(request.form.get("tipo_cliente")),
        "banco_atual": limpar_texto(request.form.get("banco_atual")),
        "banco_destino": limpar_texto(request.form.get("banco_destino")),
        "banco_digitado": limpar_texto(request.form.get("banco_digitado")),
        "produto": limpar_texto(request.form.get("produto")),
        "promotora": limpar_texto(request.form.get("promotora")),
        "beneficio_bloqueado": normalizar_bloqueado(request.form.get("beneficio_bloqueado")),
        "valor_caiu_promotora": normalizar_sim_nao(request.form.get("valor_caiu_promotora")),
        "valor_sacado": normalizar_sim_nao(request.form.get("valor_sacado")),
        "parcela_atual": parse_moeda(request.form.get("parcela_atual")),
        "nova_parcela": parse_moeda(request.form.get("nova_parcela")),
        "troco": parse_moeda(request.form.get("troco")),
        "comissao_percentual": parse_percentual(request.form.get("comissao_percentual")),
        "comissao": parse_moeda(request.form.get("comissao")),
        "margem_apos": limpar_texto(request.form.get("margem_apos")),
        "status": status,
        "responsavel": limpar_texto(request.form.get("responsavel")),
        "telefone": limpar_texto(request.form.get("telefone")),
        "endereco": limpar_texto(request.form.get("endereco")),
        "dados_bancarios": limpar_texto(request.form.get("dados_bancarios")),
        "proxima_acao": limpar_texto(request.form.get("proxima_acao")),
        "data_retorno": limpar_texto(request.form.get("data_retorno")),
        "observacoes": limpar_texto(request.form.get("observacoes")),
    }



def chave_cliente(cpf: Any, nb_matricula: Any) -> tuple[str, str]:
    """Retorna a chave lógica do cliente.

    A chave é CPF + matrícula. Quando a matrícula está vazia, usamos string vazia
    para permitir reaproveitamento em cadastros antigos, mas o ideal é preencher a matrícula.
    """
    return formatar_cpf(limpar_texto(cpf)), limpar_texto(nb_matricula)


def salvar_cliente_dos_dados(dados: dict[str, Any] | sqlite3.Row) -> int | None:
    """Cria ou atualiza o cadastro do cliente a partir dos dados da proposta.

    O benefício bloqueado não é salvo no cadastro do cliente porque muda de uma
    proposta para outra. A chave usada é CPF + NB/Matrícula.
    """
    item = dict(dados)
    nome = limpar_texto(item.get("nome"))
    cpf, nb = chave_cliente(item.get("cpf"), item.get("nb_matricula"))
    if not nome or not cpf:
        return None

    agora = agora_iso()
    db = get_db()
    existente = db.execute(
        "SELECT id FROM clientes WHERE cpf = ? AND COALESCE(nb_matricula, '') = ? LIMIT 1",
        (cpf, nb),
    ).fetchone()
    if existente:
        db.execute(
            """
            UPDATE clientes SET
                nome = ?, telefone = ?, tipo_cliente = ?, endereco = ?, dados_bancarios = ?, data_atualizacao = ?
            WHERE id = ?
            """,
            (
                nome,
                limpar_texto(item.get("telefone")),
                limpar_texto(item.get("tipo_cliente")),
                limpar_texto(item.get("endereco")),
                limpar_texto(item.get("dados_bancarios")),
                agora,
                existente["id"],
            ),
        )
        return int(existente["id"])

    cursor = db.execute(
        """
        INSERT INTO clientes (
            nome, cpf, nb_matricula, telefone, tipo_cliente, endereco, dados_bancarios, data_criacao, data_atualizacao
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            nome, cpf, nb,
            limpar_texto(item.get("telefone")),
            limpar_texto(item.get("tipo_cliente")),
            limpar_texto(item.get("endereco")),
            limpar_texto(item.get("dados_bancarios")),
            agora, agora,
        ),
    )
    return int(cursor.lastrowid)


def migrar_clientes_a_partir_de_propostas() -> None:
    db = get_db()
    propostas = db.execute(
        """
        SELECT * FROM propostas
        WHERE COALESCE(TRIM(cpf), '') <> ''
          AND (cliente_id IS NULL OR cliente_id = '')
        ORDER BY id ASC
        """
    ).fetchall()
    alterou = False
    for proposta in propostas:
        cliente_id = salvar_cliente_dos_dados(proposta)
        if cliente_id:
            db.execute("UPDATE propostas SET cliente_id = ? WHERE id = ?", (cliente_id, proposta["id"]))
            alterou = True
    if alterou:
        db.commit()

def buscar_proposta(proposta_id: int) -> sqlite3.Row | None:
    return get_db().execute("SELECT * FROM propostas WHERE id = ?", (proposta_id,)).fetchone()


def normalizar_numero_proposta(valor: Any) -> str:
    return limpar_texto(valor).upper()


def buscar_propostas_vinculadas(proposta: sqlite3.Row) -> list[sqlite3.Row]:
    """Busca propostas vinculadas manualmente por número de proposta.

    A vinculação é flexível: basta preencher o número próprio em uma proposta e,
    na outra, preencher esse número no campo de portabilidade/refin vinculado.
    """
    dados = dict(proposta)
    numeros = {
        normalizar_numero_proposta(dados.get("numero_proposta")),
        normalizar_numero_proposta(dados.get("numero_port_vinculada")),
        normalizar_numero_proposta(dados.get("numero_refin_vinculada")),
    }
    numeros.discard("")
    if not numeros:
        return []

    cpf = limpar_texto(dados.get("cpf"))
    placeholders = ",".join("?" for _ in numeros)
    params: list[Any] = [proposta["id"], *sorted(numeros)]
    where_cpf = ""
    if cpf:
        where_cpf = " OR cpf = ?"
        params.append(cpf)

    # Busca por referência cruzada ou mesmo CPF. Depois filtra em Python para
    # reduzir falsos positivos em clientes com mais de uma proposta independente.
    rows = get_db().execute(
        f"""
        SELECT * FROM propostas
        WHERE id <> ?
          AND (
                UPPER(COALESCE(numero_proposta, '')) IN ({placeholders})
             OR UPPER(COALESCE(numero_port_vinculada, '')) IN ({placeholders})
             OR UPPER(COALESCE(numero_refin_vinculada, '')) IN ({placeholders})
             {where_cpf}
          )
        ORDER BY data_criacao ASC, id ASC
        """,
        params[:1] + sorted(numeros) + sorted(numeros) + sorted(numeros) + ([cpf] if cpf else []),
    ).fetchall()

    vinculadas = []
    for row in rows:
        row_nums = {
            normalizar_numero_proposta(row["numero_proposta"]),
            normalizar_numero_proposta(row["numero_port_vinculada"]),
            normalizar_numero_proposta(row["numero_refin_vinculada"]),
        }
        row_nums.discard("")
        if numeros.intersection(row_nums) or (cpf and row["cpf"] == cpf and (dados.get("numero_port_vinculada") or dados.get("numero_refin_vinculada") or row["numero_port_vinculada"] or row["numero_refin_vinculada"])):
            vinculadas.append(row)
    return vinculadas


def produto_eh_portabilidade(proposta: sqlite3.Row | dict[str, Any]) -> bool:
    """Retorna True para portabilidade pura, evitando refin da port."""
    try:
        produto = proposta["produto"]
    except (KeyError, IndexError, TypeError):
        produto = ""
    texto = remover_acentos(limpar_texto(produto)).upper()
    if not texto:
        return False
    tem_port = "PORT" in texto or "PORTABILIDADE" in texto
    tem_refin = "REFIN" in texto or "REFINANCIAMENTO" in texto
    return tem_port and not tem_refin


def incrementar_numero_proposta(valor: Any) -> str:
    """Gera o número do refin como número da port + 1.

    Mantém zeros à esquerda quando o número é totalmente numérico.
    Para formatos com prefixo, incrementa os dígitos finais.
    """
    texto = limpar_texto(valor)
    if not texto:
        return ""
    if texto.isdigit():
        return str(int(texto) + 1).zfill(len(texto))

    match = re.search(r"(\d+)$", texto)
    if not match:
        return ""
    inicio, fim = match.span(1)
    numero = match.group(1)
    incrementado = str(int(numero) + 1).zfill(len(numero))
    return f"{texto[:inicio]}{incrementado}{texto[fim:]}"


def pode_criar_refin_vinculado(proposta: sqlite3.Row | dict[str, Any]) -> bool:
    """Exibe o botão apenas em portabilidades com número próprio preenchido."""
    try:
        numero = proposta["numero_proposta"]
    except (KeyError, IndexError, TypeError):
        numero = ""
    return produto_eh_portabilidade(proposta) and bool(incrementar_numero_proposta(numero))



def filtros_sql() -> tuple[str, list[Any], dict[str, str]]:
    filtros = {
        "nome": limpar_texto(request.args.get("nome")),
        "cpf": limpar_texto(request.args.get("cpf")),
        "mes": limpar_texto(request.args.get("mes")),
        "status": limpar_texto(request.args.get("status")),
        "banco_atual": limpar_texto(request.args.get("banco_atual")),
        "banco_destino": limpar_texto(request.args.get("banco_destino")),
        "banco_digitado": limpar_texto(request.args.get("banco_digitado")),
        "tipo_cliente": limpar_texto(request.args.get("tipo_cliente")),
        "produto": limpar_texto(request.args.get("produto")),
        "promotora": limpar_texto(request.args.get("promotora")),
        "beneficio_bloqueado": limpar_texto(request.args.get("beneficio_bloqueado")),
        "valor_caiu_promotora": limpar_texto(request.args.get("valor_caiu_promotora")),
        "valor_sacado": limpar_texto(request.args.get("valor_sacado")),
    }

    where = []
    params: list[Any] = []
    if filtros["nome"]:
        where.append("nome LIKE ?")
        params.append(f"%{filtros['nome']}%")
    if filtros["cpf"]:
        where.append("cpf LIKE ?")
        params.append(f"%{filtros['cpf']}%")
    if filtros["mes"]:
        where.append("substr(data_criacao, 1, 7) = ?")
        params.append(filtros["mes"])
    if filtros["status"]:
        where.append("status = ?")
        params.append(filtros["status"])
    if filtros["banco_atual"]:
        where.append("banco_atual LIKE ?")
        params.append(f"%{filtros['banco_atual']}%")
    if filtros["banco_destino"]:
        where.append("banco_destino LIKE ?")
        params.append(f"%{filtros['banco_destino']}%")
    if filtros["banco_digitado"]:
        where.append("COALESCE(banco_digitado, '') LIKE ?")
        params.append(f"%{filtros['banco_digitado']}%")
    if filtros["tipo_cliente"]:
        where.append("tipo_cliente = ?")
        params.append(filtros["tipo_cliente"])
    if filtros["produto"]:
        where.append("produto = ?")
        params.append(filtros["produto"])
    if filtros["promotora"]:
        where.append("promotora LIKE ?")
        params.append(f"%{filtros['promotora']}%")
    if filtros["beneficio_bloqueado"]:
        where.append("beneficio_bloqueado = ?")
        params.append(filtros["beneficio_bloqueado"])
    if filtros["valor_caiu_promotora"]:
        where.append("COALESCE(valor_caiu_promotora, 'NÃO') = ?")
        params.append(filtros["valor_caiu_promotora"])
    if filtros["valor_sacado"]:
        where.append("COALESCE(valor_sacado, 'NÃO') = ?")
        params.append(filtros["valor_sacado"])

    sql = " WHERE " + " AND ".join(where) if where else ""
    return sql, params, filtros


def carregar_modelos() -> dict[str, str]:
    try:
        db = get_db()
        # Garante a tabela para casos em que a função seja chamada antes do before_request.
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS modelos_mensagens (
                nome TEXT PRIMARY KEY,
                texto TEXT NOT NULL,
                ordem INTEGER NOT NULL DEFAULT 0,
                data_atualizacao TEXT
            )
            """
        )
        sincronizar_modelos_banco(db)
        db.commit()
        rows = db.execute("SELECT nome, texto FROM modelos_mensagens ORDER BY ordem, nome").fetchall()
        return {row["nome"]: row["texto"] for row in rows}
    except RuntimeError:
        # Fallback para execução fora do contexto Flask.
        return carregar_modelos_arquivo()


def proposta_para_dict(row: sqlite3.Row) -> dict[str, str]:
    dados = dict(row)
    dados["parcela_atual"] = br_moeda(dados.get("parcela_atual"))
    dados["nova_parcela"] = br_moeda(dados.get("nova_parcela"))
    dados["troco"] = br_moeda(dados.get("troco"))
    dados["valor"] = dados["troco"]
    dados["comissao_percentual"] = br_percentual(dados.get("comissao_percentual"))
    dados["comissao"] = br_moeda(dados.get("comissao"))
    return {k: "" if v is None else str(v) for k, v in dados.items()}


def montar_mensagens(proposta: sqlite3.Row) -> dict[str, str]:
    modelos = carregar_modelos()
    dados = proposta_para_dict(proposta)
    mensagens = {}
    for nome, modelo in modelos.items():
        try:
            mensagens[nome] = modelo.format(**dados)
        except KeyError:
            mensagens[nome] = modelo
    return mensagens


def hoje_iso() -> str:
    return date.today().isoformat()


def verificado_hoje(proposta: sqlite3.Row | dict[str, Any]) -> bool:
    try:
        valor = proposta["data_verificacao"]
    except (KeyError, IndexError, TypeError):
        valor = None
    return bool(valor and str(valor)[:10] == hoje_iso())


def status_verificacao_texto(proposta: sqlite3.Row | dict[str, Any]) -> str:
    return "Verificado hoje" if verificado_hoje(proposta) else "Não verificado hoje"


@app.context_processor
def helpers() -> dict[str, Any]:
    return {
        "STATUS_LIST": nomes_status(),
        "STATUS_VENDEDOR": nomes_status("vendedor"),
        "STATUS_ADMINISTRATIVO": nomes_status("administrativo"),
        "TIPOS_CLIENTE": TIPOS_CLIENTE,
        "PRODUTOS": PRODUTOS,
        "br_moeda": br_moeda,
        "br_percentual": br_percentual,
        "br_data": br_data,
        "br_data_hora": br_data_hora,
        "mes_atual": mes_atual,
        "status_encerrado": status_encerrado,
        "banco_digitado_exibicao": banco_digitado_exibicao,
        "tamanho_arquivo": tamanho_arquivo,
        "hoje_iso": hoje_iso,
        "verificado_hoje": verificado_hoje,
        "status_verificacao_texto": status_verificacao_texto,
        "pode_criar_refin_vinculado": pode_criar_refin_vinculado,
        "incrementar_numero_proposta": incrementar_numero_proposta,
        "anexos_base_dir": str(ANEXOS_BASE_DIR),
    }


@app.route("/")
def index():
    sql, params, filtros = filtros_sql()
    propostas = get_db().execute(
        f"SELECT * FROM propostas {sql} ORDER BY data_atualizacao DESC, id DESC", params
    ).fetchall()
    return render_template("index.html", propostas=propostas, filtros=filtros)


@app.route("/nova", methods=["GET", "POST"])
def nova_proposta():
    if request.method == "POST":
        dados = dados_formulario()
        if not dados["nome"]:
            flash("Informe o nome do cliente.", "erro")
            return render_template("nova_proposta.html", proposta=dados)

        agora = agora_iso()
        db = get_db()
        cursor = db.execute(
            """
            INSERT INTO propostas (
                cliente_id, nome, cpf, nb_matricula, numero_proposta, numero_port_vinculada, numero_refin_vinculada, tipo_cliente, banco_atual, banco_destino, banco_digitado, produto,
                promotora, beneficio_bloqueado, valor_caiu_promotora, valor_sacado, data_verificacao, parcela_atual, nova_parcela, troco, comissao_percentual, comissao, margem_apos, status, responsavel,
                telefone, endereco, dados_bancarios, data_criacao, data_atualizacao, proxima_acao, data_retorno, observacoes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                salvar_cliente_dos_dados(dados), dados["nome"], dados["cpf"], dados["nb_matricula"], dados["numero_proposta"],
                dados["numero_port_vinculada"], dados["numero_refin_vinculada"], dados["tipo_cliente"],
                dados["banco_atual"], dados["banco_destino"], dados["banco_digitado"], dados["produto"],
                dados["promotora"], dados["beneficio_bloqueado"], dados["valor_caiu_promotora"], dados["valor_sacado"], None, dados["parcela_atual"], dados["nova_parcela"], dados["troco"], dados["comissao_percentual"], dados["comissao"], dados["margem_apos"],
                dados["status"], dados["responsavel"], dados["telefone"], dados["endereco"], dados["dados_bancarios"], agora, agora,
                dados["proxima_acao"], dados["data_retorno"], dados["observacoes"],
            ),
        )
        db.commit()
        registrar_historico(cursor.lastrowid, None, dados["status"], "Proposta criada")
        if dados.get("observacoes"):
            registrar_anotacao(cursor.lastrowid, dados["observacoes"], agora)

        # v12: permite anexar documentos já na criação da proposta.
        proposta_criada = buscar_proposta(cursor.lastrowid)
        salvos = salvar_anexos_upload(
            cursor.lastrowid,
            proposta_criada or dados,
            request.files.getlist("arquivos"),
        )
        if salvos:
            registrar_historico(cursor.lastrowid, dados["status"], dados["status"], f"{salvos} anexo(s) enviado(s) na criação")
            flash(f"Proposta cadastrada com sucesso. {salvos} anexo(s) salvo(s) na pasta do cliente.", "ok")
        else:
            flash("Proposta cadastrada com sucesso.", "ok")
        return redirect(url_for("detalhe_proposta", proposta_id=cursor.lastrowid))

    proposta = {campo: "" for campo in CAMPOS_PROPOSTA}
    proposta["status"] = "Novo lead"
    return render_template("nova_proposta.html", proposta=proposta)


@app.route("/proposta/<int:proposta_id>/criar-refin-vinculado", methods=["POST"])
def criar_refin_vinculado(proposta_id: int):
    port = buscar_proposta(proposta_id)
    if not port:
        flash("Proposta de portabilidade não encontrada.", "erro")
        return redirect(url_for("index"))

    if not produto_eh_portabilidade(port):
        flash("O refinanciamento vinculado só pode ser criado a partir de uma proposta de portabilidade.", "erro")
        return redirect(url_for("detalhe_proposta", proposta_id=proposta_id))

    numero_port = limpar_texto(port["numero_proposta"])
    numero_refin = incrementar_numero_proposta(numero_port)
    if not numero_refin:
        flash("Informe um número de proposta válido na portabilidade para gerar o refinanciamento +1.", "erro")
        return redirect(url_for("detalhe_proposta", proposta_id=proposta_id))

    db = get_db()
    existente = db.execute(
        """
        SELECT * FROM propostas
        WHERE id <> ?
          AND UPPER(COALESCE(numero_proposta, '')) = UPPER(?)
        LIMIT 1
        """,
        (proposta_id, numero_refin),
    ).fetchone()

    agora = agora_iso()
    if existente:
        # Se o refin já existe, apenas garante o vínculo cruzado.
        db.execute(
            "UPDATE propostas SET numero_refin_vinculada = ?, data_atualizacao = ? WHERE id = ?",
            (numero_refin, agora, proposta_id),
        )
        db.execute(
            "UPDATE propostas SET numero_port_vinculada = ?, data_atualizacao = ? WHERE id = ? AND COALESCE(TRIM(numero_port_vinculada), '') = ''",
            (numero_port, agora, existente["id"]),
        )
        db.commit()
        registrar_historico(
            proposta_id,
            port["status"],
            port["status"],
            f"Refinanciamento vinculado existente localizado: nº {numero_refin}.",
        )
        flash("Refinanciamento existente vinculado à portabilidade.", "ok")
        return redirect(url_for("detalhe_proposta", proposta_id=existente["id"]))

    banco_refin = banco_digitado_exibicao(port) or port["banco_destino"] or port["banco_atual"] or ""
    status_inicial = status_padrao()
    observacao = f"Refinanciamento criado a partir da portabilidade nº {numero_port}."

    cursor = db.execute(
        """
        INSERT INTO propostas (
            cliente_id, nome, cpf, nb_matricula, numero_proposta, numero_port_vinculada, numero_refin_vinculada, tipo_cliente, banco_atual, banco_destino, banco_digitado, produto,
            promotora, beneficio_bloqueado, valor_caiu_promotora, valor_sacado, data_verificacao, parcela_atual, nova_parcela, troco, comissao_percentual, comissao, margem_apos, status, responsavel,
            telefone, endereco, dados_bancarios, data_criacao, data_atualizacao, proxima_acao, data_retorno, observacoes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            (port["cliente_id"] if "cliente_id" in port.keys() and port["cliente_id"] else salvar_cliente_dos_dados(port)),
            port["nome"], port["cpf"], port["nb_matricula"], numero_refin, numero_port, "",
            port["tipo_cliente"], banco_refin, banco_refin, banco_refin, "Refinanciamento",
            port["promotora"], port["beneficio_bloqueado"] or "NÃO", "NÃO", "NÃO", None,
            0, 0, 0, 0, 0, "", status_inicial, port["responsavel"], port["telefone"],
            port["endereco"] if "endereco" in port.keys() else "",
            port["dados_bancarios"] if "dados_bancarios" in port.keys() else "",
            agora, agora, "", "", observacao,
        ),
    )
    refin_id = cursor.lastrowid
    db.execute(
        "UPDATE propostas SET numero_refin_vinculada = ?, data_atualizacao = ? WHERE id = ?",
        (numero_refin, agora, proposta_id),
    )
    db.commit()

    registrar_historico(refin_id, None, status_inicial, f"Refinanciamento vinculado criado a partir da portabilidade nº {numero_port}.")
    registrar_anotacao(refin_id, observacao, agora)
    registrar_historico(proposta_id, port["status"], port["status"], f"Refinanciamento vinculado criado: nº {numero_refin}.")

    flash(f"Refinanciamento vinculado criado com nº {numero_refin}.", "ok")
    return redirect(url_for("detalhe_proposta", proposta_id=refin_id))


@app.route("/proposta/<int:proposta_id>")
def detalhe_proposta(proposta_id: int):
    proposta = buscar_proposta(proposta_id)
    if not proposta:
        flash("Proposta não encontrada.", "erro")
        return redirect(url_for("index"))
    historico = get_db().execute(
        "SELECT * FROM historico WHERE proposta_id = ? ORDER BY data_hora ASC", (proposta_id,)
    ).fetchall()
    anotacoes = get_db().execute(
        "SELECT * FROM anotacoes WHERE proposta_id = ? ORDER BY data_hora DESC, id DESC", (proposta_id,)
    ).fetchall()
    anexos = get_db().execute(
        "SELECT * FROM anexos WHERE proposta_id = ? ORDER BY data_upload DESC, id DESC",
        (proposta_id,),
    ).fetchall()
    vinculadas = buscar_propostas_vinculadas(proposta)
    mensagens = montar_mensagens(proposta)
    return render_template(
        "detalhe_proposta.html",
        proposta=proposta,
        historico=historico,
        anotacoes=anotacoes,
        anexos=anexos,
        vinculadas=vinculadas,
        pasta_anexos=pasta_cliente(proposta),
        mensagens=mensagens,
        modelos_mensagens=carregar_modelos(),
    )


@app.route("/api/propostas/buscar")
def api_buscar_propostas():
    termo = limpar_texto(request.args.get("q"))
    if len(termo) < 2:
        return jsonify([])
    like = f"%{termo}%"
    propostas = get_db().execute(
        """
        SELECT id, nome, cpf, telefone, status, produto, banco_digitado, banco_atual, banco_destino
        FROM propostas
        WHERE nome LIKE ? OR cpf LIKE ? OR telefone LIKE ?
           OR COALESCE(numero_proposta, '') LIKE ?
           OR COALESCE(numero_port_vinculada, '') LIKE ?
           OR COALESCE(numero_refin_vinculada, '') LIKE ?
        ORDER BY data_atualizacao DESC, id DESC
        LIMIT 10
        """,
        (like, like, like, like, like, like),
    ).fetchall()
    return jsonify([
        {
            "id": p["id"],
            "nome": p["nome"] or "",
            "cpf": p["cpf"] or "",
            "telefone": p["telefone"] or "",
            "status": p["status"] or "",
            "produto": p["produto"] or "",
            "banco": banco_digitado_exibicao(p) or p["banco_atual"] or p["banco_destino"] or "",
            "url": url_for("detalhe_proposta", proposta_id=p["id"]),
        }
        for p in propostas
    ])



@app.route("/api/clientes/por-cpf")
def api_clientes_por_cpf():
    cpf = formatar_cpf(limpar_texto(request.args.get("cpf")))
    if len(re.sub(r"\D", "", cpf)) < 11:
        return jsonify([])
    clientes = get_db().execute(
        """
        SELECT id, nome, cpf, nb_matricula, telefone, tipo_cliente, endereco, dados_bancarios, data_atualizacao
        FROM clientes
        WHERE cpf = ?
        ORDER BY
            CASE WHEN COALESCE(NULLIF(nb_matricula, ''), '') = '' THEN 1 ELSE 0 END,
            nb_matricula ASC,
            data_atualizacao DESC,
            id DESC
        """,
        (cpf,),
    ).fetchall()

    # Evita sugestões duplicadas para o mesmo CPF + matrícula.
    # Também evita mostrar "Sem matrícula" quando já existe uma matrícula real para o CPF,
    # porque isso confundiria o cadastro de nova proposta.
    por_matricula = {}
    possui_matricula_real = any((c["nb_matricula"] or "").strip() for c in clientes)

    for c in clientes:
        nb = (c["nb_matricula"] or "").strip()
        if not nb and possui_matricula_real:
            continue
        chave = nb or "__sem_matricula__"
        if chave not in por_matricula:
            por_matricula[chave] = c

    resposta = []
    for idx, c in enumerate(por_matricula.values(), start=1):
        nb = (c["nb_matricula"] or "").strip()
        label = f"Matrícula {idx}: {nb}" if nb else "Sem matrícula cadastrada"
        resposta.append({
            "id": c["id"],
            "label": label,
            "nome": c["nome"] or "",
            "cpf": c["cpf"] or "",
            "nb_matricula": c["nb_matricula"] or "",
            "telefone": c["telefone"] or "",
            "tipo_cliente": c["tipo_cliente"] or "",
            "endereco": c["endereco"] or "",
            "dados_bancarios": c["dados_bancarios"] or "",
        })
    return jsonify(resposta)

@app.route("/proposta/<int:proposta_id>/anexos", methods=["POST"])
def enviar_anexos(proposta_id: int):
    proposta = buscar_proposta(proposta_id)
    if not proposta:
        flash("Proposta não encontrada.", "erro")
        return redirect(url_for("index"))

    arquivos = request.files.getlist("arquivos")
    if not any(arquivo and arquivo.filename for arquivo in arquivos):
        flash("Selecione pelo menos um arquivo para anexar.", "erro")
        return redirect(url_for("detalhe_proposta", proposta_id=proposta_id))

    salvos = salvar_anexos_upload(proposta_id, proposta, arquivos)
    if salvos:
        registrar_historico(proposta_id, proposta["status"], proposta["status"], f"{salvos} anexo(s) enviado(s)")
        flash(f"{salvos} arquivo(s) anexado(s) na pasta do cliente.", "ok")
    return redirect(url_for("detalhe_proposta", proposta_id=proposta_id))


@app.route("/anexo/<int:anexo_id>/baixar")
def baixar_anexo(anexo_id: int):
    anexo = get_db().execute("SELECT * FROM anexos WHERE id = ?", (anexo_id,)).fetchone()
    if not anexo:
        flash("Anexo não encontrado.", "erro")
        return redirect(url_for("index"))
    caminho = Path(anexo["caminho"])
    if not caminho.exists():
        flash("O arquivo não foi encontrado na pasta do cliente.", "erro")
        return redirect(request.referrer or url_for("index"))
    return send_file(caminho, as_attachment=True, download_name=anexo["nome_original"])


@app.route("/anexo/<int:anexo_id>/excluir", methods=["POST"])
def excluir_anexo(anexo_id: int):
    db = get_db()
    anexo = db.execute("SELECT * FROM anexos WHERE id = ?", (anexo_id,)).fetchone()
    if not anexo:
        flash("Anexo não encontrado.", "erro")
        return redirect(url_for("index"))
    proposta_id = anexo["proposta_id"]
    caminho = Path(anexo["caminho"])
    try:
        if caminho.exists():
            caminho.unlink()
    except OSError as exc:
        flash(f"Registro removido, mas não foi possível apagar o arquivo: {exc}", "erro")
    db.execute("DELETE FROM anexos WHERE id = ?", (anexo_id,))
    db.commit()
    flash("Anexo removido.", "ok")
    return redirect(url_for("detalhe_proposta", proposta_id=proposta_id))


@app.route("/proposta/<int:proposta_id>/anotacao", methods=["POST"])
def adicionar_anotacao(proposta_id: int):
    proposta = buscar_proposta(proposta_id)
    if not proposta:
        flash("Proposta não encontrada.", "erro")
        return redirect(url_for("index"))
    texto = limpar_texto(request.form.get("texto"))
    if not texto:
        flash("Digite uma anotação antes de salvar.", "erro")
        return redirect(url_for("detalhe_proposta", proposta_id=proposta_id))
    registrar_anotacao(proposta_id, texto)
    registrar_historico(proposta_id, proposta["status"], proposta["status"], "Nova anotação adicionada")
    flash("Anotação adicionada ao histórico da proposta.", "ok")
    return redirect(url_for("detalhe_proposta", proposta_id=proposta_id))

@app.route("/proposta/<int:proposta_id>/verificacao", methods=["POST"])
def atualizar_verificacao(proposta_id: int):
    proposta = buscar_proposta(proposta_id)
    if not proposta:
        flash("Proposta não encontrada.", "erro")
        return redirect(url_for("index"))
    verificado = normalizar_sim_nao(request.form.get("verificado"))
    data_verificacao = hoje_iso() if verificado == "SIM" else None
    get_db().execute(
        "UPDATE propostas SET data_verificacao = ?, data_atualizacao = ? WHERE id = ?",
        (data_verificacao, agora_iso(), proposta_id),
    )
    get_db().commit()
    registrar_historico(
        proposta_id,
        proposta["status"],
        proposta["status"],
        "Proposta marcada como verificada hoje" if verificado == "SIM" else "Verificação diária removida",
    )
    flash("Verificação diária atualizada.", "ok")
    return redirect(url_for("detalhe_proposta", proposta_id=proposta_id))


@app.route("/mensagens/modelos", methods=["POST"])
def atualizar_modelos_mensagens():
    db = get_db()
    modelos_atuais = carregar_modelos()
    novos_modelos: dict[str, str] = {}

    for ordem, nome in enumerate(modelos_atuais.keys(), start=1):
        campo = f"modelo__{nome}"
        texto = request.form.get(campo)
        texto_final = texto if texto is not None else modelos_atuais[nome]
        novos_modelos[nome] = texto_final
        db.execute(
            """
            INSERT OR REPLACE INTO modelos_mensagens (nome, texto, ordem, data_atualizacao)
            VALUES (?, ?, ?, ?)
            """,
            (nome, texto_final, ordem, agora_iso()),
        )

    db.commit()

    # Mantém o JSON apenas como backup legível, mas a fonte principal agora é o database.db.
    DATA_DIR.mkdir(exist_ok=True)
    MODELOS_PATH.write_text(json.dumps(novos_modelos, ensure_ascii=False, indent=2), encoding="utf-8")

    flash("Mensagens padrão atualizadas.", "ok")
    destino = request.form.get("next") or request.referrer or url_for("index")
    return redirect(destino)


@app.route("/proposta/<int:proposta_id>/financeiro", methods=["POST"])
def atualizar_financeiro(proposta_id: int):
    proposta = buscar_proposta(proposta_id)
    if not proposta:
        flash("Proposta não encontrada.", "erro")
        return redirect(url_for("index"))
    caiu = normalizar_sim_nao(request.form.get("valor_caiu_promotora"))
    sacado = normalizar_sim_nao(request.form.get("valor_sacado"))
    get_db().execute(
        "UPDATE propostas SET valor_caiu_promotora = ?, valor_sacado = ?, data_atualizacao = ? WHERE id = ?",
        (caiu, sacado, agora_iso(), proposta_id),
    )
    get_db().commit()
    registrar_historico(
        proposta_id,
        proposta["status"],
        proposta["status"],
        f"Controle financeiro atualizado: caiu na promotora {caiu}; sacado {sacado}",
    )
    flash("Controle financeiro atualizado.", "ok")
    return redirect(url_for("detalhe_proposta", proposta_id=proposta_id))


@app.route("/proposta/<int:proposta_id>/editar", methods=["GET", "POST"])
def editar_proposta(proposta_id: int):
    proposta = buscar_proposta(proposta_id)
    if not proposta:
        flash("Proposta não encontrada.", "erro")
        return redirect(url_for("index"))

    if request.method == "POST":
        dados = dados_formulario()
        if not dados["nome"]:
            flash("Informe o nome do cliente.", "erro")
            return render_template("editar_proposta.html", proposta={**dict(proposta), **dados})

        status_anterior = proposta["status"]
        db = get_db()
        db.execute(
            """
            UPDATE propostas SET
                cliente_id = ?, nome = ?, cpf = ?, nb_matricula = ?, numero_proposta = ?, numero_port_vinculada = ?, numero_refin_vinculada = ?, tipo_cliente = ?, banco_atual = ?,
                banco_destino = ?, banco_digitado = ?, produto = ?, promotora = ?, beneficio_bloqueado = ?, valor_caiu_promotora = ?, valor_sacado = ?, parcela_atual = ?, nova_parcela = ?, troco = ?,
                comissao_percentual = ?, comissao = ?, margem_apos = ?, status = ?, responsavel = ?, telefone = ?, endereco = ?, dados_bancarios = ?, data_atualizacao = ?,
                proxima_acao = ?, data_retorno = ?, observacoes = ?
            WHERE id = ?
            """,
            (
                salvar_cliente_dos_dados(dados), dados["nome"], dados["cpf"], dados["nb_matricula"], dados["numero_proposta"],
                dados["numero_port_vinculada"], dados["numero_refin_vinculada"], dados["tipo_cliente"],
                dados["banco_atual"], dados["banco_destino"], dados["banco_digitado"], dados["produto"],
                dados["promotora"], dados["beneficio_bloqueado"], dados["valor_caiu_promotora"], dados["valor_sacado"], dados["parcela_atual"], dados["nova_parcela"], dados["troco"], dados["comissao_percentual"], dados["comissao"], dados["margem_apos"],
                dados["status"], dados["responsavel"], dados["telefone"], dados["endereco"], dados["dados_bancarios"], agora_iso(),
                dados["proxima_acao"], dados["data_retorno"], dados["observacoes"], proposta_id,
            ),
        )
        db.commit()
        if status_anterior != dados["status"]:
            registrar_historico(proposta_id, status_anterior, dados["status"], "Status alterado na edição")
        else:
            registrar_historico(proposta_id, status_anterior, dados["status"], "Dados da proposta atualizados")
        observacao_antiga = limpar_texto(proposta["observacoes"])
        if dados.get("observacoes") and dados["observacoes"] != observacao_antiga:
            registrar_anotacao(proposta_id, dados["observacoes"])
        flash("Proposta atualizada com sucesso.", "ok")
        return redirect(url_for("detalhe_proposta", proposta_id=proposta_id))

    return render_template("editar_proposta.html", proposta=proposta)


@app.route("/proposta/<int:proposta_id>/status", methods=["POST"])
def mudar_status(proposta_id: int):
    proposta = buscar_proposta(proposta_id)
    if not proposta:
        flash("Proposta não encontrada.", "erro")
        return redirect(url_for("index"))
    novo_status = limpar_texto(request.form.get("status"))
    observacao = limpar_texto(request.form.get("observacao")) or "Status atualizado"
    origem = limpar_texto(request.form.get("origem")) or "index"
    if not status_valido(novo_status):
        if request.headers.get("X-Requested-With") == "fetch":
            return jsonify({"ok": False, "erro": "Status inválido."}), 400
        flash("Status inválido.", "erro")
        return redirect(request.referrer or url_for("index"))
    if novo_status != proposta["status"]:
        get_db().execute(
            "UPDATE propostas SET status = ?, data_atualizacao = ? WHERE id = ?",
            (novo_status, agora_iso(), proposta_id),
        )
        get_db().commit()
        registrar_historico(proposta_id, proposta["status"], novo_status, observacao)
        if request.headers.get("X-Requested-With") == "fetch":
            return jsonify({"ok": True, "status": novo_status})
        flash("Status atualizado.", "ok")
    elif request.headers.get("X-Requested-With") == "fetch":
        return jsonify({"ok": True, "status": novo_status})
    if origem == "funil":
        return redirect(url_for("funil"))
    if origem == "encerradas":
        return redirect(url_for("encerradas"))
    if origem == "vendedor":
        return redirect(url_for("vendedor"))
    if origem == "administrativo":
        return redirect(url_for("administrativo"))
    return redirect(request.referrer or url_for("index"))


@app.route("/proposta/<int:proposta_id>/excluir", methods=["POST"])
def excluir_proposta(proposta_id: int):
    proposta = buscar_proposta(proposta_id)
    if not proposta:
        flash("Proposta não encontrada.", "erro")
        return redirect(url_for("index"))

    db = get_db()
    anexos = db.execute("SELECT * FROM anexos WHERE proposta_id = ?", (proposta_id,)).fetchall()

    # Remove arquivos físicos dos anexos, quando existirem.
    # Se algum arquivo estiver aberto/bloqueado pelo Windows, o registro ainda será removido do CRM.
    arquivos_com_erro = 0
    for anexo in anexos:
        caminho = Path(anexo["caminho"])
        try:
            if caminho.exists():
                caminho.unlink()
        except OSError:
            arquivos_com_erro += 1

    # Remove registros relacionados mesmo quando o SQLite antigo não estiver com cascade ativo.
    db.execute("DELETE FROM anexos WHERE proposta_id = ?", (proposta_id,))
    db.execute("DELETE FROM anotacoes WHERE proposta_id = ?", (proposta_id,))
    db.execute("DELETE FROM historico WHERE proposta_id = ?", (proposta_id,))
    db.execute("DELETE FROM propostas WHERE id = ?", (proposta_id,))
    db.commit()

    # Tenta remover a pasta do cliente se ela ficar vazia.
    try:
        pasta = pasta_cliente(proposta)
        if pasta.exists() and not any(pasta.iterdir()):
            pasta.rmdir()
    except OSError:
        pass

    if arquivos_com_erro:
        flash(f"Proposta excluída. {arquivos_com_erro} arquivo(s) não puderam ser apagados da pasta.", "erro")
    else:
        flash("Lead/proposta excluído com sucesso.", "ok")

    destino = request.form.get("next") or url_for("index")
    return redirect(destino)


def renderizar_funil(status_visiveis: list[str], titulo: str, subtitulo: str, modulo: str):
    if not status_visiveis:
        status_visiveis = status_ativos()
    placeholders = ",".join("?" for _ in status_visiveis)
    propostas = get_db().execute(
        f"SELECT * FROM propostas WHERE status IN ({placeholders}) ORDER BY data_retorno ASC, id DESC",
        status_visiveis,
    ).fetchall()
    por_status = {status: [] for status in status_visiveis}
    for proposta in propostas:
        por_status.setdefault(proposta["status"], []).append(proposta)
    totais_status = {
        status: {
            "qtd": len(itens),
            "comissao": sum(float(item["comissao"] or 0) for item in itens),
        }
        for status, itens in por_status.items()
    }
    return render_template(
        "funil.html",
        por_status=por_status,
        totais_status=totais_status,
        status_opcoes=nomes_status(),
        titulo=titulo,
        subtitulo=subtitulo,
        modulo=modulo,
    )


@app.route("/funil")
def funil():
    return renderizar_funil(
        status_ativos(),
        "Funil em andamento",
        "Mostra apenas propostas abertas. Pagas e perdidas ficam no menu Encerradas.",
        "geral",
    )


@app.route("/encerradas")
def encerradas():
    mes = limpar_texto(request.args.get("mes")) or mes_atual()
    propostas = get_db().execute(
        """
        SELECT * FROM propostas
        WHERE status IN ('Pago', 'Perdido / Cancelado', 'Perdido', 'Cancelado')
          AND substr(COALESCE(data_criacao, data_atualizacao), 1, 7) = ?
        ORDER BY data_atualizacao DESC, id DESC
        """,
        (mes,),
    ).fetchall()
    grupos = {
        "Pago - falta cair na promotora": [],
        "Pago - disponível para saque": [],
        "Pago - já sacado": [],
        "Perdido / Cancelado": [],
    }
    for proposta in propostas:
        if proposta["status"] == "Pago":
            caiu = (proposta["valor_caiu_promotora"] or "NÃO")
            sacado = (proposta["valor_sacado"] or "NÃO")
            if sacado == "SIM":
                grupos["Pago - já sacado"].append(proposta)
            elif caiu == "SIM":
                grupos["Pago - disponível para saque"].append(proposta)
            else:
                grupos["Pago - falta cair na promotora"].append(proposta)
        else:
            grupos["Perdido / Cancelado"].append(proposta)
    totais_status = {
        status: {
            "qtd": len(itens),
            "comissao": sum(float(item["comissao"] or 0) for item in itens),
        }
        for status, itens in grupos.items()
    }
    return render_template(
        "encerradas.html",
        por_status=grupos,
        totais_status=totais_status,
        status_opcoes=nomes_status(),
        titulo="Propostas encerradas",
        subtitulo="Pagas ficam separadas por comissão: falta cair, disponível para saque e já sacada.",
        modulo="encerradas",
        mes=mes,
    )


@app.route("/vendedor")
def vendedor():
    # Mantido para links antigos/favoritos. Agora há um único funil compartilhado.
    return redirect(url_for("funil"))


@app.route("/administrativo")
def administrativo():
    # Mantido para links antigos/favoritos. Agora há um único funil compartilhado.
    return redirect(url_for("funil"))



@app.route("/configuracoes/status", methods=["GET", "POST"])
def configurar_status():
    db = get_db()
    if request.method == "POST":
        acao = limpar_texto(request.form.get("acao"))

        if acao == "adicionar":
            nome = limpar_texto(request.form.get("nome"))
            grupo = "geral"
            if not nome:
                flash("Informe o nome da etapa.", "erro")
                return redirect(url_for("configurar_status"))
            existe = db.execute("SELECT id FROM status_etapas WHERE nome = ?", (nome,)).fetchone()
            if existe:
                flash("Já existe uma etapa com esse nome.", "erro")
                return redirect(url_for("configurar_status"))
            proxima_ordem = db.execute("SELECT COALESCE(MAX(ordem), 0) + 1 AS ordem FROM status_etapas").fetchone()["ordem"]
            db.execute(
                "INSERT INTO status_etapas (nome, grupo, ordem, ativo) VALUES (?, ?, ?, 1)",
                (nome, grupo, proxima_ordem),
            )
            db.commit()
            flash("Etapa adicionada.", "ok")
            return redirect(url_for("configurar_status"))

        if acao == "salvar":
            etapa_id = int(request.form.get("etapa_id") or 0)
            etapa = db.execute("SELECT * FROM status_etapas WHERE id = ?", (etapa_id,)).fetchone()
            if not etapa:
                flash("Etapa não encontrada.", "erro")
                return redirect(url_for("configurar_status"))
            nome = limpar_texto(request.form.get("nome"))
            grupo = "geral"
            ordem = int(request.form.get("ordem") or etapa["ordem"] or 0)
            ativo = 1 if request.form.get("ativo") == "1" else 0
            if not nome:
                flash("O nome da etapa não pode ficar vazio.", "erro")
                return redirect(url_for("configurar_status"))
            duplicada = db.execute(
                "SELECT id FROM status_etapas WHERE nome = ? AND id <> ?", (nome, etapa_id)
            ).fetchone()
            if duplicada:
                flash("Já existe outra etapa com esse nome.", "erro")
                return redirect(url_for("configurar_status"))
            db.execute(
                "UPDATE status_etapas SET nome = ?, grupo = ?, ordem = ?, ativo = ? WHERE id = ?",
                (nome, grupo, ordem, ativo, etapa_id),
            )
            if nome != etapa["nome"]:
                db.execute("UPDATE propostas SET status = ? WHERE status = ?", (nome, etapa["nome"]))
                db.execute("UPDATE historico SET status_anterior = ? WHERE status_anterior = ?", (nome, etapa["nome"]))
                db.execute("UPDATE historico SET status_novo = ? WHERE status_novo = ?", (nome, etapa["nome"]))
            db.commit()
            flash("Etapa atualizada.", "ok")
            return redirect(url_for("configurar_status"))

        if acao == "excluir":
            etapa_id = int(request.form.get("etapa_id") or 0)
            destino = limpar_texto(request.form.get("destino_status"))
            etapa = db.execute("SELECT * FROM status_etapas WHERE id = ?", (etapa_id,)).fetchone()
            if not etapa:
                flash("Etapa não encontrada.", "erro")
                return redirect(url_for("configurar_status"))
            if not destino or destino == etapa["nome"] or not status_valido(destino):
                flash("Escolha uma etapa de destino válida antes de excluir.", "erro")
                return redirect(url_for("configurar_status"))
            db.execute("UPDATE propostas SET status = ? WHERE status = ?", (destino, etapa["nome"]))
            db.execute("DELETE FROM status_etapas WHERE id = ?", (etapa_id,))
            db.commit()
            flash("Etapa excluída e propostas movidas para a etapa escolhida.", "ok")
            return redirect(url_for("configurar_status"))

    etapas = carregar_status_etapas()
    return render_template(
        "status_config.html",
        etapas=etapas,
        titulo="Configurar etapas",
        subtitulo="Edite os nomes, a ordem e quais etapas ficam ativas no funil.",
    )


def consulta_dashboard(mes: str) -> dict[str, Any]:
    db = get_db()
    propostas = db.execute(
        "SELECT * FROM propostas WHERE substr(data_criacao, 1, 7) = ? ORDER BY data_criacao DESC", (mes,)
    ).fetchall()
    total = len(propostas)
    pagas = [p for p in propostas if p["status"] == "Pago"]
    perdidas = [p for p in propostas if p["status"] in ("Perdido", "Cancelado", "Perdido / Cancelado")]
    troco_previsto = sum(float(p["troco"] or 0) for p in propostas)
    troco_pago = sum(float(p["troco"] or 0) for p in pagas)
    comissao_prevista = sum(float(p["comissao"] or 0) for p in propostas)
    comissao_paga = sum(float(p["comissao"] or 0) for p in pagas)
    valor_a_sacar = sum(float(p["comissao"] or 0) for p in pagas if (p["valor_caiu_promotora"] or "NÃO") == "SIM" and (p["valor_sacado"] or "NÃO") != "SIM")
    falta_cair_promotora = sum(float(p["comissao"] or 0) for p in pagas if (p["valor_caiu_promotora"] or "NÃO") != "SIM")
    valor_ja_sacado = sum(float(p["comissao"] or 0) for p in pagas if (p["valor_sacado"] or "NÃO") == "SIM")

    def agrupar(campo: str) -> list[dict[str, Any]]:
        rows = db.execute(
            f"""
            SELECT COALESCE(NULLIF({campo}, ''), 'Não informado') AS nome, COUNT(*) AS qtd
            FROM propostas
            WHERE substr(data_criacao, 1, 7) = ?
            GROUP BY COALESCE(NULLIF({campo}, ''), 'Não informado')
            ORDER BY qtd DESC, nome ASC
            """,
            (mes,),
        ).fetchall()
        maior = max([r["qtd"] for r in rows], default=1)
        return [{"nome": r["nome"], "qtd": r["qtd"], "percentual": round((r["qtd"] / maior) * 100, 1)} for r in rows]

    return {
        "mes": mes,
        "total": total,
        "pagas": len(pagas),
        "perdidas": len(perdidas),
        "troco_previsto": troco_previsto,
        "troco_pago": troco_pago,
        "comissao_prevista": comissao_prevista,
        "comissao_paga": comissao_paga,
        "valor_a_sacar": valor_a_sacar,
        "falta_cair_promotora": falta_cair_promotora,
        "valor_ja_sacado": valor_ja_sacado,
        "por_status": agrupar("status"),
        "por_banco": agrupar("banco_destino"),
        "por_produto": agrupar("produto"),
    }


@app.route("/dashboard")
def dashboard():
    mes = limpar_texto(request.args.get("mes")) or mes_atual()
    dados = consulta_dashboard(mes)
    return render_template("dashboard.html", dados=dados)


@app.route("/exportar/csv")
def exportar_csv():
    propostas = get_db().execute("SELECT * FROM propostas ORDER BY data_criacao DESC").fetchall()
    output = io.StringIO()
    writer = csv.writer(output, delimiter=";")
    colunas = [desc[0] for desc in get_db().execute("SELECT * FROM propostas LIMIT 1").description]
    writer.writerow(colunas)
    for p in propostas:
        writer.writerow([p[c] for c in colunas])
    memoria = io.BytesIO(output.getvalue().encode("utf-8-sig"))
    return send_file(memoria, mimetype="text/csv", as_attachment=True, download_name="propostas_crm.csv")


@app.route("/exportar/xlsx")
def exportar_xlsx():
    propostas = get_db().execute("SELECT * FROM propostas ORDER BY data_criacao DESC").fetchall()
    wb = Workbook()
    ws = wb.active
    ws.title = "Propostas"
    colunas = [desc[0] for desc in get_db().execute("SELECT * FROM propostas LIMIT 1").description]
    ws.append(colunas)
    for p in propostas:
        ws.append([p[c] for c in colunas])
    memoria = io.BytesIO()
    wb.save(memoria)
    memoria.seek(0)
    return send_file(memoria, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", as_attachment=True, download_name="propostas_crm.xlsx")


def normalizar_cabecalho(cabecalho: Any) -> str:
    texto = limpar_texto(cabecalho).lower()
    texto = texto.replace("ç", "c").replace("ã", "a").replace("õ", "o").replace("á", "a").replace("à", "a").replace("é", "e").replace("ê", "e").replace("í", "i").replace("ó", "o").replace("ô", "o").replace("ú", "u")
    texto = re.sub(r"[^a-z0-9]+", "_", texto).strip("_")
    aliases = {
        "nome_do_cliente": "nome",
        "cliente": "nome",
        "nb": "nb_matricula",
        "matricula": "nb_matricula",
        "nb_ou_matricula": "nb_matricula",
        "tipo": "tipo_cliente",
        "banco_origem": "banco_atual",
        "banco_atual": "banco_atual",
        "banco": "banco_digitado",
        "banco_digitado": "banco_digitado",
        "banco_de_digitacao": "banco_digitado",
        "digitado": "banco_digitado",
        "destino": "banco_destino",
        "banco_destino": "banco_destino",
        "promotora": "promotora",
        "promotora_responsavel": "promotora",
        "bloqueado": "beneficio_bloqueado",
        "beneficio_bloqueado": "beneficio_bloqueado",
        "beneficio": "beneficio_bloqueado",
        "valor": "troco",
        "parcela": "parcela_atual",
        "valor_da_parcela_atual": "parcela_atual",
        "valor_da_nova_parcela": "nova_parcela",
        "nova_parcela": "nova_parcela",
        "valor_de_troco": "troco",
        "comissao_percentual": "comissao_percentual",
        "percentual_comissao": "comissao_percentual",
        "percentual_da_comissao": "comissao_percentual",
        "porcentagem_comissao": "comissao_percentual",
        "porcentagem_da_comissao": "comissao_percentual",
        "comissao_%": "comissao_percentual",
        "comissao": "comissao",
        "comissão": "comissao",
        "valor_da_comissao": "comissao",
        "valor_da_comissão": "comissao",
        "pontos": "comissao",
        "saldo_pmt": "valor_caiu_promotora",
        "saldo_pmt_": "valor_caiu_promotora",
        "valor_caiu_na_promotora": "valor_caiu_promotora",
        "caiu_na_promotora": "valor_caiu_promotora",
        "valor_caiu_promotora": "valor_caiu_promotora",
        "acerto": "valor_sacado",
        "sacado": "valor_sacado",
        "valor_ja_foi_sacado": "valor_sacado",
        "valor_sacado": "valor_sacado",
        "margem": "margem_apos",
        "whatsapp": "telefone",
        "telefone_whatsapp": "telefone",
        "retorno": "data_retorno",
        "data_de_retorno": "data_retorno",
        "previsao_de_saldo": "data_retorno",
        "previsao_saldo": "data_retorno",
        "data_previsao_saldo": "data_retorno",
        "observacao": "observacoes",
        "motivo": "observacoes",
        "motivos": "observacoes",
        "numero_proposta": "numero_proposta",
        "n_proposta": "numero_proposta",
        "n_da_proposta": "numero_proposta",
        "proposta": "numero_proposta",
        "codigo_proposta": "numero_proposta",
        "numero_port": "numero_port_vinculada",
        "proposta_port": "numero_port_vinculada",
        "proposta_portabilidade": "numero_port_vinculada",
        "numero_proposta_port": "numero_port_vinculada",
        "numero_refin": "numero_refin_vinculada",
        "proposta_refin": "numero_refin_vinculada",
        "proposta_refinanciamento": "numero_refin_vinculada",
        "numero_proposta_refin": "numero_refin_vinculada",
        "dia": "data_criacao",
        "data": "data_criacao",
        "endereco": "endereco",
        "endereço": "endereco",
        "dados_bancarios": "dados_bancarios",
        "dados_bancarios_cliente": "dados_bancarios",
        "banco_cliente": "dados_bancarios",
        "conta_cliente": "dados_bancarios",
        "dados_da_conta": "dados_bancarios",
    }
    return aliases.get(texto, texto)


@app.route("/importar", methods=["POST"])
def importar():
    arquivo = request.files.get("arquivo")
    if not arquivo or not arquivo.filename:
        flash("Selecione um arquivo CSV ou XLSX.", "erro")
        return redirect(url_for("index"))

    nome = arquivo.filename.lower()
    mes_importacao = limpar_texto(request.form.get("mes_importacao")) or mes_atual()
    aba_preferida = nome_mes_pt(mes_importacao)
    linhas: list[dict[str, Any]] = []
    try:
        if nome.endswith(".csv"):
            conteudo = arquivo.read().decode("utf-8-sig")
            sample = conteudo[:2048]
            delimiter = ";" if sample.count(";") >= sample.count(",") else ","
            reader = csv.DictReader(io.StringIO(conteudo), delimiter=delimiter)
            for row in reader:
                linhas.append({normalizar_cabecalho(k): v for k, v in row.items()})
        elif nome.endswith(".xlsx"):
            wb = load_workbook(arquivo, data_only=True)
            planilha_encontrada = False
            worksheets = wb.worksheets
            if aba_preferida:
                preferidas = [ws for ws in worksheets if remover_acentos(ws.title).upper() == remover_acentos(aba_preferida).upper()]
                outras = [ws for ws in worksheets if ws not in preferidas]
                worksheets = preferidas + outras
            for ws in worksheets:
                rows = list(ws.iter_rows(values_only=True))
                if not rows:
                    continue
                header_idx = None
                for idx, possivel_header in enumerate(rows[:10]):
                    headers_teste = [normalizar_cabecalho(h) for h in possivel_header]
                    if "nome" in headers_teste and ("cpf" in headers_teste or "status" in headers_teste):
                        header_idx = idx
                        break
                if header_idx is None:
                    continue
                headers = [normalizar_cabecalho(h) for h in rows[header_idx]]
                for row in rows[header_idx + 1:]:
                    linhas.append({headers[i]: row[i] if i < len(row) else "" for i in range(len(headers))})
                planilha_encontrada = True
                break
            if not planilha_encontrada:
                flash("Não encontrei uma aba com cabeçalhos como NOME, CPF e STATUS.", "erro")
                return redirect(url_for("index"))
        else:
            flash("Formato inválido. Use CSV ou XLSX.", "erro")
            return redirect(url_for("index"))
    except Exception as exc:
        flash(f"Erro ao ler arquivo: {exc}", "erro")
        return redirect(url_for("index"))

    linhas_filtradas = [row for row in linhas if linha_no_mes(row, mes_importacao)]

    importadas = 0
    ignoradas_mes = len(linhas) - len(linhas_filtradas)
    db = get_db()
    for row in linhas_filtradas:
        nome_cliente = limpar_texto(row.get("nome"))
        if not nome_cliente:
            continue
        status_original = limpar_texto(row.get("status"))
        status = normalizar_status_importacao(status_original)
        if not status_valido(status):
            status = status_padrao()
        produto_importado = normalizar_produto_importacao(row.get("produto"))
        banco_digitado_importado = texto_planilha(row.get("banco_digitado"))
        banco_destino_importado = texto_planilha(row.get("banco_destino"))
        if not banco_destino_importado and produto_portabilidade(produto_importado):
            banco_destino_importado = banco_digitado_importado
        agora = agora_iso()
        cursor = db.execute(
            """
            INSERT INTO propostas (
                cliente_id, nome, cpf, nb_matricula, numero_proposta, numero_port_vinculada, numero_refin_vinculada, tipo_cliente, banco_atual, banco_destino, banco_digitado, produto,
                promotora, beneficio_bloqueado, valor_caiu_promotora, valor_sacado, data_verificacao, parcela_atual, nova_parcela, troco, comissao_percentual, comissao, margem_apos, status, responsavel,
                telefone, endereco, dados_bancarios, data_criacao, data_atualizacao, proxima_acao, data_retorno, observacoes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                salvar_cliente_dos_dados({
                    "nome": nome_cliente,
                    "cpf": formatar_cpf(texto_planilha(row.get("cpf"))),
                    "nb_matricula": texto_planilha(row.get("nb_matricula")),
                    "telefone": texto_planilha(row.get("telefone")),
                    "tipo_cliente": texto_planilha(row.get("tipo_cliente")),
                    "endereco": texto_planilha(row.get("endereco")),
                    "dados_bancarios": texto_planilha(row.get("dados_bancarios")),
                }),
                nome_cliente,
                formatar_cpf(texto_planilha(row.get("cpf"))),
                texto_planilha(row.get("nb_matricula")),
                texto_planilha(row.get("numero_proposta")),
                texto_planilha(row.get("numero_port_vinculada")),
                texto_planilha(row.get("numero_refin_vinculada")),
                texto_planilha(row.get("tipo_cliente")),
                texto_planilha(row.get("banco_atual")),
                banco_destino_importado,
                banco_digitado_importado,
                produto_importado,
                texto_planilha(row.get("promotora")),
                normalizar_bloqueado(row.get("beneficio_bloqueado")),
                normalizar_sim_nao(row.get("valor_caiu_promotora")),
                normalizar_sim_nao(row.get("valor_sacado")),
                None,
                parse_moeda(row.get("parcela_atual")),
                parse_moeda(row.get("nova_parcela")),
                parse_moeda(row.get("troco")),
                parse_percentual(row.get("comissao_percentual")),
                parse_moeda(row.get("comissao")),
                limpar_texto(row.get("margem_apos")),
                status,
                texto_planilha(row.get("responsavel")),
                texto_planilha(row.get("telefone")),
                texto_planilha(row.get("endereco")),
                texto_planilha(row.get("dados_bancarios")),
                parse_data_iso(row.get("data_criacao")) or agora,
                agora,
                texto_planilha(row.get("proxima_acao")),
                parse_data_iso(row.get("data_retorno")) or extrair_data_do_status(limpar_texto(row.get("status")), row.get("data_criacao")),
                texto_planilha(row.get("observacoes")),
            ),
        )
        db.commit()
        registrar_historico(cursor.lastrowid, None, status, "Proposta importada")
        observacao_importada = texto_planilha(row.get("observacoes"))
        if observacao_importada:
            registrar_anotacao(cursor.lastrowid, observacao_importada, agora)
        importadas += 1

    complemento = f" Ignoradas por mês diferente: {ignoradas_mes}." if ignoradas_mes else ""
    flash(f"Importação concluída: {importadas} proposta(s) importada(s) de {mes_importacao}.{complemento}", "ok")
    return redirect(url_for("index"))


if __name__ == "__main__":
    os.environ.setdefault("FLASK_ENV", "development")
    with app.app_context():
        init_db()
        garantir_modelos()
        criar_backup_automatico()
    app.run(host="0.0.0.0", port=5000, debug=False)
