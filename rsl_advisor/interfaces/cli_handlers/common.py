from __future__ import annotations

from typing import Optional

import typer


def validate_source(source: str) -> str:
    source_value = source.lower().strip()
    if source_value not in {"db", "csv"}:
        raise typer.BadParameter("--source debe ser 'db' o 'csv'.")
    return source_value


def print_sync_result(champions_count: int, artifacts_count: int, db: str) -> None:
    typer.echo(
        f"Sincronizacion completada: {champions_count} campeones y "
        f"{artifacts_count} artefactos guardados en {db}"
    )


def parse_pipe_values(raw: str) -> list[str]:
    return [value.strip() for value in raw.split("|") if value.strip()]


def parse_optional_bool(raw: Optional[str], option_name: str) -> Optional[bool]:
    if raw is None:
        return None
    value = raw.strip().lower()
    if value in {"true", "1", "yes", "y"}:
        return True
    if value in {"false", "0", "no", "n"}:
        return False
    raise typer.BadParameter(f"{option_name} debe ser true o false.")


def format_substats(substats: dict[str, float]) -> str:
    if not substats:
        return "-"
    return "|".join(f"{stat}:{value:g}" for stat, value in substats.items())
