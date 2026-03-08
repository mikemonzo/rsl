from __future__ import annotations

from typing import List, Optional

from sqlmodel import Session, select

from rsl_advisor.domain.models import Artifact

from .db import get_engine
from .mappers import artifact_from_db, artifact_to_db
from .tables import ArtifactDB


def save_artifacts(artifacts: List[Artifact], db_target: str) -> None:
    with Session(get_engine(db_target)) as session:
        for artifact in artifacts:
            session.merge(artifact_to_db(artifact))
        session.commit()


def load_artifacts(db_target: str) -> List[Artifact]:
    with Session(get_engine(db_target)) as session:
        rows = session.exec(select(ArtifactDB).order_by(ArtifactDB.artifact_id)).all()
    return [artifact_from_db(row) for row in rows]


def get_artifact(db_target: str, artifact_id: str) -> Optional[Artifact]:
    with Session(get_engine(db_target)) as session:
        row = session.get(ArtifactDB, artifact_id)
    if row is None:
        return None
    return artifact_from_db(row)


def delete_artifact(db_target: str, artifact_id: str) -> bool:
    with Session(get_engine(db_target)) as session:
        row = session.get(ArtifactDB, artifact_id)
        if row is None:
            return False
        session.delete(row)
        session.commit()
    return True
