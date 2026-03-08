from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class Recommendation:
    champion_id: str
    champion_name: str
    role: str
    new_score: float
    current_score: float
    delta: float
    current_item: Optional[str] = None
