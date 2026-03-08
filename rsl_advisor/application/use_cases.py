from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from rsl_advisor.domain.models import Artifact, Champion, Recommendation
from rsl_advisor.domain.scoring import (
    current_equipped_by_slot,
    evaluate_new_artifact,
    explain_artifact_fit,
)
from rsl_advisor.infrastructure.csv_io import load_artifacts_csv, load_champions_csv
from rsl_advisor.infrastructure.persistence import (
    init_db,
    load_artifacts,
    load_champions,
    save_artifacts,
    save_champions,
)


@dataclass
class ArtifactRecommendation:
    artifact: Artifact
    ranking: List[Recommendation]


def sync_csv_to_db(champions_csv: str, artifacts_csv: str, db_path: str) -> Tuple[int, int]:
    init_db(db_path)
    champions = load_champions_csv(champions_csv)
    artifacts = load_artifacts_csv(artifacts_csv)
    save_champions(champions, db_path)
    save_artifacts(artifacts, db_path)
    return len(champions), len(artifacts)


def load_data(source: str, db_path: str, champions_csv: str, artifacts_csv: str) -> Tuple[List[Champion], List[Artifact]]:
    if source == "csv":
        return load_champions_csv(champions_csv), load_artifacts_csv(artifacts_csv)

    init_db(db_path)
    return load_champions(db_path), load_artifacts(db_path)


def build_recommendations(champions: List[Champion], artifacts: List[Artifact], top_n: int) -> List[ArtifactRecommendation]:
    equipped_map = current_equipped_by_slot(artifacts)
    new_items = [artifact for artifact in artifacts if artifact.is_new]
    output: List[ArtifactRecommendation] = []

    for artifact in new_items:
        ranking = evaluate_new_artifact(artifact, champions, equipped_map, top_n=top_n)
        output.append(ArtifactRecommendation(artifact=artifact, ranking=ranking))

    return output


def recommendation_reason(champion: Champion, artifact: Artifact) -> str:
    return explain_artifact_fit(champion, artifact)


def add_champion(champion: Champion, db_path: str) -> None:
    init_db(db_path)
    save_champions([champion], db_path)


def add_artifact(artifact: Artifact, db_path: str) -> None:
    init_db(db_path)
    save_artifacts([artifact], db_path)


def edit_champion(
    champion_id: str,
    db_path: str,
    *,
    rarity: Optional[str] = None,
    role: Optional[str] = None,
    level: Optional[int] = None,
    stars: Optional[int] = None,
    hp: Optional[int] = None,
    atk: Optional[int] = None,
    defense: Optional[int] = None,
    speed: Optional[int] = None,
    crit_rate: Optional[float] = None,
    crit_damage: Optional[float] = None,
    resistance: Optional[int] = None,
    accuracy: Optional[int] = None,
    preferred_sets: Optional[List[str]] = None,
    notes: Optional[str] = None,
) -> bool:
    init_db(db_path)
    champions = load_champions(db_path)
    target = next((champ for champ in champions if champ.champion_id == champion_id), None)
    if target is None:
        return False

    updates: Dict[str, object] = {
        "rarity": rarity,
        "role": role,
        "level": level,
        "stars": stars,
        "hp": hp,
        "atk": atk,
        "defense": defense,
        "speed": speed,
        "crit_rate": crit_rate,
        "crit_damage": crit_damage,
        "resistance": resistance,
        "accuracy": accuracy,
        "preferred_sets": preferred_sets,
        "notes": notes,
    }

    for field_name, field_value in updates.items():
        if field_value is not None:
            setattr(target, field_name, field_value)

    save_champions([target], db_path)
    return True


def edit_artifact(
    artifact_id: str,
    db_path: str,
    *,
    name: Optional[str] = None,
    set_name: Optional[str] = None,
    slot: Optional[str] = None,
    rank: Optional[int] = None,
    level: Optional[int] = None,
    rarity: Optional[str] = None,
    main_stat: Optional[str] = None,
    main_value: Optional[float] = None,
    substats: Optional[Dict[str, float]] = None,
    equipped_by: Optional[str] = None,
    is_new: Optional[bool] = None,
) -> bool:
    init_db(db_path)
    artifacts = load_artifacts(db_path)
    target = next((art for art in artifacts if art.artifact_id == artifact_id), None)
    if target is None:
        return False

    updates: Dict[str, object] = {
        "name": name,
        "set_name": set_name,
        "slot": slot,
        "rank": rank,
        "level": level,
        "rarity": rarity,
        "main_stat": main_stat,
        "main_value": main_value,
        "substats": substats,
        "is_new": is_new,
    }

    for field_name, field_value in updates.items():
        if field_value is not None:
            setattr(target, field_name, field_value)

    if equipped_by is not None:
        target.equipped_by = equipped_by.strip() or None

    save_artifacts([target], db_path)
    return True


def query_champions(
    db_path: str,
    *,
    champion_id: Optional[str] = None,
    name_contains: Optional[str] = None,
    role: Optional[str] = None,
    rarity: Optional[str] = None,
) -> List[Champion]:
    init_db(db_path)
    champions = load_champions(db_path)

    champion_id_filter = champion_id.strip().lower() if champion_id else None
    name_filter = name_contains.strip().lower() if name_contains else None
    role_filter = role.strip().lower() if role else None
    rarity_filter = rarity.strip().lower() if rarity else None

    output: List[Champion] = []
    for champion in champions:
        if champion_id_filter and champion_id_filter not in champion.champion_id.lower():
            continue
        if name_filter and name_filter not in champion.name.lower():
            continue
        if role_filter and role_filter not in champion.role.lower():
            continue
        if rarity_filter and champion.rarity.lower() != rarity_filter:
            continue
        output.append(champion)
    return output


def query_artifacts(
    db_path: str,
    *,
    artifact_id: Optional[str] = None,
    slot: Optional[str] = None,
    set_name: Optional[str] = None,
    equipped_by: Optional[str] = None,
    is_new: Optional[bool] = None,
) -> List[Artifact]:
    init_db(db_path)
    artifacts = load_artifacts(db_path)

    artifact_id_filter = artifact_id.strip().lower() if artifact_id else None
    slot_filter = slot.strip().lower() if slot else None
    set_filter = set_name.strip().lower() if set_name else None
    equipped_filter = equipped_by.strip().lower() if equipped_by else None

    output: List[Artifact] = []
    for artifact in artifacts:
        if artifact_id_filter and artifact_id_filter not in artifact.artifact_id.lower():
            continue
        if slot_filter and artifact.slot.lower() != slot_filter:
            continue
        if set_filter and artifact.set_name.lower() != set_filter:
            continue
        if equipped_filter and (artifact.equipped_by or "").lower() != equipped_filter:
            continue
        if is_new is not None and artifact.is_new is not is_new:
            continue
        output.append(artifact)
    return output
