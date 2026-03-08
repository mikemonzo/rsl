from __future__ import annotations

import json

from rsl_advisor.domain.models import Artifact, Champion
from rsl_advisor.domain.scoring import normalise_stat_name

from .tables import ArtifactDB, ChampionDB


def champion_to_db(champion: Champion) -> ChampionDB:
    return ChampionDB(
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
        preferred_sets_json=json.dumps(champion.preferred_sets, ensure_ascii=True),
        notes=champion.notes,
    )


def champion_from_db(row: ChampionDB) -> Champion:
    return Champion(
        champion_id=row.champion_id,
        name=row.name,
        rarity=row.rarity,
        role=row.role,
        level=row.level,
        stars=row.stars,
        hp=row.hp,
        atk=row.atk,
        defense=row.defense,
        speed=row.speed,
        crit_rate=row.crit_rate,
        crit_damage=row.crit_damage,
        resistance=row.resistance,
        accuracy=row.accuracy,
        preferred_sets=json.loads(row.preferred_sets_json) if row.preferred_sets_json else [],
        notes=row.notes,
    )


def artifact_to_db(artifact: Artifact) -> ArtifactDB:
    return ArtifactDB(
        artifact_id=artifact.artifact_id,
        name=artifact.name,
        set_name=artifact.set_name,
        slot=artifact.slot,
        rank=artifact.rank,
        level=artifact.level,
        rarity=artifact.rarity,
        main_stat=normalise_stat_name(artifact.main_stat),
        main_value=artifact.main_value,
        substats_json=json.dumps(artifact.substats, ensure_ascii=True),
        equipped_by=artifact.equipped_by,
        is_new=artifact.is_new,
    )


def artifact_from_db(row: ArtifactDB) -> Artifact:
    substats_raw = json.loads(row.substats_json) if row.substats_json else {}
    substats = {normalise_stat_name(k): float(v) for k, v in substats_raw.items()}
    return Artifact(
        artifact_id=row.artifact_id,
        name=row.name,
        set_name=row.set_name,
        slot=row.slot,
        rank=row.rank,
        level=row.level,
        rarity=row.rarity,
        main_stat=normalise_stat_name(row.main_stat),
        main_value=row.main_value,
        substats=substats,
        equipped_by=row.equipped_by,
        is_new=row.is_new,
    )
