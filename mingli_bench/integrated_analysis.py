"""Bazi + hexagram integration rules for local MingLi reports."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence

from .intent import DEFAULT_DOMAIN, parse_question_intent


INTEGRATED_ANALYSIS_SCHEMA_VERSION = "mingli_integrated_analysis.v1"

LEVEL_LABELS = {
    "absent": "未见",
    "light": "偏少",
    "present": "适中",
    "high": "偏多",
    "low": "偏少",
    "medium": "适中",
}

RELATION_LABELS = {
    "same_as_day_master": "同日主",
    "generated_by_day_master": "日主所生",
    "generates_day_master": "生日主",
    "controlled_by_day_master": "日主所克",
    "controls_day_master": "克日主",
}

DOMAIN_INTEGRATION_GUIDANCE = {
    "事业": "事业问题中，先看八字显示的能力惯性和资源短板，再看卦象给出的阶段触发点；结论应落到推进节奏、协作方式和可执行下一步。",
    "财运": "财务问题中，先分清命盘中的资源敏感点和风险元素，再用卦象观察当下能否承接资源；不把联合分析直接写成投资或收益判断。",
    "婚姻": "关系问题中，八字用于观察互动倾向，卦象用于观察当下关系触发点；重点放在沟通、边界和修复空间。",
    "健康": "健康问题中，联合分析只能作为传统结构参考；任何身体、疾病、治疗相关内容都必须回到专业医学意见。",
    "性格": "性格问题中，八字用于提炼长期行为倾向，卦象用于提示当前表达方式或调整方向；避免把性格说成不可改变的定论。",
    "学业": "学业问题中，八字用于观察学习方式和基础短板，卦象用于提示当下节奏；建议应落到复盘、练习和资源配置。",
    "家庭": "家庭问题中，八字用于观察责任与关系结构，卦象用于提示当前沟通触发点；避免把复杂关系归咎于单一方。",
    "运势": "阶段运势中，八字提供底盘和流年关系，卦象提供当下触发点；重点是时间窗口、行动节奏和需要补充的信息。",
    DEFAULT_DOMAIN: "综合问题中，先把八字作为底盘，再把卦象作为当下触发和变化方向；若问题过宽，应优先提出追问。",
}


def build_integrated_analysis(
    *,
    question: str,
    summary: Dict[str, Any],
    element_profile: Sequence[Any],
    strongest_elements: Sequence[str],
    missing_elements: Sequence[str],
    event_years: Sequence[Dict[str, Any]],
    hexagram: Optional[Dict[str, Any]],
    question_hexagram: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    """Build a deterministic scaffold that connects Bazi and hexagram signals."""

    active_hexagram = question_hexagram or hexagram
    if not active_hexagram:
        return None

    intent = parse_question_intent(question)
    domain = intent.primary_domain
    profile = [_profile_item(item) for item in element_profile]
    strongest = [str(item) for item in strongest_elements if item]
    missing = [str(item) for item in missing_elements if item]
    alignment_signals = _alignment_signals(profile, strongest, missing, active_hexagram)
    hexagram_role = "question_hexagram" if question_hexagram else "hexagram"
    hexagram_role_label = "问事卦" if question_hexagram else "本命卦"

    sections = [
        {
            "title": "八字底盘",
            "summary": _bazi_summary(summary, profile, strongest, missing),
            "evidence": _bazi_evidence(summary, profile, strongest, missing),
        },
        {
            "title": f"{hexagram_role_label}触发",
            "summary": _hexagram_summary(active_hexagram),
            "evidence": _hexagram_evidence(active_hexagram),
        },
        {
            "title": "交叉印证",
            "summary": _alignment_summary(alignment_signals),
            "evidence": [
                f"{signal['label']}: {signal['evidence']}"
                for signal in alignment_signals
            ],
        },
        {
            "title": f"{domain}综合框架",
            "summary": _domain_summary(
                domain,
                summary,
                strongest,
                missing,
                active_hexagram,
            ),
            "evidence": _domain_evidence(intent, event_years),
        },
    ]

    return {
        "schema_version": INTEGRATED_ANALYSIS_SCHEMA_VERSION,
        "domain": domain,
        "intent_confidence": intent.confidence,
        "hexagram_role": hexagram_role,
        "hexagram_role_label": hexagram_role_label,
        "overview": _overview(summary, strongest, missing, active_hexagram, domain),
        "sections": sections,
        "alignment_signals": alignment_signals,
        "next_questions": _next_questions(domain, active_hexagram, event_years),
        "caveats": [
            "联合分析只说明八字结构与卦象结构如何互相参考，不把传统命理推演表述为确定事实。",
            "卦象由本地时间法生成，八字由本地排盘规则生成；现实决策仍需结合事实信息和专业意见。",
        ],
    }


def _profile_item(item: Any) -> Dict[str, Any]:
    if hasattr(item, "as_dict"):
        return item.as_dict()
    if isinstance(item, dict):
        return dict(item)
    return {}


def _bazi_summary(
    summary: Dict[str, Any],
    profile: Sequence[Dict[str, Any]],
    strongest: Sequence[str],
    missing: Sequence[str],
) -> str:
    strongest_text = "、".join(strongest) or "无"
    missing_text = "、".join(missing) or "无"
    return (
        f"八字底盘显示日主为{summary.get('day_master', '-')}（"
        f"{summary.get('day_master_element') or '未知'}），"
        f"显性五行相对较多为{strongest_text}，未见元素为{missing_text}。"
        f"这部分代表长期结构和惯性，优先作为分析底盘。"
    )


def _bazi_evidence(
    summary: Dict[str, Any],
    profile: Sequence[Dict[str, Any]],
    strongest: Sequence[str],
    missing: Sequence[str],
) -> List[str]:
    return [
        f"pillars_text={summary.get('pillars_text', '-')}",
        f"day_master={summary.get('day_master', '-')}",
        f"day_master_element={summary.get('day_master_element') or '未知'}",
        "element_profile=" + " ".join(_profile_text(item) for item in profile),
        "strongest_elements=" + ",".join(strongest),
        "missing_elements=" + ",".join(missing),
    ]


def _profile_text(item: Dict[str, Any]) -> str:
    element = item.get("element", "-")
    count = item.get("count", "-")
    level = LEVEL_LABELS.get(str(item.get("level")), str(item.get("level", "-")))
    relation = RELATION_LABELS.get(
        str(item.get("relation_to_day_master")),
        str(item.get("relation_to_day_master") or ""),
    )
    relation_text = f"，{relation}" if relation else ""
    return f"{element}{count}（{level}{relation_text}）"


def _hexagram_summary(hexagram: Dict[str, Any]) -> str:
    reading = hexagram.get("reading") or {}
    if reading.get("overview"):
        return str(reading["overview"])
    primary = hexagram.get("primary") or {}
    changed = hexagram.get("changed") or {}
    return (
        f"卦象显示本卦《{primary.get('name', '-')}》，"
        f"动{hexagram.get('moving_line_name', '-')}，"
        f"变卦《{changed.get('name', '-')}》。"
    )


def _hexagram_evidence(hexagram: Dict[str, Any]) -> List[str]:
    primary = hexagram.get("primary") or {}
    changed = hexagram.get("changed") or {}
    evidence = [
        f"primary={primary.get('name', '-')}",
        f"primary_theme={primary.get('theme') or '-'}",
        f"moving_line={hexagram.get('moving_line_name', '-')}",
        f"moving_line_text={hexagram.get('moving_line_text', '-')}",
        f"changed={changed.get('name', '-')}",
        f"changed_theme={changed.get('theme') or '-'}",
    ]
    reading = hexagram.get("reading") or {}
    for section in reading.get("sections") or []:
        if section.get("title") and section.get("summary"):
            evidence.append(f"{section['title']}={section['summary']}")
    return evidence


def _alignment_signals(
    profile: Sequence[Dict[str, Any]],
    strongest: Sequence[str],
    missing: Sequence[str],
    hexagram: Dict[str, Any],
) -> List[Dict[str, str]]:
    signals: List[Dict[str, str]] = []
    profile_by_element = {
        str(item.get("element")): item
        for item in profile
        if item.get("element")
    }
    hex_elements = _hexagram_elements(hexagram)
    unique_hex_elements = _unique(hex_elements)
    strongest_overlap = [item for item in unique_hex_elements if item in strongest]
    missing_overlap = [item for item in unique_hex_elements if item in missing]

    if strongest_overlap:
        signals.append(
            {
                "type": "reinforces_existing_pattern",
                "label": "卦象触及命盘相对较多元素",
                "evidence": "、".join(strongest_overlap),
                "implication": "可把这些元素看作已有惯性或可调用资源，但也要留意过旺带来的偏执与失衡。",
            }
        )
    if missing_overlap:
        signals.append(
            {
                "type": "points_to_missing_element",
                "label": "卦象触及命盘未见元素",
                "evidence": "、".join(missing_overlap),
                "implication": "这些元素适合作为补充任务或需要借助外部环境的线索，不代表命盘已经自动补足。",
            }
        )

    for element in unique_hex_elements:
        item = profile_by_element.get(element)
        if not item:
            continue
        relation = RELATION_LABELS.get(
            str(item.get("relation_to_day_master")),
            "",
        )
        if relation:
            signals.append(
                {
                    "type": "day_master_relation",
                    "label": f"卦象元素与日主关系：{element}",
                    "evidence": relation,
                    "implication": "解读时应把卦象元素放回日主关系中，而不是孤立解释上下卦五行。",
                }
            )

    if not signals:
        signals.append(
            {
                "type": "structural_reference_only",
                "label": "未检出明显五行重合",
                "evidence": "hexagram_elements=" + "、".join(unique_hex_elements),
                "implication": "本次联合分析以本卦、动爻和问题语境为主，不强行制造五行印证。",
            }
        )
    return signals


def _hexagram_elements(hexagram: Dict[str, Any]) -> List[str]:
    elements: List[str] = []
    for role in ("primary", "changed"):
        item = hexagram.get(role) or {}
        for key in ("upper_element", "lower_element"):
            value = item.get(key)
            if value:
                elements.append(str(value))
    return elements


def _alignment_summary(signals: Sequence[Dict[str, str]]) -> str:
    parts = []
    for signal in signals:
        label = signal.get("label", "结构信号")
        evidence = signal.get("evidence", "-")
        implication = signal.get("implication", "")
        parts.append(f"{label}（{evidence}）：{implication}")
    return " ".join(parts)


def _domain_summary(
    domain: str,
    summary: Dict[str, Any],
    strongest: Sequence[str],
    missing: Sequence[str],
    hexagram: Dict[str, Any],
) -> str:
    guidance = DOMAIN_INTEGRATION_GUIDANCE.get(
        domain,
        DOMAIN_INTEGRATION_GUIDANCE[DEFAULT_DOMAIN],
    )
    primary = hexagram.get("primary") or {}
    changed = hexagram.get("changed") or {}
    return (
        f"{guidance}"
        f"当前可把日主{summary.get('day_master', '-')}、"
        f"相对较多的{'、'.join(strongest) or '无'}、"
        f"未见的{'、'.join(missing) or '无'}，"
        f"与本卦《{primary.get('name', '-')}》到变卦《{changed.get('name', '-')}》"
        "的变化方向合并观察。"
    )


def _domain_evidence(intent: Any, event_years: Sequence[Dict[str, Any]]) -> List[str]:
    evidence = [
        f"domain={intent.primary_domain}",
        f"intent_confidence={intent.confidence}",
    ]
    if event_years:
        event_text = []
        for item in event_years:
            labels = [
                interaction.get("label")
                for interaction in item.get("branch_interactions") or []
                if interaction.get("label")
            ]
            relation_text = "、".join(labels) or "未检出主要冲合会合"
            event_text.append(
                f"{item.get('year')}:{item.get('year_pillar')}:{relation_text}"
            )
        evidence.append("event_years=" + " | ".join(event_text))
    if intent.matched_keywords:
        for domain, keywords in intent.matched_keywords.items():
            evidence.append(f"matched_keywords.{domain}={','.join(keywords)}")
    return evidence


def _overview(
    summary: Dict[str, Any],
    strongest: Sequence[str],
    missing: Sequence[str],
    hexagram: Dict[str, Any],
    domain: str,
) -> str:
    primary = hexagram.get("primary") or {}
    changed = hexagram.get("changed") or {}
    return (
        f"联合分析以日主{summary.get('day_master', '-')}（"
        f"{summary.get('day_master_element') or '未知'}）和五行结构为底盘，"
        f"以本卦《{primary.get('name', '-')}》、"
        f"动{hexagram.get('moving_line_name', '-')}、"
        f"变卦《{changed.get('name', '-')}》作为当下触发。"
        f"在{domain}方向上，重点观察已有惯性（{'、'.join(strongest) or '无'}）"
        f"与待补线索（{'、'.join(missing) or '无'}）如何影响行动节奏。"
    )


def _next_questions(
    domain: str,
    hexagram: Dict[str, Any],
    event_years: Sequence[Dict[str, Any]],
) -> List[str]:
    primary = (hexagram.get("primary") or {}).get("name", "本卦")
    changed = (hexagram.get("changed") or {}).get("name", "变卦")
    questions = [
        f"围绕{primary}到{changed}的变化，当前最需要落地的是资源、关系还是时间窗口？",
        "是否可以补充当前现实处境，以便区分命盘长期结构和卦象当下触发？",
    ]
    if event_years:
        questions.append("题目涉及具体年份，是否需要把流年关系与卦象变化逐年对照？")
    elif domain == "运势":
        questions.append("如果关注阶段运势，建议补充具体年份或月份窗口。")
    return questions


def _unique(values: Sequence[str]) -> List[str]:
    result: List[str] = []
    for value in values:
        if value and value not in result:
            result.append(value)
    return result


__all__ = [
    "DOMAIN_INTEGRATION_GUIDANCE",
    "INTEGRATED_ANALYSIS_SCHEMA_VERSION",
    "build_integrated_analysis",
]
