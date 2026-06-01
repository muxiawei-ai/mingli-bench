"""Deterministic local report helpers for MingLi agent outputs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .chart_api import BaziChart


ELEMENT_ORDER = ["木", "火", "土", "金", "水"]
GENERATES = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
CONTROLS = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}


@dataclass(frozen=True)
class ElementSignal:
    """One five-element signal derived from the visible four pillars."""

    element: str
    count: int
    level: str
    relation_to_day_master: Optional[str]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "element": self.element,
            "count": self.count,
            "level": self.level,
            "relation_to_day_master": self.relation_to_day_master,
        }


@dataclass(frozen=True)
class ChartReport:
    """JSON-friendly deterministic report for agent/UI/API integrations."""

    question: str
    summary: Dict[str, Any]
    element_profile: List[ElementSignal]
    strongest_elements: List[str]
    missing_elements: List[str]
    input_quality: Dict[str, Any]
    caveats: List[str]
    follow_up_questions: List[str]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "question": self.question,
            "summary": self.summary,
            "element_profile": [signal.as_dict() for signal in self.element_profile],
            "strongest_elements": self.strongest_elements,
            "missing_elements": self.missing_elements,
            "input_quality": self.input_quality,
            "caveats": self.caveats,
            "follow_up_questions": self.follow_up_questions,
        }

    def to_markdown(self) -> str:
        """Render the report as compact Markdown for terminal display."""

        summary = self.summary
        lines = [
            "## 本地结构化报告",
            "",
            "### 命盘摘要",
            f"- 四柱: {summary['pillars_text']}",
            f"- 日主: {summary['day_master']} ({summary.get('day_master_element') or '未知'})",
            f"- 公历日期: {summary['solar_date']}",
            f"- 八字换日日期: {summary['bazi_day_date']}",
            f"- 时辰: {summary.get('hour_branch') or '未知'}",
            "",
            "### 五行分布",
        ]
        for signal in self.element_profile:
            relation = (
                f", {signal.relation_to_day_master}"
                if signal.relation_to_day_master
                else ""
            )
            lines.append(
                f"- {signal.element}: {signal.count} ({signal.level}{relation})"
            )

        if self.strongest_elements:
            lines.append(f"- 相对较多: {'、'.join(self.strongest_elements)}")
        if self.missing_elements:
            lines.append(f"- 未见元素: {'、'.join(self.missing_elements)}")

        lines.extend(["", "### 输入与限制"])
        lines.append(f"- 历法来源: {self.input_quality['calendar_source']}")
        lines.append(
            "- 时区: "
            f"{self.input_quality['timezone']} "
            f"({self.input_quality['normalized_location']})"
        )
        lines.append(
            f"- 出生时间: {'已提供' if self.input_quality['has_birth_time'] else '未知'}"
        )
        if self.caveats:
            for caveat in self.caveats:
                lines.append(f"- {caveat}")

        if self.follow_up_questions:
            lines.extend(["", "### 建议追问"])
            for question in self.follow_up_questions:
                lines.append(f"- {question}")
        return "\n".join(lines)


def classify_element_count(count: int) -> str:
    """Classify a visible element count across the eight pillar characters."""

    if count <= 0:
        return "absent"
    if count == 1:
        return "light"
    if count == 2:
        return "present"
    return "high"


def relation_to_day_master(element: str, day_master_element: Optional[str]) -> Optional[str]:
    """Describe a five-phase structural relation to the day-master element."""

    if not day_master_element or element not in ELEMENT_ORDER:
        return None
    if element == day_master_element:
        return "same_as_day_master"
    if GENERATES.get(day_master_element) == element:
        return "generated_by_day_master"
    if GENERATES.get(element) == day_master_element:
        return "generates_day_master"
    if CONTROLS.get(day_master_element) == element:
        return "controlled_by_day_master"
    if CONTROLS.get(element) == day_master_element:
        return "controls_day_master"
    return None


def build_element_profile(chart: BaziChart) -> List[ElementSignal]:
    """Build a stable five-element profile from a chart."""

    return [
        ElementSignal(
            element=element,
            count=int(chart.five_elements_summary.get(element, 0)),
            level=classify_element_count(int(chart.five_elements_summary.get(element, 0))),
            relation_to_day_master=relation_to_day_master(
                element,
                chart.day_master_element,
            ),
        )
        for element in ELEMENT_ORDER
    ]


def build_chart_report(chart: BaziChart, question: str) -> ChartReport:
    """Create a deterministic report scaffold for local agent output."""

    profile = build_element_profile(chart)
    max_count = max(signal.count for signal in profile)
    strongest_elements = [
        signal.element for signal in profile if signal.count == max_count and max_count > 0
    ]
    missing_elements = [signal.element for signal in profile if signal.count == 0]

    summary = {
        "pillars_text": chart.pillars.display(),
        "year_pillar": chart.pillars.year,
        "month_pillar": chart.pillars.month,
        "day_pillar": chart.pillars.day,
        "hour_pillar": chart.pillars.hour,
        "day_master": chart.day_master,
        "day_master_element": chart.day_master_element,
        "solar_date": chart.solar_date,
        "bazi_day_date": chart.bazi_day_date,
        "hour_branch": chart.hour_branch,
        "lunar": chart.lunar,
    }
    input_quality = {
        "calendar_type": chart.input.calendar_type,
        "calendar_source": chart.source,
        "timezone": chart.timezone.get("timezone"),
        "utc_offset_hours": chart.timezone.get("utc_offset_hours"),
        "normalized_location": chart.timezone.get("normalized_location"),
        "has_birth_time": chart.input.hour is not None,
        "warnings": list(chart.warnings),
    }
    caveats = _build_caveats(chart)
    follow_up_questions = _build_follow_up_questions(chart, question)
    return ChartReport(
        question=question,
        summary=summary,
        element_profile=profile,
        strongest_elements=strongest_elements,
        missing_elements=missing_elements,
        input_quality=input_quality,
        caveats=caveats,
        follow_up_questions=follow_up_questions,
    )


def _build_caveats(chart: BaziChart) -> List[str]:
    caveats = [
        "本地报告只整理排盘结构，不把命理分析表述为确定事实。",
    ]
    if chart.input.hour is None:
        caveats.append("出生时间未知，时柱为空，涉及时柱的判断需要谨慎。")
    if "lunar_conversion_uses_fixture_index" in chart.warnings:
        caveats.append("农历转公历目前使用仓库 fixture 索引，不是完整农历引擎。")
    if chart.timezone.get("warnings"):
        caveats.append("出生地或时区存在标准化假设，建议核对具体城市。")
    if chart.warnings:
        caveats.append("原始 warnings: " + ", ".join(chart.warnings))
    return caveats


def _build_follow_up_questions(chart: BaziChart, question: str) -> List[str]:
    questions: List[str] = []
    if chart.input.hour is None:
        questions.append("能否补充准确出生时间，或至少说明上午/下午/晚上？")
    if not chart.input.location:
        questions.append("能否补充出生地，用于确认时区和日期边界？")
    if not question.strip() or question == "请基于这个八字命盘，给出结构化、审慎的中文命理分析。":
        questions.append("用户更关心事业、感情、健康、财运，还是阶段性运势？")
    if chart.input.calendar_type == "lunar":
        questions.append("农历生日是否确认包含闰月信息？")
    return questions


__all__ = [
    "ChartReport",
    "ElementSignal",
    "build_chart_report",
    "build_element_profile",
    "classify_element_count",
    "relation_to_day_master",
]
