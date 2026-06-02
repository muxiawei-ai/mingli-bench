"""Deterministic earthly-branch relation helpers.

These helpers expose auditable rule signals for agent prompts and evaluation.
They intentionally report structural relationships only; interpretation remains
outside this module.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Tuple


SIX_CLASHES = {
    frozenset(("子", "午")): "子午冲",
    frozenset(("丑", "未")): "丑未冲",
    frozenset(("寅", "申")): "寅申冲",
    frozenset(("卯", "酉")): "卯酉冲",
    frozenset(("辰", "戌")): "辰戌冲",
    frozenset(("巳", "亥")): "巳亥冲",
}

SIX_HARMONIES = {
    frozenset(("子", "丑")): ("子丑合土", "土"),
    frozenset(("寅", "亥")): ("寅亥合木", "木"),
    frozenset(("卯", "戌")): ("卯戌合火", "火"),
    frozenset(("辰", "酉")): ("辰酉合金", "金"),
    frozenset(("巳", "申")): ("巳申合水", "水"),
    frozenset(("午", "未")): ("午未合土", "土"),
}

THREE_HARMONY_GROUPS = [
    (("申", "子", "辰"), "水"),
    (("亥", "卯", "未"), "木"),
    (("寅", "午", "戌"), "火"),
    (("巳", "酉", "丑"), "金"),
]

THREE_MEETING_GROUPS = [
    (("亥", "子", "丑"), "水"),
    (("寅", "卯", "辰"), "木"),
    (("巳", "午", "未"), "火"),
    (("申", "酉", "戌"), "金"),
]


def analyze_branch_interactions(
    event_branch: str,
    natal_branches: Dict[str, str],
) -> List[Dict[str, Any]]:
    """Return deterministic branch interactions between a flow branch and natal chart.

    Args:
        event_branch: Earthly branch from the event/flow year.
        natal_branches: Mapping such as ``{"year": "寅", "month": "辰"}``.
    """

    interactions: List[Dict[str, Any]] = []
    for position, branch in natal_branches.items():
        if not branch:
            continue
        interactions.extend(_pair_interactions(event_branch, branch, position))

    interactions.extend(
        _group_interactions(
            event_branch,
            natal_branches,
            THREE_HARMONY_GROUPS,
            complete_type="three_harmony_complete",
            partial_type="three_harmony_partial",
            complete_label="三合",
            partial_label="半合",
        )
    )
    interactions.extend(
        _group_interactions(
            event_branch,
            natal_branches,
            THREE_MEETING_GROUPS,
            complete_type="three_meeting_complete",
            partial_type="three_meeting_partial",
            complete_label="三会",
            partial_label="半会",
        )
    )
    return interactions


def _pair_interactions(
    event_branch: str,
    natal_branch: str,
    natal_position: str,
) -> List[Dict[str, Any]]:
    interactions: List[Dict[str, Any]] = []
    if event_branch == natal_branch:
        interactions.append(
            {
                "type": "same_branch",
                "label": f"{event_branch}{natal_branch}同支",
                "event_branch": event_branch,
                "natal_branch": natal_branch,
                "natal_position": natal_position,
            }
        )

    pair = frozenset((event_branch, natal_branch))
    clash_label = SIX_CLASHES.get(pair)
    if clash_label:
        interactions.append(
            {
                "type": "six_clash",
                "label": clash_label,
                "event_branch": event_branch,
                "natal_branch": natal_branch,
                "natal_position": natal_position,
            }
        )

    harmony = SIX_HARMONIES.get(pair)
    if harmony:
        label, element = harmony
        interactions.append(
            {
                "type": "six_harmony",
                "label": label,
                "element": element,
                "event_branch": event_branch,
                "natal_branch": natal_branch,
                "natal_position": natal_position,
            }
        )
    return interactions


def _group_interactions(
    event_branch: str,
    natal_branches: Dict[str, str],
    groups: Iterable[Tuple[Tuple[str, str, str], str]],
    *,
    complete_type: str,
    partial_type: str,
    complete_label: str,
    partial_label: str,
) -> List[Dict[str, Any]]:
    interactions = []
    natal_branch_values = set(natal_branches.values())
    for group, element in groups:
        if event_branch not in group:
            continue
        matched_natal_branches = [
            branch for branch in group if branch != event_branch and branch in natal_branch_values
        ]
        if not matched_natal_branches:
            continue
        is_complete = len(matched_natal_branches) == 2
        present_branches = [
            branch
            for branch in group
            if branch == event_branch or branch in matched_natal_branches
        ]
        interactions.append(
            {
                "type": complete_type if is_complete else partial_type,
                "label": _group_label(
                    present_branches if not is_complete else list(group),
                    element,
                    complete_label if is_complete else partial_label,
                    complete=is_complete,
                ),
                "element": element,
                "event_branch": event_branch,
                "branches": present_branches if not is_complete else list(group),
                "matched_natal_branches": matched_natal_branches,
                "matched_natal_positions": _positions_for_branches(
                    natal_branches,
                    matched_natal_branches,
                ),
                "complete": is_complete,
            }
        )
    return interactions


def _group_label(
    branches: List[str],
    element: str,
    relation_label: str,
    *,
    complete: bool,
) -> str:
    suffix = "局" if complete else ""
    return f"{''.join(branches)}{relation_label}{element}{suffix}"


def _positions_for_branches(
    natal_branches: Dict[str, str],
    branches: List[str],
) -> List[str]:
    branch_set = set(branches)
    return [
        position
        for position, branch in natal_branches.items()
        if branch in branch_set
    ]


__all__ = [
    "SIX_CLASHES",
    "SIX_HARMONIES",
    "THREE_HARMONY_GROUPS",
    "THREE_MEETING_GROUPS",
    "analyze_branch_interactions",
]
