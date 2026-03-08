from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ChampionCreate(BaseModel):
    champion_id: str
    name: str
    rarity: str
    role: str
    level: int = Field(1, ge=1)
    stars: int = Field(1, ge=1, le=6)
    hp: int = Field(0, ge=0)
    atk: int = Field(0, ge=0)
    defense: int = Field(0, ge=0)
    speed: int = Field(0, ge=0)
    crit_rate: float = Field(0.0, ge=0.0)
    crit_damage: float = Field(0.0, ge=0.0)
    resistance: int = Field(0, ge=0)
    accuracy: int = Field(0, ge=0)
    preferred_sets: List[str] = Field(default_factory=list)
    notes: str = ""


class ChampionUpdate(BaseModel):
    rarity: Optional[str] = None
    role: Optional[str] = None
    level: Optional[int] = Field(None, ge=1)
    stars: Optional[int] = Field(None, ge=1, le=6)
    hp: Optional[int] = Field(None, ge=0)
    atk: Optional[int] = Field(None, ge=0)
    defense: Optional[int] = Field(None, ge=0)
    speed: Optional[int] = Field(None, ge=0)
    crit_rate: Optional[float] = Field(None, ge=0.0)
    crit_damage: Optional[float] = Field(None, ge=0.0)
    resistance: Optional[int] = Field(None, ge=0)
    accuracy: Optional[int] = Field(None, ge=0)
    preferred_sets: Optional[List[str]] = None
    notes: Optional[str] = None


class ChampionRead(ChampionCreate):
    pass


class ArtifactCreate(BaseModel):
    artifact_id: str
    name: str
    set_name: str
    slot: str
    rank: int = Field(0, ge=0)
    level: int = Field(0, ge=0)
    rarity: str = ""
    main_stat: str
    main_value: float = 0.0
    substats: Dict[str, float] = Field(default_factory=dict)
    equipped_by: Optional[str] = None
    is_new: bool = False


class ArtifactUpdate(BaseModel):
    name: Optional[str] = None
    set_name: Optional[str] = None
    slot: Optional[str] = None
    rank: Optional[int] = Field(None, ge=0)
    level: Optional[int] = Field(None, ge=0)
    rarity: Optional[str] = None
    main_stat: Optional[str] = None
    main_value: Optional[float] = None
    substats: Optional[Dict[str, float]] = None
    equipped_by: Optional[str] = None
    is_new: Optional[bool] = None


class ArtifactRead(ArtifactCreate):
    pass
