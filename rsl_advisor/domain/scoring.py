from __future__ import annotations

from typing import Dict, List, Sequence, Tuple

from .models import Artifact, Champion, Recommendation

ROLE_WEIGHTS: Dict[str, Dict[str, float]] = {
    "DPS / Farmer": {
        "SPD": 1.4,
        "C.RATE": 2.2,
        "C.DMG": 1.8,
        "ATK%": 1.8,
        "ATK": 0.7,
        "ACC": 0.5,
        "HP%": 0.4,
        "DEF%": 0.4,
        "RES": 0.2,
    },
    "Clan Boss Poison": {
        "SPD": 1.8,
        "ACC": 2.2,
        "HP%": 1.0,
        "DEF%": 1.1,
        "C.RATE": 0.6,
        "C.DMG": 0.5,
        "ATK%": 0.6,
        "RES": 0.2,
    },
    "Support / Cleanse": {
        "SPD": 2.4,
        "HP%": 1.8,
        "DEF%": 1.7,
        "RES": 1.3,
        "ACC": 0.8,
        "C.RATE": 0.1,
        "C.DMG": 0.1,
        "ATK%": 0.2,
    },
    "Support / Revive": {
        "SPD": 2.3,
        "HP%": 1.9,
        "DEF%": 1.8,
        "RES": 1.1,
        "ACC": 0.5,
        "C.RATE": 0.1,
        "C.DMG": 0.1,
        "ATK%": 0.2,
    },
    "Debuffer / Control": {
        "SPD": 2.1,
        "ACC": 2.0,
        "DEF%": 1.2,
        "HP%": 1.0,
        "RES": 0.5,
        "C.RATE": 0.5,
        "C.DMG": 0.3,
        "ATK%": 0.3,
    },
    "Bombs (Arena)": {
        "SPD": 2.0,
        "ACC": 1.7,
        "ATK%": 1.8,
        "ATK": 0.9,
        "HP%": 0.6,
        "DEF%": 0.6,
        "RES": 0.2,
        "C.RATE": 0.1,
        "C.DMG": 0.1,
    },
    "Speed Booster": {
        "SPD": 2.8,
        "HP%": 1.2,
        "DEF%": 1.1,
        "RES": 0.8,
        "ACC": 0.4,
        "C.RATE": 0.1,
        "C.DMG": 0.1,
        "ATK%": 0.2,
    },
}

DEFAULT_ROLE_WEIGHTS = {
    "SPD": 1.5,
    "HP%": 1.0,
    "DEF%": 1.0,
    "ACC": 1.0,
    "RES": 0.5,
    "C.RATE": 0.7,
    "C.DMG": 0.7,
    "ATK%": 0.8,
    "ATK": 0.4,
}

PREFERRED_MAIN_STATS: Dict[str, Dict[str, List[str]]] = {
    "boots": {
        "all": ["SPD"],
        "DPS / Farmer": ["SPD", "ATK%"],
        "Clan Boss Poison": ["SPD"],
        "Support / Cleanse": ["SPD"],
        "Support / Revive": ["SPD"],
        "Debuffer / Control": ["SPD"],
        "Bombs (Arena)": ["SPD", "ATK%"],
    },
    "chest": {
        "DPS / Farmer": ["ATK%", "HP%", "DEF%"],
        "Clan Boss Poison": ["HP%", "DEF%", "ATK%"],
        "Support / Cleanse": ["HP%", "DEF%", "RES"],
        "Support / Revive": ["HP%", "DEF%", "RES"],
        "Debuffer / Control": ["ACC", "HP%", "DEF%"],
        "Bombs (Arena)": ["ATK%", "ACC"],
        "all": ["HP%", "DEF%", "ATK%"],
    },
    "gloves": {
        "DPS / Farmer": ["C.RATE", "C.DMG", "ATK%"],
        "Clan Boss Poison": ["HP%", "DEF%", "C.RATE"],
        "Support / Cleanse": ["HP%", "DEF%"],
        "Support / Revive": ["HP%", "DEF%"],
        "Debuffer / Control": ["HP%", "DEF%", "C.RATE"],
        "Bombs (Arena)": ["ATK%", "HP%"],
        "all": ["HP%", "DEF%"],
    },
}

ANTI_WEIGHTS: Dict[str, Dict[str, float]] = {
    "Support / Cleanse": {"C.RATE": -0.4, "C.DMG": -0.4},
    "Support / Revive": {"C.RATE": -0.4, "C.DMG": -0.4},
    "Bombs (Arena)": {"C.RATE": -0.3, "C.DMG": -0.3},
}

STAT_NORMALIZATION = {
    "SPD": 1.0,
    "ACC": 8.0,
    "RES": 10.0,
    "C.RATE": 7.0,
    "C.DMG": 8.0,
    "HP%": 5.0,
    "DEF%": 5.0,
    "ATK%": 5.0,
    "HP": 500.0,
    "DEF": 30.0,
    "ATK": 30.0,
}


