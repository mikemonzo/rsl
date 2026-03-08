from __future__ import annotations

import sqlite3
from typing import Optional

from sqlmodel import SQLModel, create_engine

from .tables import ArtifactDB, ChampionDB

REQUIRED_DB_COLUMNS = {
    "champions": {
        "champion_id",
        "name",
        "rarity",
        "role",
        "level",
        "stars",
        "hp",
        "atk",
        "defense",
        "speed",
        "crit_rate",
        "crit_damage",
        "resistance",
        "accuracy",
        "preferred_sets_json",
        "notes",
    },
    "artifacts": {
        "artifact_id",
        "name",
        "set_name",
        "slot",
        "rank",
        "level",
        "rarity",
        "main_stat",
        "main_value",
        "substats_json",
        "equipped_by",
        "is_new",
    },
}


def is_database_url(db_target: str) -> bool:
    return "://" in db_target


def resolve_database_url(db_target: str) -> str:
    if is_database_url(db_target):
        return db_target
    return f"sqlite:///{db_target}"


def sqlite_file_from_target(db_target: str) -> Optional[str]:
    db_url = resolve_database_url(db_target)
    if not db_url.startswith("sqlite:///"):
        return None
    return db_url.removeprefix("sqlite:///")


def get_engine(db_target: str):
    return create_engine(resolve_database_url(db_target), echo=False, pool_pre_ping=True)


def _drop_legacy_tables_if_needed(db_target: str) -> None:
    sqlite_file = sqlite_file_from_target(db_target)
    if not sqlite_file:
        return

    with sqlite3.connect(sqlite_file) as conn:
        for table, required in REQUIRED_DB_COLUMNS.items():
            cols = {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}
            if cols and not required.issubset(cols):
                conn.execute(f"DROP TABLE IF EXISTS {table}")
        conn.commit()


def init_db(db_target: str) -> None:
    # Import side effect ensures SQLModel metadata includes all table classes.
    _ = (ChampionDB, ArtifactDB)
    _drop_legacy_tables_if_needed(db_target)
    SQLModel.metadata.create_all(get_engine(db_target))
