from __future__ import annotations

import os
from typing import Dict, List, Optional

from fastapi import FastAPI, Query, status

from rsl_advisor.interfaces.api_handlers.artifacts import (
    create_artifact_handler,
    list_artifacts_handler,
    read_artifact_handler,
    remove_artifact_handler,
    update_artifact_handler,
)
from rsl_advisor.interfaces.api_handlers.champions import (
    create_champion_handler,
    list_champions_handler,
    read_champion_handler,
    remove_champion_handler,
    update_champion_handler,
)
from rsl_advisor.interfaces.api_models import (
    ArtifactCreate,
    ArtifactRead,
    ArtifactUpdate,
    ChampionCreate,
    ChampionRead,
    ChampionUpdate,
)

DATABASE_TARGET = os.getenv("DATABASE_URL", "advisor.db")

app = FastAPI(title="RSL Advisor API", version="0.1.0")


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/champions", response_model=List[ChampionRead])
def list_champions(
    champion_id: Optional[str] = Query(None),
    name_contains: Optional[str] = Query(None),
    role: Optional[str] = Query(None),
    rarity: Optional[str] = Query(None),
) -> List[ChampionRead]:
    return list_champions_handler(
        DATABASE_TARGET,
        champion_id=champion_id,
        name_contains=name_contains,
        role=role,
        rarity=rarity,
    )


@app.post("/champions", response_model=ChampionRead, status_code=status.HTTP_201_CREATED)
def create_champion(payload: ChampionCreate) -> ChampionRead:
    return create_champion_handler(DATABASE_TARGET, payload)


@app.get("/champions/{champion_id}", response_model=ChampionRead)
def read_champion(champion_id: str) -> ChampionRead:
    return read_champion_handler(DATABASE_TARGET, champion_id)


@app.patch("/champions/{champion_id}", response_model=ChampionRead)
def update_champion(champion_id: str, payload: ChampionUpdate) -> ChampionRead:
    return update_champion_handler(DATABASE_TARGET, champion_id, payload)


@app.delete("/champions/{champion_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_champion(champion_id: str) -> None:
    remove_champion_handler(DATABASE_TARGET, champion_id)


@app.get("/artifacts", response_model=List[ArtifactRead])
def list_artifacts(
    artifact_id: Optional[str] = Query(None),
    slot: Optional[str] = Query(None),
    set_name: Optional[str] = Query(None),
    equipped_by: Optional[str] = Query(None),
    is_new: Optional[bool] = Query(None),
) -> List[ArtifactRead]:
    return list_artifacts_handler(
        DATABASE_TARGET,
        artifact_id=artifact_id,
        slot=slot,
        set_name=set_name,
        equipped_by=equipped_by,
        is_new=is_new,
    )


@app.post("/artifacts", response_model=ArtifactRead, status_code=status.HTTP_201_CREATED)
def create_artifact(payload: ArtifactCreate) -> ArtifactRead:
    return create_artifact_handler(DATABASE_TARGET, payload)


@app.get("/artifacts/{artifact_id}", response_model=ArtifactRead)
def read_artifact(artifact_id: str) -> ArtifactRead:
    return read_artifact_handler(DATABASE_TARGET, artifact_id)


@app.patch("/artifacts/{artifact_id}", response_model=ArtifactRead)
def update_artifact(artifact_id: str, payload: ArtifactUpdate) -> ArtifactRead:
    return update_artifact_handler(DATABASE_TARGET, artifact_id, payload)


@app.delete("/artifacts/{artifact_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_artifact(artifact_id: str) -> None:
    remove_artifact_handler(DATABASE_TARGET, artifact_id)
