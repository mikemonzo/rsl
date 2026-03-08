from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import typer

from rsl_advisor.interfaces.cli_handlers.artifacts import (
    add_artifact_handler,
    edit_artifact_handler,
    list_artifacts_handler,
)
from rsl_advisor.interfaces.cli_handlers.champions import (
    add_champion_handler,
    edit_champion_handler,
    list_champions_handler,
)
from rsl_advisor.interfaces.cli_handlers.recommendations import recommend_handler
from rsl_advisor.interfaces.cli_handlers.system import init_db_handler, sync_handler

app = typer.Typer(add_completion=False, no_args_is_help=True)
DEFAULT_DB_TARGET = os.getenv("DATABASE_URL", "advisor.db")


@app.command("init-db")
def init_db_command(
    db: str = typer.Option(
        DEFAULT_DB_TARGET, "--db", help="Ruta SQLite o URL de base de datos"
    ),
) -> None:
    init_db_handler(db)
    typer.echo(f"Base de datos inicializada: {db}")


@app.command("sync")
def sync_command(
    champions_csv: Path = typer.Option(
        Path("champions.csv"), "--champions-csv", help="CSV de campeones"
    ),
    artifacts_csv: Path = typer.Option(
        Path("artifacts.csv"), "--artifacts-csv", help="CSV de artefactos"
    ),
    db: str = typer.Option(
        DEFAULT_DB_TARGET, "--db", help="Ruta SQLite o URL de base de datos"
    ),
) -> None:
    sync_handler(str(champions_csv), str(artifacts_csv), db)


@app.command("add-champion")
def add_champion_command(
    champion_id: str = typer.Option(..., "--champion-id", help="ID unico del campeon"),
    name: str = typer.Option(..., "--name", help="Nombre del campeon"),
    rarity: str = typer.Option(..., "--rarity", help="Rare/Epic/Legendary/Mystic"),
    role: str = typer.Option(..., "--role", help="Rol usado por la heuristica"),
    level: int = typer.Option(1, "--level", min=1, max=100),
    stars: int = typer.Option(1, "--stars", min=1, max=6),
    hp: int = typer.Option(0, "--hp", min=0),
    atk: int = typer.Option(0, "--atk", min=0),
    defense: int = typer.Option(0, "--defense", min=0),
    speed: int = typer.Option(0, "--speed", min=0),
    crit_rate: float = typer.Option(0.0, "--crit-rate", min=0.0),
    crit_damage: float = typer.Option(0.0, "--crit-damage", min=0.0),
    resistance: int = typer.Option(0, "--resistance", min=0),
    accuracy: int = typer.Option(0, "--accuracy", min=0),
    preferred_sets: str = typer.Option(
        "",
        "--preferred-sets",
        help="Sets preferidos separados por |. Ej: Speed|Perception",
    ),
    notes: str = typer.Option("", "--notes", help="Notas del campeon"),
    db: str = typer.Option(
        DEFAULT_DB_TARGET, "--db", help="Ruta SQLite o URL de base de datos"
    ),
) -> None:
    add_champion_handler(
        champion_id=champion_id,
        name=name,
        rarity=rarity,
        role=role,
        level=level,
        stars=stars,
        hp=hp,
        atk=atk,
        defense=defense,
        speed=speed,
        crit_rate=crit_rate,
        crit_damage=crit_damage,
        resistance=resistance,
        accuracy=accuracy,
        preferred_sets=preferred_sets,
        notes=notes,
        db=db,
    )


@app.command("add-artifact")
def add_artifact_command(
    artifact_id: str = typer.Option(..., "--artifact-id", help="ID unico del artefacto"),
    name: str = typer.Option(..., "--name", help="Nombre del artefacto"),
    set_name: str = typer.Option(..., "--set-name", help="Nombre del set"),
    slot: str = typer.Option(..., "--slot", help="boots/chest/gloves/etc"),
    rank: int = typer.Option(0, "--rank", min=0),
    level: int = typer.Option(0, "--level", min=0),
    rarity: str = typer.Option("", "--rarity"),
    main_stat: str = typer.Option(..., "--main-stat", help="Ej: SPD, C.RATE, HP%"),
    main_value: float = typer.Option(0.0, "--main-value"),
    substats: str = typer.Option(
        "",
        "--substats",
        help="Formato STAT:valor|STAT:valor. Ej: SPD:8|ACC:30",
    ),
    equipped_by: str = typer.Option("", "--equipped-by", help="ID del campeon equipado"),
    is_new: bool = typer.Option(False, "--is-new", help="Marcar como artefacto nuevo"),
    db: str = typer.Option(
        DEFAULT_DB_TARGET, "--db", help="Ruta SQLite o URL de base de datos"
    ),
) -> None:
    add_artifact_handler(
        artifact_id=artifact_id,
        name=name,
        set_name=set_name,
        slot=slot,
        rank=rank,
        level=level,
        rarity=rarity,
        main_stat=main_stat,
        main_value=main_value,
        substats=substats,
        equipped_by=equipped_by,
        is_new=is_new,
        db=db,
    )


