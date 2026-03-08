from __future__ import annotations

from rsl_advisor.application.use_cases import sync_csv_to_db
from rsl_advisor.infrastructure.persistence import init_db

from .common import print_sync_result


def init_db_handler(db: str) -> None:
    init_db(db)


def sync_handler(champions_csv: str, artifacts_csv: str, db: str) -> None:
    champions_count, artifacts_count = sync_csv_to_db(champions_csv, artifacts_csv, db)
    print_sync_result(champions_count, artifacts_count, db)
