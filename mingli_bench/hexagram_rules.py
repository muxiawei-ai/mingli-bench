"""Rule-based interpretation helpers for deterministic hexagram reports."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .intent import DEFAULT_DOMAIN, parse_question_intent


HEXAGRAM_READING_SCHEMA_VERSION = "hexagram_reading.v1"

LINE_POSITION_RULES: Dict[int, Dict[str, str]] = {
    1: {
        "stage": "初始与根基",
        "focus": "先看事情的起点、基础条件和潜在苗头。",
    },
    2: {
        "stage": "内部响应与执行位",
        "focus": "重点看实际执行、关系响应和内在资源是否配合。",
    },
    3: {
        "stage": "内外交界与风险位",
        "focus": "处在由内向外的转换点，容易出现急进、迟疑或摩擦。",
    },
    4: {
        "stage": "外部承接与近主位",
        "focus": "重点看能否承接外部机会，并把态度落实成行动。",
    },
    5: {
        "stage": "主位与决策位",
        "focus": "重点看主导权、判断力、资源调度和关键选择。",
    },
    6: {
        "stage": "收束与过极位",
        "focus": "事情进入后段，需观察过度、收尾、反转或余波。",
    },
}

DOMAIN_HEXAGRAM_GUIDANCE: Dict[str, str] = {
    "事业": "用于事业问题时，优先把卦象落实到推进节奏、协作对象、角色边界和阶段转换；不要只看抽象吉凶。",
    "财运": "用于财务问题时，优先观察资源来源、承接能力、风险暴露和现金流节奏；不要把卦象直接当作投资判断。",
    "婚姻": "用于关系问题时，优先观察互动模式、情绪回应、边界与修复空间；不宜把卦象写成单方面定论。",
    "健康": "用于健康问题时，只能作为传统象意和压力结构参考；必须避免替代医学诊断或治疗建议。",
    "性格": "用于性格问题时，优先提炼行为倾向、反应方式、优势与盲点；不要把人格写成固定标签。",
    "学业": "用于学业问题时，优先观察学习节奏、基础修补、专注度和外部助力；不宜替代现实学习规划。",
    "家庭": "用于家庭问题时，优先观察责任分配、沟通方式、照应与边界；避免把复杂关系简化成单一责任方。",
    "运势": "用于阶段运势时，优先观察本卦到变卦的走势、动爻所在阶段和需要追问的时间窗口。",
    DEFAULT_DOMAIN: "用于综合问题时，先把卦象作为结构化参考，围绕本卦主轴、动爻焦点和变卦方向提出追问。",
}


def build_hexagram_reading(
    hexagram: Optional[Dict[str, Any]],
    question: str = "",
) -> Optional[Dict[str, Any]]:
    """Build a local, auditable reading scaffold for one hexagram result."""

    if not hexagram:
        return None
    primary = hexagram.get("primary") or {}
    changed = hexagram.get("changed") or {}
    if not primary and not changed:
        return None

    intent = parse_question_intent(question)
    domain = intent.primary_domain
    moving_line = _safe_int(hexagram.get("moving_line"))
    position_rule = LINE_POSITION_RULES.get(moving_line or 0, {})
    moving_name = str(hexagram.get("moving_line_name") or "动爻")
    moving_text = str(hexagram.get("moving_line_text") or "").strip()

    sections = [
        {
            "title": "本卦主轴",
            "summary": _primary_summary(primary),
            "evidence": _primary_evidence(primary),
        },
        {
            "title": "动爻焦点",
            "summary": _moving_line_summary(
                moving_name,
                moving_text,
                position_rule,
            ),
            "evidence": _moving_line_evidence(hexagram, position_rule),
        },
        {
            "title": "变卦方向",
            "summary": _transition_summary(primary, changed),
            "evidence": _transition_evidence(primary, changed),
        },
        {
            "title": f"{domain}问题提示",
            "summary": _domain_summary(domain, primary, changed, moving_name),
            "evidence": _domain_evidence(intent),
        },
    ]

    return {
        "schema_version": HEXAGRAM_READING_SCHEMA_VERSION,
        "domain": domain,
        "intent_confidence": intent.confidence,
        "overview": _overview(primary, changed, moving_name, domain),
        "sections": sections,
        "keywords": _keywords(primary, changed, position_rule, domain),
        "caveats": [
            "本地卦象解读规则只整理结构线索，不把卦象解释为确定事实。",
            "卦象判断需与八字结构、用户问题、现实信息和后续追问一起使用。",
        ],
    }


def _overview(
    primary: Dict[str, Any],
    changed: Dict[str, Any],
    moving_name: str,
    domain: str,
) -> str:
    return (
        f"本卦《{primary.get('name', '-')}》主轴为“{primary.get('theme', '未标注')}”，"
        f"动{moving_name}，"
        f"变卦《{changed.get('name', '-')}》指向“{changed.get('theme', '未标注')}”。"
        f"在{domain}问题中，宜把它作为从当前结构到后续调整方向的参考。"
    )


def _primary_summary(primary: Dict[str, Any]) -> str:
    return (
        f"本卦《{primary.get('name', '-')}》描述当前问题的主场景；"
        f"主题为“{primary.get('theme', '未标注')}”，"
        f"上下卦为 {primary.get('description', '-')}。"
    )


def _primary_evidence(primary: Dict[str, Any]) -> List[str]:
    evidence = [
        f"primary.name={primary.get('name', '-')}",
        f"primary.description={primary.get('description', '-')}",
    ]
    if primary.get("theme"):
        evidence.append(f"primary.theme={primary['theme']}")
    if primary.get("judgment"):
        evidence.append(f"primary.judgment={primary['judgment']}")
    return evidence


def _moving_line_summary(
    moving_name: str,
    moving_text: str,
    position_rule: Dict[str, str],
) -> str:
    stage = position_rule.get("stage", "动爻位置")
    focus = position_rule.get("focus", "重点看此爻对应的变化触发点。")
    text = f"爻辞为“{moving_text}”。" if moving_text else "爻辞未提供。"
    return f"{moving_name}落在“{stage}”，{focus}{text}"


def _moving_line_evidence(
    hexagram: Dict[str, Any],
    position_rule: Dict[str, str],
) -> List[str]:
    evidence = [
        f"moving_line={hexagram.get('moving_line', '-')}",
        f"moving_line_name={hexagram.get('moving_line_name', '-')}",
    ]
    if position_rule.get("stage"):
        evidence.append(f"line_stage={position_rule['stage']}")
    if hexagram.get("moving_line_text"):
        evidence.append(f"moving_line_text={hexagram['moving_line_text']}")
    return evidence


def _transition_summary(primary: Dict[str, Any], changed: Dict[str, Any]) -> str:
    primary_theme = primary.get("theme") or "当前结构"
    changed_theme = changed.get("theme") or "后续变化"
    return (
        f"变卦不是另起一卦，而是本卦动爻变化后的方向；"
        f"这里体现为从“{primary_theme}”转向“{changed_theme}”。"
    )


def _transition_evidence(
    primary: Dict[str, Any],
    changed: Dict[str, Any],
) -> List[str]:
    evidence = [
        f"primary={primary.get('name', '-')}",
        f"changed={changed.get('name', '-')}",
    ]
    if changed.get("theme"):
        evidence.append(f"changed.theme={changed['theme']}")
    if changed.get("judgment"):
        evidence.append(f"changed.judgment={changed['judgment']}")
    return evidence


def _domain_summary(
    domain: str,
    primary: Dict[str, Any],
    changed: Dict[str, Any],
    moving_name: str,
) -> str:
    guidance = DOMAIN_HEXAGRAM_GUIDANCE.get(
        domain,
        DOMAIN_HEXAGRAM_GUIDANCE[DEFAULT_DOMAIN],
    )
    return (
        f"{guidance}"
        f"本卦主题“{primary.get('theme', '-')}”可作为当前状态，"
        f"{moving_name}作为变化触发点，"
        f"变卦主题“{changed.get('theme', '-')}”作为后续调整方向。"
    )


def _domain_evidence(intent: Any) -> List[str]:
    evidence = [
        f"domain={intent.primary_domain}",
        f"intent_confidence={intent.confidence}",
    ]
    if intent.matched_keywords:
        for domain, keywords in intent.matched_keywords.items():
            evidence.append(f"matched_keywords.{domain}={','.join(keywords)}")
    return evidence


def _keywords(
    primary: Dict[str, Any],
    changed: Dict[str, Any],
    position_rule: Dict[str, str],
    domain: str,
) -> List[str]:
    values = [
        domain,
        str(primary.get("theme") or ""),
        str(changed.get("theme") or ""),
        str(position_rule.get("stage") or ""),
    ]
    keywords: List[str] = []
    for value in values:
        for item in value.replace("、", "，").split("，"):
            item = item.strip()
            if item and item not in keywords:
                keywords.append(item)
    return keywords


def _safe_int(value: Any) -> Optional[int]:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


__all__ = [
    "DOMAIN_HEXAGRAM_GUIDANCE",
    "HEXAGRAM_READING_SCHEMA_VERSION",
    "LINE_POSITION_RULES",
    "build_hexagram_reading",
]
