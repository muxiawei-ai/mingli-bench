"""Deterministic candidate-year scoring diagnostics.

This module scores year options by visible local signals only. The score is a
diagnostic aid, not a prediction and not a benchmark answer.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


YEAR_OPTION_PATTERN = re.compile(r"^((?:19|20)\d{2})年?$")

INTERACTION_WEIGHTS = {
    "same_branch": 0.7,
    "six_harmony": 1.0,
    "six_clash": 1.2,
    "three_harmony_partial": 0.8,
    "three_harmony_complete": 1.6,
    "three_meeting_partial": 0.8,
    "three_meeting_complete": 1.6,
}

FOCUS_POSITION_WEIGHTS = {
    "marriage_timing": {"day": 1.2, "hour": 0.3},
    "children_timing": {"hour": 1.2, "day": 0.4},
    "health_timing": {"day": 0.7, "month": 0.7},
    "general_timing": {"day": 0.5, "month": 0.5, "hour": 0.5, "year": 0.3},
}

BRANCH_RELATION_WEIGHT = 0.4


@dataclass(frozen=True)
class CandidateYearScoringVariant:
    """One local scoring hypothesis for candidate-year diagnostics."""

    name: str
    interaction_weights: Dict[str, float]
    focus_position_weights: Dict[str, Dict[str, float]]
    branch_relation_weight: float = BRANCH_RELATION_WEIGHT


SCORING_VARIANTS = {
    "default": CandidateYearScoringVariant(
        name="default",
        interaction_weights=INTERACTION_WEIGHTS,
        focus_position_weights=FOCUS_POSITION_WEIGHTS,
    ),
    "movement_weighted": CandidateYearScoringVariant(
        name="movement_weighted",
        interaction_weights={
            **INTERACTION_WEIGHTS,
            "same_branch": 0.4,
            "six_harmony": 0.8,
            "six_clash": 2.0,
            "three_harmony_complete": 1.2,
            "three_meeting_complete": 1.2,
        },
        focus_position_weights=FOCUS_POSITION_WEIGHTS,
    ),
    "focus_palace_weighted": CandidateYearScoringVariant(
        name="focus_palace_weighted",
        interaction_weights=INTERACTION_WEIGHTS,
        focus_position_weights={
            **FOCUS_POSITION_WEIGHTS,
            "marriage_timing": {"day": 1.8, "hour": 0.2},
            "children_timing": {"hour": 1.8, "day": 0.4},
            "health_timing": {"day": 1.0, "month": 1.0},
        },
    ),
    "balanced_groups": CandidateYearScoringVariant(
        name="balanced_groups",
        interaction_weights={
            **INTERACTION_WEIGHTS,
            "same_branch": 0.5,
            "six_clash": 1.4,
            "three_harmony_partial": 0.9,
            "three_meeting_partial": 0.9,
            "three_harmony_complete": 1.1,
            "three_meeting_complete": 1.1,
        },
        focus_position_weights=FOCUS_POSITION_WEIGHTS,
    ),
}


def infer_timing_focus(question: str) -> str:
    """Infer a coarse timing focus from question text."""

    text = question or ""
    if any(
        keyword in text
        for keyword in ["结婚", "婚姻", "妻", "夫", "伴侣", "感情"]
    ):
        return "marriage_timing"
    if any(
        keyword in text
        for keyword in ["子女", "女儿", "儿子", "孩子", "出生", "生子", "怀孕"]
    ):
        return "children_timing"
    if any(
        keyword in text
        for keyword in ["病", "健康", "受伤", "意外", "抑郁", "医疗"]
    ):
        return "health_timing"
    return "general_timing"


def build_candidate_year_scores(
    question: str,
    event_years: List[Dict[str, Any]],
    option_semantics: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Score A-D options that are plain candidate years."""

    focus = infer_timing_focus(question)
    event_by_year = {int(item["year"]): item for item in event_years if item.get("year")}
    candidates = []
    for option in option_semantics:
        year = _option_year(option.get("text"))
        if year is None or year not in event_by_year:
            continue
        candidates.append(
            _score_candidate_year(
                option,
                event_by_year[year],
                focus,
            )
        )
    _assign_variant_ranks(candidates)
    return [
        {**item, "rank": item["variant_ranks"]["default"]}
        for item in candidates
    ]


