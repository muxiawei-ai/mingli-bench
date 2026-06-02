"""Lightweight MingLi agent service layer.

The agent composes deterministic chart calculation with an optional LLM call.
This keeps calendar/Bazi computation local and testable while leaving
interpretation to a model client when one is provided.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .chart_api import BaziChart, ChartInputLike, build_bazi_chart
from .intent import QuestionIntent, parse_question_intent
from .interpretation import (
    InterpretationResult,
    build_local_interpretation,
    interpretation_prompt_contract,
    parse_interpretation_response,
)
from .models.base import ModelClient
from .report import ChartReport, build_chart_report


DEFAULT_AGENT_QUESTION = "请基于这个八字命盘，给出结构化、审慎的中文命理分析。"


@dataclass(frozen=True)
class AgentStage:
    """One auditable step in a MingLi agent run."""

    name: str
    status: str
    summary: str
    data: Dict[str, Any]
    warnings: List[str]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status,
            "summary": self.summary,
            "data": self.data,
            "warnings": self.warnings,
        }


@dataclass(frozen=True)
class AgentResult:
    """JSON-friendly result returned by the MingLi agent."""

    chart: BaziChart
    intent: QuestionIntent
    report: ChartReport
    interpretation: InterpretationResult
    question: str
    prompt: str
    response: Optional[str]
    model: Optional[str]
    warnings: List[str]
    trace: List[AgentStage]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "chart": self.chart.as_dict(),
            "intent": self.intent.as_dict(),
            "report": self.report.as_dict(),
            "interpretation": self.interpretation.as_dict(),
            "question": self.question,
            "prompt": self.prompt,
            "response": self.response,
            "model": self.model,
            "warnings": self.warnings,
            "trace": [stage.as_dict() for stage in self.trace],
        }


def build_interpretation_prompt(
    chart: BaziChart,
    question: str = DEFAULT_AGENT_QUESTION,
    report: Optional[ChartReport] = None,
    intent: Optional[QuestionIntent] = None,
) -> str:
    """Build the prompt sent to an LLM for chart interpretation."""

    report = report or build_chart_report(chart, question)
    intent = intent or parse_question_intent(question)
    intent_json = json.dumps(intent.as_dict(), ensure_ascii=False, indent=2)
    report_json = json.dumps(report.as_dict(), ensure_ascii=False, indent=2)
    chart_json = json.dumps(chart.as_dict(), ensure_ascii=False, indent=2)
    return f"""你是一个中文命理分析 Agent。

请只基于下方 JSON 中的结构化排盘结果进行分析，不要重新发明或猜测四柱。
如果 warnings 中提示地点、历法或时区存在不确定性，请先说明该限制。
本地 report 是程序确定性整理出的命盘摘要和限制条件，请优先使用它作为分析骨架。
如果本地 report.event_years 提供了题目年份的 year_pillar，请直接使用该流年干支，不要自行重算或猜测年份干支。
intent 是程序对用户问题的粗粒度路由，请优先围绕 primary_domain 和 section_hints 组织回答。

输出要求：
1. 遵守下方 JSON 输出契约。
2. 先给出排盘摘要：四柱、日主、五行概况。
3. 再回答用户问题。
4. 保持审慎，不要把命理分析说成确定事实。
5. 如果信息不足，列出需要追问的关键问题。
6. 如果用户问题包含 A/B/C/D 选项，必须逐项比较所有选项，给出 option_scores，并在 answer_choice 中只填一个最终选项字母。
7. answer_confidence 必须与证据强弱一致；若出生时间、地点、时区或题意有不确定性，不要给出高置信度。
8. 不要因为某个选项文字更戏剧化就选择它；必须说明它和四柱、流年、宫位、十神或本地 report 证据的对应关系。
9. 对题目中出现的年份，优先引用本地 report.event_years 中的 year_pillar、age 和 nominal_age；不要把 1996、2008、2020 等年份误写成其他干支。

JSON 输出契约：
{interpretation_prompt_contract()}

用户问题：
{question}

问题 intent JSON：
{intent_json}

