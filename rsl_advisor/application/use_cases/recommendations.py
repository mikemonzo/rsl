from __future__ import annotations

from dataclasses import dataclass
from typing import List

from rsl_advisor.domain.models import Artifact, Champion, Recommendation
from rsl_advisor.domain.scoring import current_equipped_by_slot, evaluate_new_artifact, explain_artifact_fit


@dataclass
class ArtifactRecommendation:
    artifact: Artifact
    ranking: List[Recommendation]


def build_recommendations(champions: List[Champion], artifacts: List[Artifact], top_n: int) -> List[ArtifactRecommendation]:
    equipped_map = current_equipped_by_slot(artifacts)
    new_items = [artifact for artifact in artifacts if artifact.is_new]
    output: List[ArtifactRecommendation] = []

    for artifact in new_items:
        ranking = evaluate_new_artifact(artifact, champions, equipped_map, top_n=top_n)
        output.append(ArtifactRecommendation(artifact=artifact, ranking=ranking))

    return output


def recommendation_reason(champion: Champion, artifact: Artifact) -> str:
    return explain_artifact_fit(champion, artifact)
