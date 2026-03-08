from __future__ import annotations

from typing import Optional

from sqlmodel import Field, SQLModel


class ChampionDB(SQLModel, table=True):
    __tablename__ = "champions"

    champion_id: str = Field(primary_key=True)
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
    preferred_sets_json: str = Field(default="[]")
    notes: str = Field(default="")


class ArtifactDB(SQLModel, table=True):
    __tablename__ = "artifacts"

    artifact_id: str = Field(primary_key=True)
    name: str
    set_name: str
    slot: str
    rank: int
    level: int
    rarity: str
    main_stat: str
    main_value: float
    substats_json: str = Field(default="{}")
    equipped_by: Optional[str] = Field(default=None)
    is_new: bool = Field(default=False)
