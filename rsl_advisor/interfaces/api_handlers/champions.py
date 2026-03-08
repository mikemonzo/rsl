from __future__ import annotations

from typing import List, Optional

from fastapi import HTTPException

from rsl_advisor.application.use_cases import (
    add_champion,
    delete_champion,
    edit_champion,
    get_champion,
    query_champions,
)
from rsl_advisor.domain.models import Champion
from rsl_advisor.interfaces.api_models import ChampionCreate, ChampionRead, ChampionUpdate
from rsl_advisor.interfaces.api_serializers import champion_to_read


def require_champion(champion_id: str, db_target: str) -> Champion:
    champion = get_champion(champion_id, db_target)
    if champion is None:
        raise HTTPException(status_code=404, detail="Champion not found")
    return champion


def list_champions_handler(
    db_target: str,
    *,
    champion_id: Optional[str],
    name_contains: Optional[str],
    role: Optional[str],
    rarity: Optional[str],
) -> List[ChampionRead]:
    champions = query_champions(
        db_target,
        champion_id=champion_id,
        name_contains=name_contains,
        role=role,
        rarity=rarity,
    )
    return [champion_to_read(champion) for champion in champions]


def create_champion_handler(db_target: str, payload: ChampionCreate) -> ChampionRead:
    champion = Champion(**payload.model_dump())
    add_champion(champion, db_target)
    return champion_to_read(champion)


def read_champion_handler(db_target: str, champion_id: str) -> ChampionRead:
    return champion_to_read(require_champion(champion_id, db_target))


def update_champion_handler(db_target: str, champion_id: str, payload: ChampionUpdate) -> ChampionRead:
    updated = edit_champion(champion_id, db_target, **payload.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Champion not found")
    return champion_to_read(require_champion(champion_id, db_target))


def remove_champion_handler(db_target: str, champion_id: str) -> None:
    removed = delete_champion(champion_id, db_target)
    if not removed:
        raise HTTPException(status_code=404, detail="Champion not found")
