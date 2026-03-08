from __future__ import annotations

import json
import sqlite3
from typing import List, Optional

from sqlmodel import Field, SQLModel, Session, create_engine, select

from rsl_advisor.domain.models import Artifact, Champion
from rsl_advisor.domain.scoring import normalise_stat_name


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


REQUIRED_DB_COLUMNS = {
    "champions": {
        "champion_id",
        "name",
        "rarity",
        "role",
        "level",
        "stars",
        "hp",
        "atk",
        "defense",
        "speed",
        "crit_rate",
        "crit_damage",
        "resistance",
        "accuracy",
        "preferred_sets_json",
        "notes",
    },
    "artifacts": {
        "artifact_id",
        "name",
        "set_name",
        "slot",
        "rank",
        "level",
        "rarity",
        "main_stat",
        "main_value",
        "substats_json",
        "equipped_by",
        "is_new",
    },
}


def get_engine(db_path: str):
    return create_engine(f"sqlite:///{db_path}", echo=False)


def _drop_legacy_tables_if_needed(db_path: str) -> None:
    with sqlite3.connect(db_path) as conn:
        for table, required in REQUIRED_DB_COLUMNS.items():
            cols = {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}
            if cols and not required.issubset(cols):
                conn.execute(f"DROP TABLE IF EXISTS {table}")
        conn.commit()


def init_db(db_path: str) -> None:
    _drop_legacy_tables_if_needed(db_path)
    SQLModel.metadata.create_all(get_engine(db_path))


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


def save_champions(champions: List[Champion], db_path: str) -> None:
    with Session(get_engine(db_path)) as session:
        for champion in champions:
            session.merge(champion_to_db(champion))
        session.commit()


def save_artifacts(artifacts: List[Artifact], db_path: str) -> None:
    with Session(get_engine(db_path)) as session:
        for artifact in artifacts:
            session.merge(artifact_to_db(artifact))
        session.commit()


def load_champions(db_path: str) -> List[Champion]:
    with Session(get_engine(db_path)) as session:
        rows = session.exec(select(ChampionDB).order_by(ChampionDB.name, ChampionDB.champion_id)).all()
    return [champion_from_db(row) for row in rows]


def load_artifacts(db_path: str) -> List[Artifact]:
    with Session(get_engine(db_path)) as session:
        rows = session.exec(select(ArtifactDB).order_by(ArtifactDB.artifact_id)).all()
    return [artifact_from_db(row) for row in rows]
