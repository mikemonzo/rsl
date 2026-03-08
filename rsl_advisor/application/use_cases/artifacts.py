from __future__ import annotations

from typing import Dict, List, Optional

from rsl_advisor.domain.models import Artifact
from rsl_advisor.infrastructure.persistence import (
    delete_artifact as delete_artifact_repo,
    get_artifact as get_artifact_repo,
    load_artifacts,
    save_artifacts,
)

from .common import apply_updates, ensure_db


def add_artifact(artifact: Artifact, db_path: str) -> None:
    ensure_db(db_path)
    save_artifacts([artifact], db_path)


def get_artifact(artifact_id: str, db_path: str) -> Optional[Artifact]:
    ensure_db(db_path)
    return get_artifact_repo(db_path, artifact_id)


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
    target = get_artifact(artifact_id, db_path)
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

    apply_updates(target, updates)

    if equipped_by is not None:
        target.equipped_by = equipped_by.strip() or None

    save_artifacts([target], db_path)
    return True


def delete_artifact(artifact_id: str, db_path: str) -> bool:
    ensure_db(db_path)
    return delete_artifact_repo(db_path, artifact_id)


def query_artifacts(
    db_path: str,
    *,
    artifact_id: Optional[str] = None,
    slot: Optional[str] = None,
    set_name: Optional[str] = None,
    equipped_by: Optional[str] = None,
    is_new: Optional[bool] = None,
) -> List[Artifact]:
    ensure_db(db_path)
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