def _score_candidate_year(
    option: Dict[str, Any],
    event_year: Dict[str, Any],
    focus: str,
) -> Dict[str, Any]:
    default_variant = SCORING_VARIANTS["default"]
    score = 0.0
    signals = []
    interaction_labels = []
    matched_positions = []
    for interaction in event_year.get("branch_interactions") or []:
        interaction_type = str(interaction.get("type") or "")
        weight = default_variant.interaction_weights.get(interaction_type, 0.0)
        if weight:
            score += weight
            label = str(interaction.get("label") or interaction_type)
            interaction_labels.append(label)
            signals.append(
                {
                    "type": "branch_interaction",
                    "label": label,
                    "weight": weight,
                }
            )
        positions = _interaction_positions(interaction)
        matched_positions.extend(positions)
        for position in positions:
            position_weight = (
                default_variant.focus_position_weights.get(focus, {}).get(position, 0.0)
            )
            if position_weight:
                score += position_weight
                signals.append(
                    {
                        "type": "focus_position",
                        "position": position,
                        "focus": focus,
                        "weight": position_weight,
                    }
                )
    branch_relation = event_year.get("branch_relation_to_day_master")
    if branch_relation in {"controls_day_master", "controlled_by_day_master"}:
        score += default_variant.branch_relation_weight
        signals.append(
            {
                "type": "branch_relation_to_day_master",
                "label": branch_relation,
                "weight": default_variant.branch_relation_weight,
            }
        )
    variant_scores = {
        name: _score_with_variant(event_year, focus, variant)
        for name, variant in SCORING_VARIANTS.items()
    }
    return {
        "letter": option.get("letter"),
        "text": option.get("text"),
        "year": event_year.get("year"),
        "year_pillar": event_year.get("year_pillar"),
        "focus": focus,
        "score": round(score, 4),
        "variant_scores": variant_scores,
        "variant_ranks": {},
        "interaction_labels": interaction_labels,
        "matched_positions": sorted(set(matched_positions)),
        "signals": signals,
        "note": "candidate_year_score_is_diagnostic_not_gold_label",
    }


def _score_with_variant(
    event_year: Dict[str, Any],
    focus: str,
    variant: CandidateYearScoringVariant,
) -> float:
    score = 0.0
    for interaction in event_year.get("branch_interactions") or []:
        interaction_type = str(interaction.get("type") or "")
        score += variant.interaction_weights.get(interaction_type, 0.0)
        for position in _interaction_positions(interaction):
            score += variant.focus_position_weights.get(focus, {}).get(position, 0.0)
    branch_relation = event_year.get("branch_relation_to_day_master")
    if branch_relation in {"controls_day_master", "controlled_by_day_master"}:
        score += variant.branch_relation_weight
    return round(score, 4)


def _assign_variant_ranks(candidates: List[Dict[str, Any]]) -> None:
    for variant_name in SCORING_VARIANTS:
        ranked = sorted(
            candidates,
            key=lambda item: item["variant_scores"].get(variant_name, 0.0),
            reverse=True,
        )
        for rank, item in enumerate(ranked, start=1):
            item["variant_ranks"][variant_name] = rank


def _interaction_positions(interaction: Dict[str, Any]) -> List[str]:
    positions = []
    if interaction.get("natal_position"):
        positions.append(str(interaction["natal_position"]))
    positions.extend(
        str(item) for item in interaction.get("matched_natal_positions") or []
    )
    return positions


def _option_year(text: Any) -> Optional[int]:
    match = YEAR_OPTION_PATTERN.fullmatch(str(text or "").strip())
    if not match:
        return None
    return int(match.group(1))


__all__ = [
    "build_candidate_year_scores",
    "CandidateYearScoringVariant",
    "infer_timing_focus",
    "SCORING_VARIANTS",
]
