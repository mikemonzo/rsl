from rsl_advisor.domain.models import Artifact, Champion
from rsl_advisor.domain.scoring import evaluate_new_artifact
from rsl_advisor.infrastructure.csv_io import parse_substats


def test_parse_substats_ignores_invalid_values():
    parsed = parse_substats("SPD:12|ACC:abc|HP%:10")
    assert parsed == {"SPD": 12.0, "HP%": 10.0}


def test_evaluate_new_artifact_returns_sorted_ranking_by_delta_then_score():
    kael = Champion(
        champion_id="kael-01",
        name="Kael",
        rarity="Rare",
        role="DPS / Farmer",
        level=60,
        stars=6,
        hp=20000,
        atk=2500,
        defense=1200,
        speed=150,
        crit_rate=80,
        crit_damage=140,
        resistance=70,
        accuracy=60,
        preferred_sets=["Lethal"],
    )
    rector = Champion(
        champion_id="rector-01",
        name="Rector Drath",
        rarity="Epic",
        role="Support / Revive",
        level=60,
        stars=6,
        hp=32000,
        atk=1500,
        defense=2000,
        speed=120,
        crit_rate=20,
        crit_damage=70,
        resistance=90,
        accuracy=50,
        preferred_sets=["Immortal"],
    )

    current_gloves_kael = Artifact(
        artifact_id="A1",
        name="Guantes Kael",
        set_name="Cruel",
        slot="gloves",
        rank=5,
        level=16,
        rarity="Epic",
        main_stat="HP%",
        main_value=50,
        substats={"DEF%": 10},
        equipped_by="kael-01",
    )
    new_gloves = Artifact(
        artifact_id="N1",
        name="Guantes nuevos",
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

    equipped_map = {
        ("kael-01", "gloves"): current_gloves_kael,
    }

    ranking = evaluate_new_artifact(new_gloves, [kael, rector], equipped_map, top_n=2)

    assert len(ranking) == 2
    assert ranking[0].champion_name == "Kael"
    assert ranking[0].delta > ranking[1].delta