@app.command("edit-champion")
def edit_champion_command(
    champion_id: str = typer.Option(..., "--champion-id", help="ID del campeon a editar"),
    rarity: Optional[str] = typer.Option(None, "--rarity"),
    role: Optional[str] = typer.Option(None, "--role"),
    level: Optional[int] = typer.Option(None, "--level", min=1, max=100),
    stars: Optional[int] = typer.Option(None, "--stars", min=1, max=6),
    hp: Optional[int] = typer.Option(None, "--hp", min=0),
    atk: Optional[int] = typer.Option(None, "--atk", min=0),
    defense: Optional[int] = typer.Option(None, "--defense", min=0),
    speed: Optional[int] = typer.Option(None, "--speed", min=0),
    crit_rate: Optional[float] = typer.Option(None, "--crit-rate", min=0.0),
    crit_damage: Optional[float] = typer.Option(None, "--crit-damage", min=0.0),
    resistance: Optional[int] = typer.Option(None, "--resistance", min=0),
    accuracy: Optional[int] = typer.Option(None, "--accuracy", min=0),
    preferred_sets: Optional[str] = typer.Option(
        None,
        "--preferred-sets",
        help="Sets preferidos separados por |. Ej: Speed|Perception",
    ),
    notes: Optional[str] = typer.Option(None, "--notes"),
    db: str = typer.Option(
        DEFAULT_DB_TARGET, "--db", help="Ruta SQLite o URL de base de datos"
    ),
) -> None:
    edit_champion_handler(
        champion_id=champion_id,
        rarity=rarity,
        role=role,
        level=level,
        stars=stars,
        hp=hp,
        atk=atk,
        defense=defense,
        speed=speed,
        crit_rate=crit_rate,
        crit_damage=crit_damage,
        resistance=resistance,
        accuracy=accuracy,
        preferred_sets=preferred_sets,
        notes=notes,
        db=db,
    )


@app.command("edit-artifact")
def edit_artifact_command(
    artifact_id: str = typer.Option(..., "--artifact-id", help="ID del artefacto a editar"),
    name: Optional[str] = typer.Option(None, "--name"),
    set_name: Optional[str] = typer.Option(None, "--set-name"),
    slot: Optional[str] = typer.Option(None, "--slot"),
    rank: Optional[int] = typer.Option(None, "--rank", min=0),
    level: Optional[int] = typer.Option(None, "--level", min=0),
    rarity: Optional[str] = typer.Option(None, "--rarity"),
    main_stat: Optional[str] = typer.Option(None, "--main-stat"),
    main_value: Optional[float] = typer.Option(None, "--main-value"),
    substats: Optional[str] = typer.Option(None, "--substats"),
    equipped_by: Optional[str] = typer.Option(
        None, "--equipped-by", help="ID del campeon equipado (vacio para quitar equipado)"
    ),
    is_new: Optional[str] = typer.Option(None, "--is-new", help="true/false"),
    db: str = typer.Option(
        DEFAULT_DB_TARGET, "--db", help="Ruta SQLite o URL de base de datos"
    ),
) -> None:
    edit_artifact_handler(
        artifact_id=artifact_id,
        name=name,
        set_name=set_name,
        slot=slot,
        rank=rank,
        level=level,
        rarity=rarity,
        main_stat=main_stat,
        main_value=main_value,
        substats=substats,
        equipped_by=equipped_by,
        is_new=is_new,
        db=db,
    )


@app.command("list-champions")
def list_champions_command(
    champion_id: Optional[str] = typer.Option(None, "--champion-id"),
    name_contains: Optional[str] = typer.Option(None, "--name-contains"),
    role: Optional[str] = typer.Option(None, "--role"),
    rarity: Optional[str] = typer.Option(None, "--rarity"),
    db: str = typer.Option(
        DEFAULT_DB_TARGET, "--db", help="Ruta SQLite o URL de base de datos"
    ),
) -> None:
    list_champions_handler(
        champion_id=champion_id,
        name_contains=name_contains,
        role=role,
        rarity=rarity,
        db=db,
    )


@app.command("list-artifacts")
def list_artifacts_command(
    artifact_id: Optional[str] = typer.Option(None, "--artifact-id"),
    slot: Optional[str] = typer.Option(None, "--slot"),
    set_name: Optional[str] = typer.Option(None, "--set-name"),
    equipped_by: Optional[str] = typer.Option(None, "--equipped-by", help="ID del campeon equipado"),
    is_new: Optional[str] = typer.Option(None, "--is-new", help="true/false"),
    db: str = typer.Option(
        DEFAULT_DB_TARGET, "--db", help="Ruta SQLite o URL de base de datos"
    ),
) -> None:
    list_artifacts_handler(
        artifact_id=artifact_id,
        slot=slot,
        set_name=set_name,
        equipped_by=equipped_by,
        is_new=is_new,
        db=db,
    )


@app.command("recommend")
def recommend_command(
    source: str = typer.Option("db", "--source", help="Origen de datos: db o csv"),
    db: str = typer.Option(
        DEFAULT_DB_TARGET, "--db", help="Ruta SQLite o URL de base de datos"
    ),
    champions_csv: Path = typer.Option(
        Path("champions.csv"), "--champions-csv", help="CSV de campeones"
    ),
    artifacts_csv: Path = typer.Option(
        Path("artifacts.csv"), "--artifacts-csv", help="CSV de artefactos"
    ),
    sync_csv: bool = typer.Option(
        False, "--sync-csv", help="Sincroniza CSV -> DB antes de recomendar"
    ),
    top_n: int = typer.Option(
        5, "--top-n", min=1, max=20, help="Numero de recomendaciones por artefacto"
    ),
) -> None:
    recommend_handler(
        source=source,
        db=db,
        champions_csv=str(champions_csv),
        artifacts_csv=str(artifacts_csv),
        sync_csv=sync_csv,
        top_n=top_n,
    )
