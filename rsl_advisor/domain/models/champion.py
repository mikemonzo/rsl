
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class StatBlock:
    hp: int = 0
    atk: int = 0
    defense: int = 0
    speed: int = 0
    crit_rate: float = 0.0
    crit_damage: float = 0.0
    resistance: int = 0
    accuracy: int = 0


@dataclass(frozen=True)
class SkillEffect:
    effect_type: str = ""
    target: str = ""
    value: float = 0.0
    duration: Optional[int] = None
    chance: Optional[float] = None
    condition: str = ""
    notes: str = ""


@dataclass(frozen=True)
class Skill:
    skill_id: str = ""
    name: str = ""
    description: str = ""
    skill_type: str = ""
    cooldown: Optional[int] = None
    booked_cooldown: Optional[int] = None
    effects: list[SkillEffect] = field(default_factory=list)
    books_required: int = 0
    is_passive: bool = False
    is_default: bool = False


@dataclass(frozen=True)
class Aura:
    stat: str = ""
    value: float = 0.0
    scope: str = ""
    area: str = ""


@dataclass(frozen=True)
class Blessing:
    name: str = ""
    level: int = 0
    description: str = ""


@dataclass(frozen=True)
class Relic:
    relic_id: str = ""
    name: str = ""
    rarity: str = ""
    level: int = 0
    effect: str = ""


@dataclass(frozen=True)
class Mastery:
    mastery_id: str = ""
    name: str = ""
    tree: str = ""
    tier: int = 0
    description: str = ""
    unlocked: bool = False


@dataclass(frozen=True)
class ArtifactRef:
    artifact_id: str
    slot: str
    set_name: str = ""
    equipped: bool = True


@dataclass(frozen=True)
class ChampionProgression:
    level: int = 1
    stars: int = 1
    ascension_level: int = 0
    awaken_level: int = 0
    power: Optional[int] = None
    booked: bool = False


@dataclass(frozen=True)
class ChampionFlags:
    is_locked: bool = False
    is_favorite: bool = False
    is_vaulted: bool = False
    is_food: bool = False


@dataclass
class Champion:
    champion_id: str
    name: str
    rarity: str
    faction: str = ""
    affinity: str = ""
    roles: list[str] = field(default_factory=list)
    primary_role: str = ""
    priority: Optional[int] = None
    progression: ChampionProgression = field(default_factory=ChampionProgression)
    base_stats: StatBlock = field(default_factory=StatBlock)
    total_stats: StatBlock = field(default_factory=StatBlock)
    artifacts: list[ArtifactRef] = field(default_factory=list)
    relic: Optional[Relic] = None
    skills: list[Skill] = field(default_factory=list)
    aura: Optional[Aura] = None
    blessing: Optional[Blessing] = None
    masteries: list[Mastery] = field(default_factory=list)
    set_list: list[str] = field(default_factory=list)
    preferred_sets: list[str] = field(default_factory=list)
    content_tags: list[str] = field(default_factory=list)
    flags: ChampionFlags = field(default_factory=ChampionFlags)
    notes: str = ""

    @property
    def level(self) -> int:
        return self.progression.level

    @property
    def stars(self) -> int:
        return self.progression.stars

    @property
    def power(self) -> Optional[int]:
        return self.progression.power
