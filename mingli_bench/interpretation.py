"""Structured interpretation contract for MingLi agent outputs."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

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

    def as_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "mode": self.mode,
            "question": self.question,
            "overview": self.overview,
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
"""


def build_local_interpretation(report: ChartReport) -> InterpretationResult:
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
        InterpretationSection(
            title="输入质量",
            summary=_input_quality_summary(report),
            evidence=[
                f"calendar_source={report.input_quality.get('calendar_source')}",
                f"timezone={report.input_quality.get('timezone')}",
                f"has_birth_time={report.input_quality.get('has_birth_time')}",
            ],
            caveats=list(report.caveats),
        ),
    ]
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
) -> InterpretationResult:
    """Parse an LLM response into the interpretation contract when possible."""

    payload = _load_json_object(response)
    if payload is None:
        fallback = build_local_interpretation(report)
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
        sections = build_local_interpretation(report).sections
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


def _load_json_object(text: str) -> Optional[Dict[str, Any]]:
    cleaned = text.strip()
    if not cleaned:
        return None
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start < 0 or end <= start:
            return None
        try:
            parsed = json.loads(cleaned[start : end + 1])
        except json.JSONDecodeError:
            return None
    return parsed if isinstance(parsed, dict) else None


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


__all__ = [
    "INTERPRETATION_SCHEMA_VERSION",
    "InterpretationResult",
    "InterpretationSection",
    "build_local_interpretation",
    "interpretation_prompt_contract",
    "parse_interpretation_response",
]
