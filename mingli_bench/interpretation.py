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
如果 report.question_hexagram 存在，sections 中应包含“问事卦象参考”，并与 report.hexagram 的本命卦象参考分开说明。
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
    if report.bazi_profile:
        sections.append(
            InterpretationSection(
                title="八字画像",
                summary=_bazi_profile_summary(report),
                evidence=_bazi_profile_evidence(report),
                caveats=list(report.bazi_profile.get("caveats") or []),
            )
        )
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
    if report.dayun:
        sections.append(
            InterpretationSection(
                title="大运时间轴",
                summary=_dayun_summary(report),
                evidence=_dayun_evidence(report),
                caveats=list(report.dayun.get("caveats") or []),
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
    if report.hexagram:
        sections.append(
            InterpretationSection(
                title="本命卦象参考",
                summary=_hexagram_summary(report),
                evidence=_hexagram_evidence(report),
                caveats=list(report.hexagram.get("caveats") or []),
            )
        )
    if report.question_hexagram:
        sections.append(
            InterpretationSection(
                title="问事卦象参考",
                summary=_question_hexagram_summary(report),
                evidence=_question_hexagram_evidence(report),
                caveats=list(report.question_hexagram.get("caveats") or []),
            )
        )
    if report.integrated_analysis:
        sections.append(
            InterpretationSection(
                title="八字卦象联合分析",
                summary=_integrated_summary(report),
                evidence=_integrated_evidence(report),
                caveats=list(report.integrated_analysis.get("caveats") or []),
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


def _bazi_profile_summary(report: ChartReport) -> str:
    profile = report.bazi_profile or {}
    return str(profile.get("overview") or "")


def _bazi_profile_evidence(report: ChartReport) -> List[str]:
    profile = report.bazi_profile or {}
    evidence: List[str] = []
    strength = profile.get("day_master_strength") or {}
    if strength:
        evidence.append(
            "day_master_strength="
            f"{strength.get('label')} support_index={strength.get('support_index')}"
        )
    groups = profile.get("ten_god_groups") or {}
    for key, payload in groups.items():
        evidence.append(
            f"ten_god_group.{key}={payload.get('label')}:"
            f"visible={payload.get('count')},"
            f"weighted={payload.get('weighted_count', payload.get('count'))}"
        )
    hidden_stems = profile.get("hidden_stems") or []
    if hidden_stems:
        evidence.append(f"hidden_stems_count={len(hidden_stems)}")
    for signal in profile.get("structure_signals") or []:
        if signal.get("label") and signal.get("summary"):
            evidence.append(f"{signal['label']}: {signal['summary']}")
    return evidence


def _dayun_summary(report: ChartReport) -> str:
    dayun = report.dayun or {}
    if not dayun.get("available"):
        missing = "、".join(dayun.get("missing_inputs") or [])
        return f"大运未生成，缺少{missing or '必要输入'}。"
    start = dayun.get("start_timing") or {}
    overlays = dayun.get("event_overlays") or []
    overlay_text = ""
    if overlays:
        first = overlays[0]
        active = first.get("active_cycle") or {}
        if active:
            overlay_text = f"题目年份 {first['year']} 约落在 {active.get('pillar')} 大运。"
    return (
        f"大运按{dayun.get('direction_label')}生成，"
        f"起运约 {start.get('start_age_years')} 岁。{overlay_text}"
    )


def _dayun_evidence(report: ChartReport) -> List[str]:
    dayun = report.dayun or {}
    evidence: List[str] = []
    if not dayun:
        return evidence
    evidence.append(f"dayun.available={dayun.get('available')}")
    if dayun.get("direction_label"):
        evidence.append(f"direction={dayun.get('direction_label')}")
    start = dayun.get("start_timing") or {}
    if start:
        evidence.append(
            "start_timing="
            f"{start.get('start_age_years')}岁 via {start.get('anchor_term')}"
        )
    for cycle in (dayun.get("cycles") or [])[:4]:
        evidence.append(
            f"cycle.{cycle.get('index')}="
            f"{cycle.get('pillar')} age={cycle.get('age_start')}-{cycle.get('age_end')}"
        )
    for overlay in dayun.get("event_overlays") or []:
        active = overlay.get("active_cycle") or {}
        if active:
            evidence.append(
                f"event_year.{overlay.get('year')}="
                f"{active.get('pillar')}大运"
            )
    return evidence


def _hexagram_summary(report: ChartReport) -> str:
    hexagram = report.hexagram or {}
    return _format_hexagram_summary(hexagram, "本命卦")


def _question_hexagram_summary(report: ChartReport) -> str:
    hexagram = report.question_hexagram or {}
    return _format_hexagram_summary(hexagram, "问事卦")


def _format_hexagram_summary(hexagram: Dict[str, Any], role_label: str) -> str:
    reading = hexagram.get("reading") or {}
    if reading.get("overview"):
        return f"{role_label}：{reading['overview']}"
    primary = hexagram.get("primary") or {}
    changed = hexagram.get("changed") or {}
    return (
        f"{role_label}由本地梅花易数时间法生成，本卦《{primary.get('name', '-')}》"
        f"（{primary.get('description', '-')}），"
        f"动{hexagram.get('moving_line_name', '-')}，"
        f"变卦为《{changed.get('name', '-')}》"
        f"（{changed.get('description', '-')}）。"
    )


def _hexagram_evidence(report: ChartReport) -> List[str]:
    hexagram = report.hexagram or {}
    return _format_hexagram_evidence(hexagram, "hexagram")


def _question_hexagram_evidence(report: ChartReport) -> List[str]:
    hexagram = report.question_hexagram or {}
    return _format_hexagram_evidence(hexagram, "question_hexagram")


def _format_hexagram_evidence(hexagram: Dict[str, Any], prefix: str) -> List[str]:
    evidence = [str(item) for item in hexagram.get("basis") or []]
    if hexagram.get("time_source_label"):
        evidence.append(f"{prefix}.time_source_label: {hexagram['time_source_label']}")
    if hexagram.get("input_datetime"):
        evidence.append(f"{prefix}.input_datetime: {hexagram['input_datetime']}")
    if hexagram.get("moving_line_text"):
        evidence.append(
            f"moving_line_text: {hexagram.get('moving_line_name', '-')}"
            f" {hexagram['moving_line_text']}"
        )
    reading = hexagram.get("reading") or {}
    for section in reading.get("sections") or []:
        title = section.get("title")
        summary = section.get("summary")
        if title and summary:
            evidence.append(f"{title}: {summary}")
    source = hexagram.get("number_source") or {}
    if source:
        evidence.append(
            "number_source="
            + ",".join(
                f"{key}:{value}"
                for key, value in source.items()
                if value is not None
            )
        )
    return evidence


def _integrated_summary(report: ChartReport) -> str:
    integrated = report.integrated_analysis or {}
    return str(integrated.get("overview") or "")


def _integrated_evidence(report: ChartReport) -> List[str]:
    integrated = report.integrated_analysis or {}
    evidence: List[str] = []
    for section in integrated.get("sections") or []:
        title = section.get("title")
        summary = section.get("summary")
        if title and summary:
            evidence.append(f"{title}: {summary}")
    for signal in integrated.get("alignment_signals") or []:
        label = signal.get("label")
        evidence_text = signal.get("evidence")
        implication = signal.get("implication")
        if label and evidence_text:
            evidence.append(f"{label}: {evidence_text}; {implication or ''}")
    return evidence


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

    # Strip markdown code fences (```json ... ```) that models often wrap responses in
    if cleaned.startswith("```"):
        first_newline = cleaned.find("\n")
        if first_newline >= 0:
            end_fence = cleaned.rfind("```")
            if end_fence > first_newline:
                cleaned = cleaned[first_newline + 1 : end_fence].strip()

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
