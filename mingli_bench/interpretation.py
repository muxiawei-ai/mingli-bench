"""Structured interpretation contract for MingLi agent outputs."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .intent import QuestionIntent
from .report import ChartReport


INTERPRETATION_SCHEMA_VERSION = "mingli_interpretation.v1"


@dataclass(frozen=True)
class InterpretationSection:
    """One structured section in a MingLi interpretation."""

    title: str
    summary: str
    evidence: List[str]
    caveats: List[str]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "summary": self.summary,
            "evidence": self.evidence,
            "caveats": self.caveats,
        }


@dataclass(frozen=True)
class InterpretationResult:
    """Versioned, JSON-friendly interpretation contract."""

    schema_version: str
    mode: str
    question: str
    overview: str
    sections: List[InterpretationSection]
    follow_up_questions: List[str]
    caveats: List[str]
    parsed_from_response: bool
    raw_response: Optional[str]
    answer_choice: Optional[str] = None
    answer_confidence: Optional[float] = None
    option_scores: Optional[Dict[str, Any]] = None

    def as_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "mode": self.mode,
            "question": self.question,
            "overview": self.overview,
            "answer_choice": self.answer_choice,
            "answer_confidence": self.answer_confidence,
            "option_scores": self.option_scores,
            "sections": [section.as_dict() for section in self.sections],
            "follow_up_questions": self.follow_up_questions,
            "caveats": self.caveats,
            "parsed_from_response": self.parsed_from_response,
            "raw_response": self.raw_response,
        }

    def to_markdown(self) -> str:
        """Render a compact human-readable interpretation."""

        lines = [
            f"概览: {self.overview}",
            f"模式: {self.mode}",
        ]
        if self.answer_choice:
            confidence = (
                f"；置信度: {self.answer_confidence:.2f}"
                if self.answer_confidence is not None
                else ""
            )
            lines.append(f"答案选项: {self.answer_choice}{confidence}")
        for section in self.sections:
            lines.extend(["", f"### {section.title}", section.summary])
            if section.evidence:
                lines.append("依据: " + "；".join(section.evidence))
            if section.caveats:
                lines.append("限制: " + "；".join(section.caveats))
        if self.follow_up_questions:
            lines.extend(["", "### 建议追问"])
            for question in self.follow_up_questions:
                lines.append(f"- {question}")
        if self.caveats:
            lines.extend(["", "### 整体限制"])
            for caveat in self.caveats:
                lines.append(f"- {caveat}")
        return "\n".join(lines)


def interpretation_prompt_contract() -> str:
    """Return the prompt instructions for structured LLM output."""

    return f"""请严格输出一个 JSON object，不要输出 Markdown，不要使用代码块。
