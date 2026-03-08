from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Champion:
    champion_id: str
    name: str
    rarity: str
    role: str
    level: int
    stars: int
    hp: int
    atk: int
    defense: int
    speed: int
    crit_rate: float
    crit_damage: float
    resistance: int
    accuracy: int
    preferred_sets: List[str] = field(default_factory=list)
    notes: str = ""


@dataclass
class Artifact:
    artifact_id: str
    name: str
    set_name: str
    slot: str
    rank: int
    level: int
    rarity: str
    main_stat: str
    main_value: float
    substats: Dict[str, float]
    equipped_by: Optional[str] = None
    is_new: bool = False


@dataclass
class Recommendation:
    champion_id: str
    champion_name: str
    role: str
    new_score: float
    current_score: float
    delta: float
    current_item: Optional[str] = None
