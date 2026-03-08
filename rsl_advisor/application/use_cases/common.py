from __future__ import annotations

from typing import Any, Dict

from rsl_advisor.infrastructure.persistence import init_db


def ensure_db(db_target: str) -> None:
    init_db(db_target)


def apply_updates(target: Any, updates: Dict[str, object]) -> None:
    for field_name, field_value in updates.items():
        if field_value is not None:
            setattr(target, field_name, field_value)
