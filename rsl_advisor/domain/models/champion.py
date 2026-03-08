from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


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
