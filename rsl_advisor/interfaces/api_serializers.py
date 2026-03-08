from __future__ import annotations

from typing import Dict

from rsl_advisor.domain.models import Artifact, Champion
from rsl_advisor.domain.scoring import normalise_stat_name
from rsl_advisor.interfaces.api_models import ArtifactRead, ChampionRead


def normalise_substats(substats: Dict[str, float]) -> Dict[str, float]:
    return {normalise_stat_name(stat): float(value) for stat, value in substats.items()}


def champion_to_read(champion: Champion) -> ChampionRead:
    return ChampionRead(
        champion_id=champion.champion_id,
        name=champion.name,
        rarity=champion.rarity,
        role=champion.role,
        level=champion.level,
        stars=champion.stars,
        hp=champion.hp,
        atk=champion.atk,
        defense=champion.defense,
        speed=champion.speed,
        crit_rate=champion.crit_rate,
        crit_damage=champion.crit_damage,
        resistance=champion.resistance,
        accuracy=champion.accuracy,
        preferred_sets=champion.preferred_sets,
        notes=champion.notes,
    )


def artifact_to_read(artifact: Artifact) -> ArtifactRead:
    return ArtifactRead(
        artifact_id=artifact.artifact_id,
        name=artifact.name,
        set_name=artifact.set_name,
        slot=artifact.slot,
        rank=artifact.rank,
        level=artifact.level,
        rarity=artifact.rarity,
        main_stat=artifact.main_stat,
        main_value=artifact.main_value,
        substats=artifact.substats,
        equipped_by=artifact.equipped_by,
        is_new=artifact.is_new,
    )
