from __future__ import annotations

import typer

from rsl_advisor.application.use_cases import add_artifact, edit_artifact, query_artifacts
from rsl_advisor.domain.models import Artifact
from rsl_advisor.domain.scoring import normalise_stat_name
from rsl_advisor.infrastructure.csv_io import parse_substats

from .common import format_substats, parse_optional_bool


def add_artifact_handler(
    artifact_id: str,
    name: str,
    set_name: str,
    slot: str,
    rank: int,
    level: int,
    rarity: str,
    main_stat: str,
    main_value: float,
    substats: str,
    equipped_by: str,
    is_new: bool,
    db: str,
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


def edit_artifact_handler(
    artifact_id: str,
    name: str | None,
    set_name: str | None,
    slot: str | None,
    rank: int | None,
    level: int | None,
    rarity: str | None,
    main_stat: str | None,
    main_value: float | None,
    substats: str | None,
    equipped_by: str | None,
    is_new: str | None,
    db: str,
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
        is_new=parse_optional_bool(is_new, "--is-new"),
    )
    if not updated:
        typer.echo(f"No existe artefacto con id: {artifact_id}")
        raise typer.Exit(code=1)
    typer.echo(f"Artefacto actualizado: {artifact_id}")


def list_artifacts_handler(
    artifact_id: str | None,
    slot: str | None,
    set_name: str | None,
    equipped_by: str | None,
    is_new: str | None,
    db: str,
) -> None:
    artifacts = query_artifacts(
        db,
        artifact_id=artifact_id,
        slot=slot,
        set_name=set_name,
        equipped_by=equipped_by,
        is_new=parse_optional_bool(is_new, "--is-new"),
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
            f"substats={format_substats(artifact.substats)} | equipped_by={equipped} | "
            f"is_new={artifact.is_new}"
        )
