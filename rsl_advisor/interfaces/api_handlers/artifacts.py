from __future__ import annotations

from typing import List, Optional

from fastapi import HTTPException

from rsl_advisor.application.use_cases import (
    add_artifact,
    delete_artifact,
    edit_artifact,
    get_artifact,
    query_artifacts,
)
from rsl_advisor.domain.models import Artifact
from rsl_advisor.domain.scoring import normalise_stat_name
from rsl_advisor.interfaces.api_models import ArtifactCreate, ArtifactRead, ArtifactUpdate
from rsl_advisor.interfaces.api_serializers import artifact_to_read, normalise_substats


def require_artifact(artifact_id: str, db_target: str) -> Artifact:
    artifact = get_artifact(artifact_id, db_target)
    if artifact is None:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return artifact


def list_artifacts_handler(
    db_target: str,
    *,
    artifact_id: Optional[str],
    slot: Optional[str],
    set_name: Optional[str],
    equipped_by: Optional[str],
    is_new: Optional[bool],
) -> List[ArtifactRead]:
    artifacts = query_artifacts(
        db_target,
        artifact_id=artifact_id,
        slot=slot,
        set_name=set_name,
        equipped_by=equipped_by,
        is_new=is_new,
    )
    return [artifact_to_read(artifact) for artifact in artifacts]


def create_artifact_handler(db_target: str, payload: ArtifactCreate) -> ArtifactRead:
    data = payload.model_dump()
    data["main_stat"] = normalise_stat_name(data["main_stat"])
    data["substats"] = normalise_substats(data["substats"])
    artifact = Artifact(**data)
    add_artifact(artifact, db_target)
    return artifact_to_read(artifact)


def read_artifact_handler(db_target: str, artifact_id: str) -> ArtifactRead:
    return artifact_to_read(require_artifact(artifact_id, db_target))


def update_artifact_handler(db_target: str, artifact_id: str, payload: ArtifactUpdate) -> ArtifactRead:
    updates = payload.model_dump(exclude_unset=True)
    if "main_stat" in updates and updates["main_stat"] is not None:
        updates["main_stat"] = normalise_stat_name(updates["main_stat"])
    if "substats" in updates and updates["substats"] is not None:
        updates["substats"] = normalise_substats(updates["substats"])

    updated = edit_artifact(artifact_id, db_target, **updates)
    if not updated:
        raise HTTPException(status_code=404, detail="Artifact not found")

    return artifact_to_read(require_artifact(artifact_id, db_target))


def remove_artifact_handler(db_target: str, artifact_id: str) -> None:
    removed = delete_artifact(artifact_id, db_target)
    if not removed:
        raise HTTPException(status_code=404, detail="Artifact not found")
