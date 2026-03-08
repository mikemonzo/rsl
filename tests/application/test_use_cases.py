from pathlib import Path

from rsl_advisor.application.use_cases import (
    add_artifact,
    add_champion,
    build_recommendations,
    edit_artifact,
    edit_champion,
    load_data,
    query_artifacts,
    query_champions,
    sync_csv_to_db,
)
from rsl_advisor.domain.models import Artifact, Champion


CHAMPIONS_CSV = """champion_id,name,rarity,role,level,stars,hp,atk,defense,speed,crit_rate,crit_damage,resistance,accuracy,preferred_sets,notes
kael-01,Kael,Rare,DPS / Farmer,60,6,24324,2966,1451,146,93,145,90,47,Lethal|Cruel,Farmer
rector-01,Rector Drath,Epic,Support / Revive,60,6,33790,1763,1877,119,39,80,85,57,Immortal|Speed,Revive
"""

ARTIFACTS_CSV = """artifact_id,name,set_name,slot,rank,level,rarity,main_stat,main_value,substats,equipped_by,is_new
A001,Speed Boots Kael,Speed,boots,5,16,Epic,SPD,40,\"C.RATE:8|ATK%:12\",kael-01,false
N001,Nuevas botas,Perception,boots,6,16,Epic,SPD,45,\"ACC:32|HP%:10|DEF%:12\",,true
"""