def normalise_stat_name(raw: str) -> str:
    s = raw.strip().upper().replace("CRIT RATE", "C.RATE").replace("CRIT DAMAGE", "C.DMG")
    aliases = {
        "CR%": "C.RATE",
        "CD%": "C.DMG",
        "CRATE": "C.RATE",
        "CDMG": "C.DMG",
        "DEF": "DEF",
        "HP": "HP",
        "ATK": "ATK",
        "SPD": "SPD",
        "ACC": "ACC",
        "RES": "RES",
    }
    return aliases.get(s, s)


def role_key(role: str) -> str:
    role = role.strip()
    if role in ROLE_WEIGHTS:
        return role

    low = role.lower()
    if "revive" in low:
        return "Support / Revive"
    if "cleanse" in low or "support" in low:
        return "Support / Cleanse"
    if "poison" in low or "clan boss" in low:
        return "Clan Boss Poison"
    if "debuff" in low or "control" in low:
        return "Debuffer / Control"
    if "bomb" in low:
        return "Bombs (Arena)"
    if "speed" in low:
        return "Speed Booster"
    if "dps" in low or "farmer" in low:
        return "DPS / Farmer"
    return "default"


def get_weights(champion: Champion) -> Dict[str, float]:
    return ROLE_WEIGHTS.get(role_key(champion.role), DEFAULT_ROLE_WEIGHTS)


def get_anti_weights(champion: Champion) -> Dict[str, float]:
    return ANTI_WEIGHTS.get(role_key(champion.role), {})


def preferred_main_stat_bonus(champion: Champion, artifact: Artifact) -> float:
    slot = artifact.slot.lower()
    role = role_key(champion.role)
    options = PREFERRED_MAIN_STATS.get(slot, {})
    preferred = options.get(role, options.get("all", []))

    stat = normalise_stat_name(artifact.main_stat)
    if stat in preferred:
        return 8.0
    return 0.0


def set_bonus(champion: Champion, artifact: Artifact) -> float:
    if not champion.preferred_sets:
        return 0.0
    if artifact.set_name.lower() in {s.lower() for s in champion.preferred_sets}:
        return 3.5
    return 0.0


def stat_score(stat: str, value: float, weights: Dict[str, float], anti: Dict[str, float]) -> float:
    stat = normalise_stat_name(stat)
    norm = STAT_NORMALIZATION.get(stat, 10.0)
    positive = weights.get(stat, 0.0)
    negative = anti.get(stat, 0.0)
    return (value / norm) * (positive + negative)


def artifact_score_for_champion(champion: Champion, artifact: Artifact) -> float:
    weights = get_weights(champion)
    anti = get_anti_weights(champion)

    total = 0.0
    total += stat_score(artifact.main_stat, artifact.main_value, weights, anti)

    for stat, value in artifact.substats.items():
        total += stat_score(stat, value, weights, anti)

    total += preferred_main_stat_bonus(champion, artifact)
    total += set_bonus(champion, artifact)

    if champion.accuracy < 180 and "ACC" in artifact.substats:
        total += min(artifact.substats["ACC"] / 10.0, 3.0)

    if champion.speed < 170 and "SPD" in artifact.substats:
        total += min(artifact.substats["SPD"] / 2.0, 4.0)

    return round(total, 2)


def current_equipped_by_slot(artifacts: Sequence[Artifact]) -> Dict[Tuple[str, str], Artifact]:
    result: Dict[Tuple[str, str], Artifact] = {}
    for art in artifacts:
        if art.equipped_by:
            result[(art.equipped_by.lower(), art.slot.lower())] = art
    return result


def evaluate_new_artifact(
    artifact: Artifact,
    champions: Sequence[Champion],
    equipped_map: Dict[Tuple[str, str], Artifact],
    top_n: int = 5,
) -> List[Recommendation]:
    ranking: List[Recommendation] = []

    for champion in champions:
        new_score = artifact_score_for_champion(champion, artifact)
        current = equipped_map.get((champion.name.lower(), artifact.slot.lower()))
        current_score = artifact_score_for_champion(champion, current) if current else 0.0
        delta = round(new_score - current_score, 2)

        ranking.append(
            Recommendation(
                champion=champion.name,
                role=champion.role,
                new_score=new_score,
                current_score=current_score,
                delta=delta,
                current_item=current.name if current else None,
            )
        )

    ranking.sort(key=lambda row: (row.delta, row.new_score), reverse=True)
    return ranking[:top_n]


def explain_artifact_fit(champion: Champion, artifact: Artifact) -> str:
    weights = get_weights(champion)
    useful_stats = []
    for stat, value in artifact.substats.items():
        w = weights.get(normalise_stat_name(stat), 0)
        if w > 0.9:
            useful_stats.append(f"{stat}+{value}")

    main = f"main stat {artifact.main_stat}"
    if useful_stats:
        return f"Encaja por {main} y substats utiles: {', '.join(useful_stats)}"
    return f"Encaja principalmente por {main}"
