from __future__ import annotations

import os
import shutil
import sqlite3
from contextlib import contextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DATABASE_PATH = DATA_DIR / "crm.db"
SOURCE_DATABASE = Path(os.getenv(
    "CRM_SOURCE_DB", r"C:\GitHub\Python\Práticas Avulsas\CRM Consignado\database.db"
))


def prepare_database() -> None:
    """Cria uma cópia local uma única vez; nunca modifica o banco de origem."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if DATABASE_PATH.exists():
        return
    if not SOURCE_DATABASE.exists():
        raise RuntimeError(f"Banco de origem não encontrado: {SOURCE_DATABASE}")
    shutil.copy2(SOURCE_DATABASE, DATABASE_PATH)


@contextmanager
def db():
    prepare_database()
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def rows(cursor: sqlite3.Cursor) -> list[dict]:
    return [dict(item) for item in cursor.fetchall()]

