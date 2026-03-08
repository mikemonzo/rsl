from __future__ import annotations

from typing import Dict, List, Optional

from rsl_advisor.domain.models import Champion
from rsl_advisor.infrastructure.persistence import (
    delete_champion as delete_champion_repo,
    get_champion as get_champion_repo,
    load_champions,
    save_champions,
)

from .common import apply_updates, ensure_db


def add_champion(champion: Champion, db_path: str) -> None:
    ensure_db(db_path)
    save_champions([champion], db_path)


def get_champion(champion_id: str, db_path: str) -> Optional[Champion]:
    ensure_db(db_path)
    return get_champion_repo(db_path, champion_id)


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
    target = get_champion(champion_id, db_path)
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

    apply_updates(target, updates)

    save_champions([target], db_path)
    return True


def delete_champion(champion_id: str, db_path: str) -> bool:
    ensure_db(db_path)
    return delete_champion_repo(db_path, champion_id)


def query_champions(
    db_path: str,
    *,
    champion_id: Optional[str] = None,
    name_contains: Optional[str] = None,
    role: Optional[str] = None,
    rarity: Optional[str] = None,
) -> List[Champion]:
    ensure_db(db_path)
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