def _write_file(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def test_sync_and_load_data_from_db(tmp_path: Path):
    champions_csv = tmp_path / "champions.csv"
    artifacts_csv = tmp_path / "artifacts.csv"
    db_path = tmp_path / "raid.db"

    _write_file(champions_csv, CHAMPIONS_CSV)
    _write_file(artifacts_csv, ARTIFACTS_CSV)

    champion_count, artifact_count = sync_csv_to_db(str(champions_csv), str(artifacts_csv), str(db_path))

    assert champion_count == 2
    assert artifact_count == 2

    champions, artifacts = load_data("db", str(db_path), str(champions_csv), str(artifacts_csv))
    assert len(champions) == 2
    assert len(artifacts) == 2


def test_build_recommendations_only_uses_new_artifacts(tmp_path: Path):
    champions_csv = tmp_path / "champions.csv"
    artifacts_csv = tmp_path / "artifacts.csv"
    db_path = tmp_path / "raid.db"

    _write_file(champions_csv, CHAMPIONS_CSV)
    _write_file(artifacts_csv, ARTIFACTS_CSV)
    sync_csv_to_db(str(champions_csv), str(artifacts_csv), str(db_path))

    champions, artifacts = load_data("db", str(db_path), str(champions_csv), str(artifacts_csv))
    groups = build_recommendations(champions, artifacts, top_n=3)

    assert len(groups) == 1
    assert groups[0].artifact.artifact_id == "N001"
    assert len(groups[0].ranking) >= 1


def test_manual_add_commands_use_cases_persist_entities(tmp_path: Path):
    db_path = tmp_path / "raid.db"

    champion = Champion(
        champion_id="manual-kael-01",
        name="Manual Kael",
        rarity="Rare",
        role="DPS / Farmer",
        level=60,
        stars=6,
        hp=24324,
        atk=2966,
        defense=1451,
        speed=146,
        crit_rate=93,
        crit_damage=145,
        resistance=90,
        accuracy=47,
        preferred_sets=["Lethal", "Cruel"],
    )
    artifact = Artifact(
        artifact_id="M001",
        name="Guantes Manuales",
        set_name="Lethal",
        slot="gloves",
        rank=6,
        level=16,
        rarity="Epic",
        main_stat="C.RATE",
        main_value=60,
        substats={"C.DMG": 20, "ATK%": 15, "SPD": 8},
        is_new=True,
    )

    add_champion(champion, str(db_path))
    add_artifact(artifact, str(db_path))
    champions, artifacts = load_data("db", str(db_path), "unused.csv", "unused.csv")

    assert len(champions) == 1
    assert champions[0].name == "Manual Kael"
    assert len(artifacts) == 1
    assert artifacts[0].artifact_id == "M001"


def test_edit_champion_updates_selected_fields(tmp_path: Path):
    db_path = tmp_path / "raid.db"
    champion = Champion(
        champion_id="edit-me-01",
        name="Edit Me",
        rarity="Rare",
        role="DPS / Farmer",
        level=50,
        stars=5,
        hp=20000,
        atk=2000,
        defense=1200,
        speed=140,
        crit_rate=70,
        crit_damage=120,
        resistance=50,
        accuracy=40,
        preferred_sets=["Speed"],
        notes="old",
    )
    add_champion(champion, str(db_path))

    updated = edit_champion(
        "edit-me-01",
        str(db_path),
        level=60,
        speed=170,
        preferred_sets=["Lethal", "Cruel"],
        notes="new",
    )

    assert updated is True
    champions, _ = load_data("db", str(db_path), "unused.csv", "unused.csv")
    edited = champions[0]
    assert edited.level == 60
    assert edited.speed == 170
    assert edited.preferred_sets == ["Lethal", "Cruel"]
    assert edited.notes == "new"


def test_edit_artifact_updates_selected_fields_and_can_unequip(tmp_path: Path):
    db_path = tmp_path / "raid.db"
    artifact = Artifact(
        artifact_id="E001",
        name="Old Artifact",
        set_name="Speed",
        slot="boots",
        rank=5,
        level=12,
        rarity="Epic",
        main_stat="SPD",
        main_value=40,
        substats={"HP%": 5},
        equipped_by="edit-me-01",
        is_new=False,
    )
    add_artifact(artifact, str(db_path))

    updated = edit_artifact(
        "E001",
        str(db_path),
        name="New Artifact",
        main_value=45,
        substats={"ACC": 24, "SPD": 6},
        equipped_by="",
        is_new=True,
    )

    assert updated is True
    _, artifacts = load_data("db", str(db_path), "unused.csv", "unused.csv")
    edited = artifacts[0]
    assert edited.name == "New Artifact"
    assert edited.main_value == 45
    assert edited.substats == {"ACC": 24.0, "SPD": 6.0}
    assert edited.equipped_by is None
    assert edited.is_new is True


def test_edit_use_cases_return_false_when_entity_missing(tmp_path: Path):
    db_path = tmp_path / "raid.db"
    assert edit_champion("missing", str(db_path), level=60) is False
    assert edit_artifact("missing", str(db_path), level=16) is False


def test_query_champions_filters_by_name_role_and_rarity(tmp_path: Path):
    champions_csv = tmp_path / "champions.csv"
    artifacts_csv = tmp_path / "artifacts.csv"
    db_path = tmp_path / "raid.db"

    _write_file(champions_csv, CHAMPIONS_CSV)
    _write_file(artifacts_csv, ARTIFACTS_CSV)
    sync_csv_to_db(str(champions_csv), str(artifacts_csv), str(db_path))

    by_name = query_champions(str(db_path), name_contains="kael")
    assert len(by_name) == 1
    assert by_name[0].name == "Kael"

    by_role = query_champions(str(db_path), role="support")
    assert len(by_role) == 1
    assert by_role[0].name == "Rector Drath"

    by_rarity = query_champions(str(db_path), rarity="epic")
    assert len(by_rarity) == 1
    assert by_rarity[0].name == "Rector Drath"

    by_id = query_champions(str(db_path), champion_id="kael-01")
    assert len(by_id) == 1
    assert by_id[0].champion_id == "kael-01"


def test_query_artifacts_filters_by_fields(tmp_path: Path):
    champions_csv = tmp_path / "champions.csv"
    artifacts_csv = tmp_path / "artifacts.csv"
    db_path = tmp_path / "raid.db"

    _write_file(champions_csv, CHAMPIONS_CSV)
    _write_file(artifacts_csv, ARTIFACTS_CSV)
    sync_csv_to_db(str(champions_csv), str(artifacts_csv), str(db_path))

    by_id = query_artifacts(str(db_path), artifact_id="N001")
    assert len(by_id) == 1
    assert by_id[0].artifact_id == "N001"

    by_slot_and_set = query_artifacts(str(db_path), slot="boots", set_name="perception")
    assert len(by_slot_and_set) == 1
    assert by_slot_and_set[0].artifact_id == "N001"

    by_equipped = query_artifacts(str(db_path), equipped_by="kael-01")
    assert len(by_equipped) == 1
    assert by_equipped[0].artifact_id == "A001"

    only_new = query_artifacts(str(db_path), is_new=True)
    assert len(only_new) == 1
    assert only_new[0].artifact_id == "N001"
