from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional


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
