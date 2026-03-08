from __future__ import annotations

import typer

from rsl_advisor.application.use_cases import add_champion, edit_champion, query_champions
from rsl_advisor.domain.models import Champion

from .common import parse_pipe_values


def add_champion_handler(
    champion_id: str,
    name: str,
    rarity: str,
    role: str,
    level: int,
    stars: int,
    hp: int,
    atk: int,
    defense: int,
    speed: int,
    crit_rate: float,
    crit_damage: float,
    resistance: int,
    accuracy: int,
    preferred_sets: str,
    notes: str,
    db: str,
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
        preferred_sets=parse_pipe_values(preferred_sets),
        notes=notes,
    )
    add_champion(champion, db)
    typer.echo(f"Campeon guardado: {champion_id} ({name})")


def edit_champion_handler(
    champion_id: str,
    rarity: str | None,
    role: str | None,
    level: int | None,
    stars: int | None,
    hp: int | None,
    atk: int | None,
    defense: int | None,
    speed: int | None,
    crit_rate: float | None,
    crit_damage: float | None,
    resistance: int | None,
    accuracy: int | None,
    preferred_sets: str | None,
    notes: str | None,
    db: str,
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
        preferred_sets=parse_pipe_values(preferred_sets) if preferred_sets is not None else None,
        notes=notes,
    )
    if not updated:
        typer.echo(f"No existe campeon con id: {champion_id}")
        raise typer.Exit(code=1)
    typer.echo(f"Campeon actualizado: {champion_id}")


def list_champions_handler(
    champion_id: str | None,
    name_contains: str | None,
    role: str | None,
    rarity: str | None,
    db: str,
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
