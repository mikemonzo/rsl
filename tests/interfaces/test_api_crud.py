from fastapi.testclient import TestClient

from rsl_advisor.interfaces import api as api_module


def _client_with_db(tmp_path):
    api_module.DATABASE_TARGET = str(tmp_path / "api_test.db")
    return TestClient(api_module.app)


def test_champion_crud_api(tmp_path):
    client = _client_with_db(tmp_path)

    payload = {
        "champion_id": "kael-01",
        "name": "Kael",
        "rarity": "Rare",
        "role": "DPS / Farmer",
        "level": 60,
        "stars": 6,
        "hp": 24324,
        "atk": 2966,
        "defense": 1451,
        "speed": 146,
        "crit_rate": 93,
        "crit_damage": 145,
        "resistance": 90,
        "accuracy": 47,
        "preferred_sets": ["Lethal", "Cruel"],
        "notes": "Farmer",
    }

    create_res = client.post("/champions", json=payload)
    assert create_res.status_code == 201

    get_res = client.get("/champions/kael-01")
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "Kael"

    patch_res = client.patch("/champions/kael-01", json={"speed": 175, "notes": "Arena"})
    assert patch_res.status_code == 200
    assert patch_res.json()["speed"] == 175
    assert patch_res.json()["notes"] == "Arena"

    list_res = client.get("/champions", params={"role": "DPS"})
    assert list_res.status_code == 200
    assert len(list_res.json()) == 1

    delete_res = client.delete("/champions/kael-01")
    assert delete_res.status_code == 204

    missing_res = client.get("/champions/kael-01")
    assert missing_res.status_code == 404


def test_artifact_crud_api(tmp_path):
    client = _client_with_db(tmp_path)

    payload = {
        "artifact_id": "art-01",
        "name": "Guantes",
        "set_name": "Lethal",
        "slot": "gloves",
        "rank": 6,
        "level": 16,
        "rarity": "Epic",
        "main_stat": "C.RATE",
        "main_value": 60,
        "substats": {"C.DMG": 20, "ATK%": 15, "SPD": 8},
        "equipped_by": None,
        "is_new": True,
    }

    create_res = client.post("/artifacts", json=payload)
    assert create_res.status_code == 201

    get_res = client.get("/artifacts/art-01")
    assert get_res.status_code == 200
    assert get_res.json()["slot"] == "gloves"

    patch_res = client.patch(
        "/artifacts/art-01",
        json={"main_value": 65, "is_new": False, "substats": {"SPD": 10}},
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["main_value"] == 65
    assert patch_res.json()["is_new"] is False
    assert patch_res.json()["substats"] == {"SPD": 10.0}

    list_res = client.get("/artifacts", params={"slot": "gloves"})
    assert list_res.status_code == 200
    assert len(list_res.json()) == 1

    delete_res = client.delete("/artifacts/art-01")
    assert delete_res.status_code == 204

    missing_res = client.get("/artifacts/art-01")
    assert missing_res.status_code == 404
