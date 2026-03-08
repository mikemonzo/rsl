from __future__ import annotations

import csv
from typing import Dict, List

from rsl_advisor.domain.models import Artifact, Champion
from rsl_advisor.domain.scoring import normalise_stat_name


def parse_substats(raw: str) -> Dict[str, float]:
    if not raw.strip():
        return {}

    result: Dict[str, float] = {}
    for part in raw.split("|"):
        if ":" not in part:
            continue
        stat, value = part.split(":", 1)
        try:
            result[normalise_stat_name(stat)] = float(value.strip())
        except ValueError:
            continue
    return result


def load_champions_csv(path: str) -> List[Champion]:
    champions: List[Champion] = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            preferred_sets = [s.strip() for s in row.get("preferred_sets", "").split("|") if s.strip()]
            champions.append(
                Champion(
                    name=row["name"],
                    rarity=row.get("rarity", ""),
                    role=row.get("role", ""),
                    level=int(row.get("level", 1)),
                    stars=int(row.get("stars", 1)),
                    hp=int(row.get("hp", 0)),
                    atk=int(row.get("atk", 0)),
                    defense=int(row.get("defense", 0)),
                    speed=int(row.get("speed", 0)),
                    crit_rate=float(row.get("crit_rate", 0)),
                    crit_damage=float(row.get("crit_damage", 0)),
                    resistance=int(row.get("resistance", 0)),
                    accuracy=int(row.get("accuracy", 0)),
                    preferred_sets=preferred_sets,
                    notes=row.get("notes", ""),
                )
            )
    return champions


def load_artifacts_csv(path: str) -> List[Artifact]:
    artifacts: List[Artifact] = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            artifacts.append(
                Artifact(
                    artifact_id=row["artifact_id"],
                    name=row.get("name", row["artifact_id"]),
                    set_name=row.get("set_name", ""),
                    slot=row["slot"],
                    rank=int(row.get("rank", 0)),
                    level=int(row.get("level", 0)),
                    rarity=row.get("rarity", ""),
                    main_stat=normalise_stat_name(row.get("main_stat", "")),
                    main_value=float(row.get("main_value", 0)),
                    substats=parse_substats(row.get("substats", "")),
                    equipped_by=row.get("equipped_by") or None,
                    is_new=str(row.get("is_new", "false")).strip().lower() == "true",
                )
            )
    return artifacts
