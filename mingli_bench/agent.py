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
    include_candidate_year_diagnostics: bool = False,
) -> str:
    """Build the prompt sent to an LLM for chart interpretation."""

    report = report or build_chart_report(chart, question)
    intent = intent or parse_question_intent(question)
    intent_json = json.dumps(intent.as_dict(), ensure_ascii=False, indent=2)
    report_for_prompt = report.as_dict()
    report_for_prompt.pop("candidate_year_scores", None)
    candidate_year_diagnostics = (
        _candidate_year_prompt_diagnostics(report)
        if include_candidate_year_diagnostics
        else None
    )
    candidate_year_instruction = ""
    candidate_year_requirement = ""
    if candidate_year_diagnostics:
        report_for_prompt["candidate_year_diagnostics"] = candidate_year_diagnostics
        candidate_year_instruction = "\n如果本地 report.candidate_year_diagnostics 提供了 activation_weighted 候选年份诊断，请只把它当作本地规则参考，不要把它当作标准答案；必须仍然逐项比较所有选项，并说明采纳或不采纳该诊断 top 候选的理由。"
        candidate_year_requirement = "\n13. 对候选年份题，可以引用本地 report.candidate_year_diagnostics 中的 activation_rank、activation_score、interaction_labels 和 matched_positions 作为辅助诊断；这些字段不是答案，不能代替你对四柱、流年和题意的独立比较。"
    report_json = json.dumps(report_for_prompt, ensure_ascii=False, indent=2)
    chart_json = json.dumps(chart.as_dict(), ensure_ascii=False, indent=2)
    return f"""你是一个中文命理分析 Agent。

请只基于下方 JSON 中的结构化排盘结果进行分析，不要重新发明或猜测四柱。
如果 warnings 中提示地点、历法或时区存在不确定性，请先说明该限制。
本地 report 是程序确定性整理出的命盘摘要和限制条件，请优先使用它作为分析骨架。
如果本地 report.event_years 提供了题目年份的 year_pillar，请直接使用该流年干支，不要自行重算或猜测年份干支。
如果本地 report.event_years 提供了 branch_interactions，请直接引用其中的 label，不要自行编造三合、三会、六合、六冲名称。
如果本地 report.option_semantics 提供了选项事件类型，请只把它当作选项文字的语义标签，不要把它当作标准答案或命理加分依据。
如果本地 report.hexagram 提供了卦象结构，请只引用其中的本卦、变卦、动爻、起卦依据、已提供的卦辞/爻辞字段和 reading 规则解读；不要自行重新起卦，也不要补造经典爻辞。
如果本地 report.integrated_analysis 提供了八字+卦象联合分析，请优先用它组织综合判断；不要把八字和卦象写成彼此无关的两段。
{candidate_year_instruction}
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
10. 对流年地支关系，优先引用本地 report.event_years.branch_interactions 中的 label 和 element；如果没有对应关系，请说明本地规则未检出主要冲合会合。
11. 对 A/B/C/D 选项，可以引用本地 report.option_semantics 中的 primary_event_type、labels 和 matched_keywords 来说明选项文字含义；评分必须来自 chart/report 的干支、流年、地支关系与选项文本的直接对应。不要因为标签中出现婚恋、财运、健康或意外就自动加分，也不要只因为“意外”“车祸”等词更具体就选择它。
12. 如果引用卦象，只能引用本地 report.hexagram 的确定性字段和 report.hexagram.reading 的规则解读；不要自行补造卦辞、爻辞或重新起卦。
13. 如果 report.integrated_analysis 存在，请至少引用其中一个 sections 条目或 alignment_signals 条目来说明八字与卦象如何互相参考。
{candidate_year_requirement}

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


def _candidate_year_prompt_diagnostics(report: ChartReport) -> Optional[Dict[str, Any]]:
    scores = report.candidate_year_scores
    if not scores:
        return None
    variant = "activation_weighted"
    candidates = []
    for item in scores:
        variant_ranks = item.get("variant_ranks") or {}
        variant_scores = item.get("variant_scores") or {}
        if variant not in variant_ranks or variant not in variant_scores:
            continue
        candidates.append(
            {
                "letter": item.get("letter"),
                "text": item.get("text"),
                "year": item.get("year"),
                "year_pillar": item.get("year_pillar"),
                "focus": item.get("focus"),
                "activation_rank": variant_ranks.get(variant),
                "activation_score": variant_scores.get(variant),
                "default_rank": item.get("rank"),
                "interaction_labels": item.get("interaction_labels") or [],
                "matched_positions": item.get("matched_positions") or [],
            }
        )
    if not candidates:
        return None
    ranked = sorted(
        candidates,
        key=lambda item: (
            int(item.get("activation_rank") or 999),
            -float(item.get("activation_score") or 0.0),
        ),
    )
    return {
        "variant": variant,
        "note": "local_candidate_year_diagnostic_not_gold_label",
        "top_candidate": ranked[0].get("letter"),
        "candidates": candidates,
    }


class MingLiAgent:
    """Deterministic chart builder plus optional LLM interpreter."""

    def __init__(
        self,
        model_client: Optional[ModelClient] = None,
        *,
        include_candidate_year_diagnostics: bool = False,
    ):
        self.model_client = model_client
        self.include_candidate_year_diagnostics = include_candidate_year_diagnostics

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
                    "has_hexagram": report.hexagram is not None,
                    "caveat_count": len(report.caveats),
                    "follow_up_count": len(report.follow_up_questions),
                },
                warnings=[],
            )
        )
        prompt = build_interpretation_prompt(
            chart,
            question,
            report,
            intent,
            include_candidate_year_diagnostics=(
                self.include_candidate_year_diagnostics
            ),
        )
        trace.append(
            AgentStage(
                name="prompt",
                status="completed",
                summary="Built LLM interpretation prompt.",
                data={
                    "prompt_chars": len(prompt),
                    "include_candidate_year_diagnostics": (
                        self.include_candidate_year_diagnostics
                    ),
                },
                warnings=[],
            )
        )
        response = None
        if self.model_client:
            response = self.model_client.generate(prompt)
            llm_data = {
                "model": self.model_client.model_name,
                "response_chars": len(response),
            }
            cache_hit = getattr(self.model_client, "last_cache_hit", None)
            if cache_hit is not None:
                llm_data["cache_hit"] = bool(cache_hit)
                llm_data["cache_key"] = getattr(self.model_client, "last_cache_key", None)
                llm_data["cache_path"] = getattr(self.model_client, "last_cache_path", None)
            trace.append(
                AgentStage(
                    name="llm",
                    status="completed",
                    summary=(
                        "Used cached model response for interpretation."
                        if cache_hit
                        else "Called model client for interpretation."
                    ),
                    data=llm_data,
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
