from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import typer

from rsl_advisor.application.use_cases import (
    add_artifact,
    add_champion,
    build_recommendations,
    edit_artifact,
    edit_champion,
    load_data,
    recommendation_reason,
    query_artifacts,
    query_champions,
    sync_csv_to_db,
)
from rsl_advisor.domain.models import Artifact, Champion
from rsl_advisor.domain.scoring import normalise_stat_name
from rsl_advisor.infrastructure.csv_io import parse_substats
from rsl_advisor.infrastructure.persistence import init_db

app = typer.Typer(add_completion=False, no_args_is_help=True)
DEFAULT_DB_TARGET = os.getenv("DATABASE_URL", "advisor.db")


def _validate_source(source: str) -> str:
    source_value = source.lower().strip()
    if source_value not in {"db", "csv"}:
        raise typer.BadParameter("--source debe ser 'db' o 'csv'.")
    return source_value


def _print_sync_result(champions_count: int, artifacts_count: int, db: str) -> None:
    typer.echo(
        f"Sincronizacion completada: {champions_count} campeones y "
        f"{artifacts_count} artefactos guardados en {db}"
    )


def _parse_pipe_values(raw: str) -> list[str]:
    return [value.strip() for value in raw.split("|") if value.strip()]


def _parse_optional_bool(raw: Optional[str], option_name: str) -> Optional[bool]:
    if raw is None:
        return None
    value = raw.strip().lower()
    if value in {"true", "1", "yes", "y"}:
        return True
    if value in {"false", "0", "no", "n"}:
        return False
    raise typer.BadParameter(f"{option_name} debe ser true o false.")


def _fmt_substats(substats: dict[str, float]) -> str:
    if not substats:
        return "-"
    return "|".join(f"{stat}:{value:g}" for stat, value in substats.items())


@app.command("init-db")
def init_db_command(
    db: str = typer.Option(
        DEFAULT_DB_TARGET, "--db", help="Ruta SQLite o URL de base de datos"
    ),
) -> None:
    init_db(db)
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
    champions_count, artifacts_count = sync_csv_to_db(
        str(champions_csv), str(artifacts_csv), db
    )
    _print_sync_result(champions_count, artifacts_count, db)


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
    champion = Champion(
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
        preferred_sets=_parse_pipe_values(preferred_sets),
        notes=notes,
    )
    add_champion(champion, db)
    typer.echo(f"Campeon guardado: {champion_id} ({name})")


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
    artifact = Artifact(
        artifact_id=artifact_id,
        name=name,
        set_name=set_name,
        slot=slot,
        rank=rank,
        level=level,
        rarity=rarity,
        main_stat=normalise_stat_name(main_stat),
        main_value=main_value,
        substats=parse_substats(substats),
        equipped_by=equipped_by.strip() or None,
        is_new=is_new,
    )
    add_artifact(artifact, db)
    typer.echo(f"Artefacto guardado: {artifact_id}")


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
    updated = edit_champion(
        champion_id,
        db,
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
        preferred_sets=_parse_pipe_values(preferred_sets) if preferred_sets is not None else None,
        notes=notes,
    )
    if not updated:
        typer.echo(f"No existe campeon con id: {champion_id}")
        raise typer.Exit(code=1)
    typer.echo(f"Campeon actualizado: {champion_id}")


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
    updated = edit_artifact(
        artifact_id,
        db,
        name=name,
        set_name=set_name,
        slot=slot,
        rank=rank,
        level=level,
        rarity=rarity,
        main_stat=normalise_stat_name(main_stat) if main_stat is not None else None,
        main_value=main_value,
        substats=parse_substats(substats) if substats is not None else None,
        equipped_by=equipped_by,
        is_new=_parse_optional_bool(is_new, "--is-new"),
    )
    if not updated:
        typer.echo(f"No existe artefacto con id: {artifact_id}")
        raise typer.Exit(code=1)
    typer.echo(f"Artefacto actualizado: {artifact_id}")


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
    champions = query_champions(
        db, champion_id=champion_id, name_contains=name_contains, role=role, rarity=rarity
    )
    if not champions:
        typer.echo("No se encontraron campeones.")
        return

    typer.echo(f"Campeones encontrados: {len(champions)}")
    for champion in champions:
        preferred_sets = "|".join(champion.preferred_sets) if champion.preferred_sets else "-"
        typer.echo(
            f"- {champion.champion_id} | {champion.name} | rarity={champion.rarity} | role={champion.role} | "
            f"lvl={champion.level} | stars={champion.stars} | sets={preferred_sets}"
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
    artifacts = query_artifacts(
        db,
        artifact_id=artifact_id,
        slot=slot,
        set_name=set_name,
        equipped_by=equipped_by,
        is_new=_parse_optional_bool(is_new, "--is-new"),
    )
    if not artifacts:
        typer.echo("No se encontraron artefactos.")
        return

    typer.echo(f"Artefactos encontrados: {len(artifacts)}")
    for artifact in artifacts:
        equipped = artifact.equipped_by or "-"
        typer.echo(
            f"- {artifact.artifact_id} | {artifact.name} | set={artifact.set_name} | "
            f"slot={artifact.slot} | main={artifact.main_stat} {artifact.main_value:g} | "
            f"substats={_fmt_substats(artifact.substats)} | equipped_by={equipped} | "
            f"is_new={artifact.is_new}"
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
    source_value = _validate_source(source)

    if sync_csv:
        champions_count, artifacts_count = sync_csv_to_db(
            str(champions_csv), str(artifacts_csv), db
        )
        _print_sync_result(champions_count, artifacts_count, db)

    champions, artifacts = load_data(
        source_value, db, str(champions_csv), str(artifacts_csv)
    )

    if not champions or not artifacts:
        typer.echo(
            "No hay datos suficientes para evaluar. "
            "Usa 'sync' o --sync-csv para cargar CSV en la base de datos."
        )
        raise typer.Exit(code=1)

    champions_by_id = {champion.champion_id: champion for champion in champions}
    recommendation_groups = build_recommendations(champions, artifacts, top_n=top_n)

    if not recommendation_groups:
        typer.echo("No hay artefactos marcados como nuevos (is_new=true).")
        return

    for group in recommendation_groups:
        artifact = group.artifact
        typer.echo("=" * 90)
        typer.echo(
            f"ARTEFACTO: {artifact.name} | set={artifact.set_name} | slot={artifact.slot} | "
            f"main={artifact.main_stat} {artifact.main_value} | substats={artifact.substats}"
        )

        for idx, row in enumerate(group.ranking, start=1):
            champion = champions_by_id.get(row.champion_id)
            if champion is None:
                continue
            reason = recommendation_reason(champion, artifact)
            current_desc = row.current_item or "sin artefacto equipado en ese slot"
            typer.echo(
                f"{idx}. {row.champion_name} [{row.champion_id}] ({row.role}) -> nuevo={row.new_score} | "
                f"actual={row.current_score} | mejora={row.delta} | actual={current_desc}"
            )
            typer.echo(f"   Motivo: {reason}")
        typer.echo("")
