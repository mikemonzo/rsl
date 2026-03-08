from __future__ import annotations

from typing import List, Tuple

from rsl_advisor.domain.models import Artifact, Champion
from rsl_advisor.infrastructure.csv_io import load_artifacts_csv, load_champions_csv
from rsl_advisor.infrastructure.persistence import load_artifacts, load_champions, save_artifacts, save_champions

from .common import ensure_db


def sync_csv_to_db(champions_csv: str, artifacts_csv: str, db_path: str) -> Tuple[int, int]:
    ensure_db(db_path)
    champions = load_champions_csv(champions_csv)
    artifacts = load_artifacts_csv(artifacts_csv)
    save_champions(champions, db_path)
    save_artifacts(artifacts, db_path)
    return len(champions), len(artifacts)


def load_data(source: str, db_path: str, champions_csv: str, artifacts_csv: str) -> Tuple[List[Champion], List[Artifact]]:
    if source == "csv":
        return load_champions_csv(champions_csv), load_artifacts_csv(artifacts_csv)

    ensure_db(db_path)
    return load_champions(db_path), load_artifacts(db_path)
