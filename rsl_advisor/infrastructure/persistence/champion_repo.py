from __future__ import annotations

from typing import List, Optional

from sqlmodel import Session, select

from rsl_advisor.domain.models import Champion

from .db import get_engine
from .mappers import champion_from_db, champion_to_db
from .tables import ChampionDB


def save_champions(champions: List[Champion], db_target: str) -> None:
    with Session(get_engine(db_target)) as session:
        for champion in champions:
            session.merge(champion_to_db(champion))
        session.commit()


def load_champions(db_target: str) -> List[Champion]:
    with Session(get_engine(db_target)) as session:
        rows = session.exec(select(ChampionDB).order_by(ChampionDB.name, ChampionDB.champion_id)).all()
    return [champion_from_db(row) for row in rows]


def get_champion(db_target: str, champion_id: str) -> Optional[Champion]:
    with Session(get_engine(db_target)) as session:
        row = session.get(ChampionDB, champion_id)
    if row is None:
        return None
    return champion_from_db(row)


def delete_champion(db_target: str, champion_id: str) -> bool:
    with Session(get_engine(db_target)) as session:
        row = session.get(ChampionDB, champion_id)
        if row is None:
            return False
        session.delete(row)
        session.commit()
    return True