本地 report JSON：
{report_json}

结构化排盘 JSON：
{chart_json}
"""


class MingLiAgent:
    """Deterministic chart builder plus optional LLM interpreter."""

    def __init__(self, model_client: Optional[ModelClient] = None):
        self.model_client = model_client

    def run(
        self,
        chart_input: ChartInputLike,
        *,
        question: str = DEFAULT_AGENT_QUESTION,
        fortune_data_path: Optional[str] = None,
    ) -> AgentResult:
        trace = [
            AgentStage(
                name="input",
                status="completed",
                summary="Received chart input and user question.",
                data={
                    "input_type": type(chart_input).__name__,
                    "question_chars": len(question),
                },
                warnings=[],
            )
        ]
        intent = parse_question_intent(question)
        trace.append(
            AgentStage(
                name="intent",
                status="completed",
                summary="Parsed user-question intent.",
                data={
                    "primary_domain": intent.primary_domain,
                    "domains": list(intent.domains),
                    "confidence": intent.confidence,
                    "needs_clarification": intent.needs_clarification,
                },
                warnings=["intent_needs_clarification"] if intent.needs_clarification else [],
            )
        )
        chart = build_bazi_chart(chart_input, fortune_data_path=fortune_data_path)
        trace.append(
            AgentStage(
                name="chart",
                status="completed",
                summary="Built deterministic Bazi chart.",
                data={
                    "pillars_text": chart.pillars.display(),
                    "day_master": chart.day_master,
                    "source": chart.source,
                    "timezone": chart.timezone.get("timezone"),
                },
                warnings=list(chart.warnings),
            )
        )
        report = build_chart_report(chart, question)
        trace.append(
            AgentStage(
                name="report",
                status="completed",
                summary="Built deterministic local report.",
                data={
                    "strongest_elements": list(report.strongest_elements),
                    "missing_elements": list(report.missing_elements),
                    "caveat_count": len(report.caveats),
                    "follow_up_count": len(report.follow_up_questions),
                },
                warnings=[],
            )
        )
        prompt = build_interpretation_prompt(chart, question, report, intent)
        trace.append(
            AgentStage(
                name="prompt",
                status="completed",
                summary="Built LLM interpretation prompt.",
                data={"prompt_chars": len(prompt)},
                warnings=[],
            )
        )
        response = None
        if self.model_client:
            response = self.model_client.generate(prompt)
            trace.append(
                AgentStage(
                    name="llm",
                    status="completed",
                    summary="Called model client for interpretation.",
                    data={
                        "model": self.model_client.model_name,
                        "response_chars": len(response),
                    },
                    warnings=[],
                )
            )
        else:
            trace.append(
                AgentStage(
                    name="llm",
                    status="skipped",
                    summary="No model client configured; returned local chart, report, and prompt only.",
                    data={"model": None},
                    warnings=["llm_not_called"],
                )
            )
        if response:
            interpretation = parse_interpretation_response(response, report, intent)
        else:
            interpretation = build_local_interpretation(report, intent)
        trace.append(
            AgentStage(
                name="interpretation",
                status="completed",
                summary="Built structured interpretation contract.",
                data={
                    "mode": interpretation.mode,
                    "schema_version": interpretation.schema_version,
                    "section_count": len(interpretation.sections),
                    "parsed_from_response": interpretation.parsed_from_response,
                },
                warnings=[
                    caveat
                    for caveat in interpretation.caveats
                    if caveat.startswith("llm_response_")
                ],
            )
        )
        warnings = list(chart.warnings)
        if self.model_client is None:
            warnings.append("llm_not_called")
        return AgentResult(
            chart=chart,
            intent=intent,
            report=report,
            interpretation=interpretation,
            question=question,
            prompt=prompt,
            response=response,
            model=self.model_client.model_name if self.model_client else None,
            warnings=warnings,
            trace=trace,
        )


__all__ = [
    "AgentResult",
    "AgentStage",
    "DEFAULT_AGENT_QUESTION",
    "MingLiAgent",
    "build_interpretation_prompt",
]
