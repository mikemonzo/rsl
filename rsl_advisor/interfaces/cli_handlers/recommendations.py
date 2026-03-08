from __future__ import annotations

import typer

from rsl_advisor.application.use_cases import (
    build_recommendations,
    load_data,
    recommendation_reason,
    sync_csv_to_db,
)

from .common import print_sync_result, validate_source


def recommend_handler(
    source: str,
    db: str,
    champions_csv: str,
    artifacts_csv: str,
    sync_csv: bool,
    top_n: int,
) -> None:
    source_value = validate_source(source)

    if sync_csv:
        champions_count, artifacts_count = sync_csv_to_db(champions_csv, artifacts_csv, db)
        print_sync_result(champions_count, artifacts_count, db)

    champions, artifacts = load_data(source_value, db, champions_csv, artifacts_csv)

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
