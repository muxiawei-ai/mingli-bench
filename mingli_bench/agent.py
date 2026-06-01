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
from .models.base import ModelClient
from .report import ChartReport, build_chart_report


DEFAULT_AGENT_QUESTION = "请基于这个八字命盘，给出结构化、审慎的中文命理分析。"


@dataclass(frozen=True)
class AgentResult:
    """JSON-friendly result returned by the MingLi agent."""

    chart: BaziChart
    report: ChartReport
    question: str
    prompt: str
    response: Optional[str]
    model: Optional[str]
    warnings: List[str]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "chart": self.chart.as_dict(),
            "report": self.report.as_dict(),
            "question": self.question,
            "prompt": self.prompt,
            "response": self.response,
            "model": self.model,
            "warnings": self.warnings,
        }


def build_interpretation_prompt(
    chart: BaziChart,
    question: str = DEFAULT_AGENT_QUESTION,
    report: Optional[ChartReport] = None,
) -> str:
    """Build the prompt sent to an LLM for chart interpretation."""

    report = report or build_chart_report(chart, question)
    report_json = json.dumps(report.as_dict(), ensure_ascii=False, indent=2)
    chart_json = json.dumps(chart.as_dict(), ensure_ascii=False, indent=2)
    return f"""你是一个中文命理分析 Agent。

请只基于下方 JSON 中的结构化排盘结果进行分析，不要重新发明或猜测四柱。
如果 warnings 中提示地点、历法或时区存在不确定性，请先说明该限制。
本地 report 是程序确定性整理出的命盘摘要和限制条件，请优先使用它作为分析骨架。

输出要求：
1. 先给出排盘摘要：四柱、日主、五行概况。
2. 再回答用户问题。
3. 保持审慎，不要把命理分析说成确定事实。
4. 如果信息不足，列出需要追问的关键问题。

用户问题：
{question}

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
        chart = build_bazi_chart(chart_input, fortune_data_path=fortune_data_path)
        report = build_chart_report(chart, question)
        prompt = build_interpretation_prompt(chart, question, report)
        response = self.model_client.generate(prompt) if self.model_client else None
        warnings = list(chart.warnings)
        if self.model_client is None:
            warnings.append("llm_not_called")
        return AgentResult(
            chart=chart,
            report=report,
            question=question,
            prompt=prompt,
            response=response,
            model=self.model_client.model_name if self.model_client else None,
            warnings=warnings,
        )


__all__ = [
    "AgentResult",
    "DEFAULT_AGENT_QUESTION",
    "MingLiAgent",
    "build_interpretation_prompt",
]