JSON 必须符合以下结构：
{{
  "schema_version": "{INTERPRETATION_SCHEMA_VERSION}",
  "overview": "一句话总览，保持审慎",
  "answer_choice": null,
  "answer_confidence": null,
  "option_scores": null,
  "sections": [
    {{
      "title": "排盘摘要",
      "summary": "这一段的结构化解读",
      "evidence": ["引用 report 或 chart 中的具体字段"],
      "caveats": ["这一段的不确定性"]
    }}
  ],
  "follow_up_questions": ["如果信息不足，需要追问的问题"],
  "caveats": ["整体限制和不确定性"]
}}
如果用户问题包含 A/B/C/D 选项，请在 answer_choice 中给出最终选择（"A"、"B"、"C" 或 "D"）。
如果没有选项或无法判断，请使用 null。answer_confidence 为 0 到 1 之间的小数，表示对该选项的审慎置信度。
如果用户问题包含 A/B/C/D 选项，请在 option_scores 中为每个选项给出 0 到 1 的分数和一句理由，例如：
{{"A": {{"score": 0.2, "rationale": "与流年证据较弱"}}, "B": {{"score": 0.7, "rationale": "与夫妻宫证据较强"}}}}
"""


def build_local_interpretation(
    report: ChartReport,
    intent: Optional[QuestionIntent] = None,
) -> InterpretationResult:
    """Build a deterministic local interpretation scaffold without LLM claims."""

    summary = report.summary
    sections = [
        InterpretationSection(
            title="排盘摘要",
            summary=(
                f"四柱为 {summary['pillars_text']}，日主为 "
                f"{summary['day_master']}（{summary.get('day_master_element') or '未知'}）。"
            ),
            evidence=[
                f"pillars_text={summary['pillars_text']}",
                f"day_master={summary['day_master']}",
                f"day_master_element={summary.get('day_master_element')}",
            ],
            caveats=[],
        ),
        InterpretationSection(
            title="五行观察",
            summary=_element_summary(report),
            evidence=[
                "strongest_elements=" + ",".join(report.strongest_elements),
                "missing_elements=" + ",".join(report.missing_elements),
            ],
            caveats=["这是基于四柱显性天干地支的数量统计，不等同于完整格局判断。"],
        ),
    ]
    if report.event_years:
        sections.append(
            InterpretationSection(
                title="题目年份关系",
                summary=_event_years_summary(report),
                evidence=_event_years_evidence(report),
                caveats=[
                    "这是本地规则检出的流年干支与原局地支关系，不等同于最终事件判断。",
                ],
            )
        )
    if report.option_semantics:
        sections.append(
            InterpretationSection(
                title="选项语义标签",
                summary=_option_semantics_summary(report),
                evidence=_option_semantics_evidence(report),
                caveats=[
                    "这是从选项文字抽取的事件类型标签，不代表标准答案。",
                ],
            )
        )
    sections.append(
        InterpretationSection(
            title="输入质量",
            summary=_input_quality_summary(report),
            evidence=[
                f"calendar_source={report.input_quality.get('calendar_source')}",
                f"timezone={report.input_quality.get('timezone')}",
                f"has_birth_time={report.input_quality.get('has_birth_time')}",
            ],
            caveats=list(report.caveats),
        )
    )
    if intent is not None:
        sections.append(
            InterpretationSection(
                title=f"{intent.primary_domain}问题路由",
                summary=(
                    f"用户问题被归入 {intent.primary_domain} 方向；"
                    f"建议围绕 {'、'.join(intent.section_hints)} 展开。"
                ),
                evidence=[
                    "domains=" + ",".join(intent.domains),
                    f"confidence={intent.confidence}",
                ],
                caveats=(
                    ["问题方向较宽，建议先追问具体关注点。"]
                    if intent.needs_clarification
                    else []
                ),
            )
        )
    return InterpretationResult(
        schema_version=INTERPRETATION_SCHEMA_VERSION,
        mode="local",
        question=report.question,
        overview="本地模式只提供排盘结构和可审计观察，不生成确定性命理断语。",
        sections=sections,
        follow_up_questions=list(report.follow_up_questions),
        caveats=list(report.caveats),
        parsed_from_response=False,
        raw_response=None,
    )


def parse_interpretation_response(
    response: str,
    report: ChartReport,
    intent: Optional[QuestionIntent] = None,
) -> InterpretationResult:
    """Parse an LLM response into the interpretation contract when possible."""

    payload = _load_json_object(response)
    if payload is None:
        fallback = build_local_interpretation(report, intent)
        return InterpretationResult(
            schema_version=fallback.schema_version,
            mode="llm_text",
            question=report.question,
            overview=response.strip(),
            sections=fallback.sections,
            follow_up_questions=fallback.follow_up_questions,
            caveats=fallback.caveats + ["llm_response_not_valid_json"],
            parsed_from_response=False,
            raw_response=response,
        )

    sections = [
        _section_from_mapping(section)
        for section in _as_list(payload.get("sections"))
    ]
    if not sections:
        sections = build_local_interpretation(report, intent).sections
    return InterpretationResult(
        schema_version=str(
            payload.get("schema_version") or INTERPRETATION_SCHEMA_VERSION
        ),
        mode="llm_json",
        question=report.question,
        overview=str(payload.get("overview") or "").strip(),
        sections=sections,
        follow_up_questions=[
            str(item) for item in _as_list(payload.get("follow_up_questions"))
        ],
        caveats=[str(item) for item in _as_list(payload.get("caveats"))],
        parsed_from_response=True,
        raw_response=response,
        answer_choice=_normalize_answer_choice(payload.get("answer_choice")),
        answer_confidence=_normalize_confidence(payload.get("answer_confidence")),
        option_scores=_normalize_option_scores(payload.get("option_scores")),
    )


def _element_summary(report: ChartReport) -> str:
    strongest = "、".join(report.strongest_elements) or "无"
    missing = "、".join(report.missing_elements) or "无"
    return f"显性五行中相对较多的是 {strongest}；未见元素为 {missing}。"


def _input_quality_summary(report: ChartReport) -> str:
    time_text = "已提供" if report.input_quality.get("has_birth_time") else "未知"
    return (
        f"历法来源为 {report.input_quality.get('calendar_source')}，"
        f"时区为 {report.input_quality.get('timezone')}，出生时间{time_text}。"
    )


def _event_years_summary(report: ChartReport) -> str:
    parts = []
    for item in report.event_years:
        labels = [
            interaction.get("label")
            for interaction in item.get("branch_interactions") or []
            if interaction.get("label")
        ]
        label_text = "、".join(labels) if labels else "未检出主要冲合会合"
        age_text = (
            f"，实岁约{item['age']}岁"
            if item.get("age") is not None
            else ""
        )
        parts.append(
            f"{item.get('year')}年为{item.get('year_pillar')}流年{age_text}；"
            f"地支关系：{label_text}。"
        )
    return " ".join(parts)


def _event_years_evidence(report: ChartReport) -> List[str]:
    evidence = []
    for item in report.event_years:
        evidence.append(f"event_year={item.get('year')}:{item.get('year_pillar')}")
        for interaction in item.get("branch_interactions") or []:
            label = interaction.get("label")
            if label:
                evidence.append(f"branch_interaction={label}")
    return evidence


def _option_semantics_summary(report: ChartReport) -> str:
    parts = []
    for item in report.option_semantics:
        labels = "、".join(item.get("labels") or []) or "unknown"
        parts.append(f"{item.get('letter')}={labels}")
    return "；".join(parts) + "。"


def _option_semantics_evidence(report: ChartReport) -> List[str]:
    evidence = []
    for item in report.option_semantics:
        event_type = item.get("primary_event_type") or "unknown"
        letter = item.get("letter")
        evidence.append(f"option_{letter}_primary_event_type={event_type}")
        for event_type, keywords in (item.get("matched_keywords") or {}).items():
            evidence.append(
                f"option_{letter}_{event_type}_keywords={','.join(keywords)}"
            )
    return evidence


def _load_json_object(text: str) -> Optional[Dict[str, Any]]:
    cleaned = text.strip()
    if not cleaned:
        return None

    candidates = [cleaned]
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start >= 0 and end > start:
        candidates.append(cleaned[start : end + 1])

    for candidate in candidates:
        parsed = _loads_json_object_candidate(candidate)
        if parsed is not None:
            return parsed
    return None


def _loads_json_object_candidate(text: str, *, max_depth: int = 3) -> Optional[Dict[str, Any]]:
    """Parse a JSON object, including common double-encoded model responses."""

    current: Any = text
    for _ in range(max_depth + 1):
        if isinstance(current, dict):
            return current
        if not isinstance(current, str):
            return None
        current = _loads_json_value(current)
        if current is None:
            return None
    return current if isinstance(current, dict) else None


def _loads_json_value(text: str) -> Optional[Any]:
    """Load JSON with small repairs for common model formatting slips."""

    cleaned = text.strip()
    for candidate in (
        cleaned,
        _escape_control_chars_in_json_strings(cleaned),
        _remove_trailing_commas(cleaned),
        _remove_trailing_commas(_escape_control_chars_in_json_strings(cleaned)),
    ):
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            continue
    return None


def _escape_control_chars_in_json_strings(text: str) -> str:
    """Escape literal newlines/tabs when a model leaves them inside JSON strings."""

    result = []
    in_string = False
    escape = False
    for char in text:
        if escape:
            result.append(char)
            escape = False
            continue
        if char == "\\":
            result.append(char)
            escape = True
            continue
        if char == '"':
            result.append(char)
            in_string = not in_string
            continue
        if in_string and char == "\n":
            result.append("\\n")
            continue
        if in_string and char == "\r":
            result.append("\\r")
            continue
        if in_string and char == "\t":
            result.append("\\t")
            continue
        result.append(char)
    return "".join(result)


def _remove_trailing_commas(text: str) -> str:
    return re.sub(r",\s*([}\]])", r"\1", text)


def _section_from_mapping(payload: Any) -> InterpretationSection:
    if not isinstance(payload, dict):
        return InterpretationSection(
            title="未命名段落",
            summary=str(payload),
            evidence=[],
            caveats=[],
        )
    return InterpretationSection(
        title=str(payload.get("title") or "未命名段落"),
        summary=str(payload.get("summary") or ""),
        evidence=[str(item) for item in _as_list(payload.get("evidence"))],
        caveats=[str(item) for item in _as_list(payload.get("caveats"))],
    )


def _as_list(value: Any) -> List[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _normalize_answer_choice(value: Any) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip().upper()
    return text if text in {"A", "B", "C", "D"} else None


def _normalize_confidence(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        confidence = float(value)
    except (TypeError, ValueError):
        return None
    return min(max(confidence, 0.0), 1.0)


def _normalize_option_scores(value: Any) -> Optional[Dict[str, Any]]:
    if not isinstance(value, dict):
        return None
    normalized: Dict[str, Any] = {}
    for raw_key, raw_item in value.items():
        key = _normalize_answer_choice(raw_key)
        if not key:
            continue
        if isinstance(raw_item, dict):
            normalized[key] = {
                "score": _normalize_confidence(raw_item.get("score")),
                "rationale": str(raw_item.get("rationale") or ""),
            }
        else:
            normalized[key] = {
                "score": _normalize_confidence(raw_item),
                "rationale": "",
            }
    return normalized or None


__all__ = [
    "INTERPRETATION_SCHEMA_VERSION",
    "InterpretationResult",
    "InterpretationSection",
    "build_local_interpretation",
    "interpretation_prompt_contract",
    "parse_interpretation_response",
]
