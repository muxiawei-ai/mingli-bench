"""Agent pipeline evaluation helpers for MingLi-Bench."""

from __future__ import annotations

import json
import time
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .agent import MingLiAgent
from .data.loader import DataLoader
from .interpretation import INTERPRETATION_SCHEMA_VERSION
from .models.base import ModelClient


EXPECTED_TRACE = ["input", "intent", "chart", "report", "prompt", "llm", "interpretation"]


@dataclass(frozen=True)
class AgentEvalConfig:
    """Configuration for an agent evaluation run."""

    sample_size: Optional[int] = None
    year: Optional[int] = None
    categories: Optional[List[str]] = None
    data_path: Optional[str] = None
    fortune_data_path: Optional[str] = None
    model_name: Optional[str] = None
    output_dir: str = "logs"
    save: bool = True

    def as_dict(self) -> Dict[str, Any]:
        return {
            "sample_size": self.sample_size,
            "year": self.year,
            "categories": self.categories,
            "data_path": self.data_path,
            "fortune_data_path": self.fortune_data_path,
            "model_name": self.model_name,
            "output_dir": self.output_dir,
            "save": self.save,
        }


def load_agent_eval_questions(config: AgentEvalConfig) -> List[Dict[str, Any]]:
    """Load benchmark questions for agent pipeline evaluation."""

    loader = DataLoader(config.data_path)
    return loader.load_questions(
        sample_size=config.sample_size,
        year=config.year,
        categories=config.categories,
        shuffle=False,
        shuffle_options=False,
    )


def evaluate_agent_questions(
    questions: Iterable[Dict[str, Any]],
    *,
    model_client: Optional[ModelClient] = None,
    fortune_data_path: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Run the local MingLi agent over benchmark questions."""

    records = []
    agent = MingLiAgent(model_client)
    for question in questions:
        records.append(
            evaluate_agent_question(
                question,
                agent=agent,
                fortune_data_path=fortune_data_path,
            )
        )
    return records


def evaluate_agent_question(
    question: Dict[str, Any],
    *,
    agent: MingLiAgent,
    fortune_data_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Evaluate one benchmark question through the agent pipeline."""

    start_time = time.time()
    record = {
        "question_id": question.get("id"),
        "case_id": question.get("case_id"),
        "benchmark_year": question.get("benchmark_year"),
        "category": question.get("category"),
        "question": question.get("question"),
        "success": False,
        "error": None,
        "response_time": 0.0,
        "agent": None,
        "checks": {},
    }
    try:
        birth_info = question.get("birth_info") or {}
        result = agent.run(
            birth_info,
            question=str(question.get("question") or ""),
            fortune_data_path=fortune_data_path,
        )
        agent_dict = result.as_dict()
        record["agent"] = agent_dict
        record["checks"] = build_agent_checks(agent_dict)
        record["success"] = True
    except Exception as error:
        record["error"] = f"{error.__class__.__name__}: {error}"
    record["response_time"] = time.time() - start_time
    return record


def build_agent_checks(agent_result: Dict[str, Any]) -> Dict[str, Any]:
    """Build per-record quality checks for agent outputs."""

    trace_names = [stage.get("name") for stage in agent_result.get("trace", [])]
    interpretation = agent_result.get("interpretation") or {}
    intent = agent_result.get("intent") or {}
    return {
        "chart_ok": bool((agent_result.get("chart") or {}).get("pillars_text")),
        "intent_ok": bool(intent.get("primary_domain")),
        "trace_complete": trace_names == EXPECTED_TRACE,
        "interpretation_schema_ok": (
            interpretation.get("schema_version") == INTERPRETATION_SCHEMA_VERSION
            and bool(interpretation.get("sections"))
        ),
        "llm_json_parsed": interpretation.get("mode") == "llm_json"
        and bool(interpretation.get("parsed_from_response")),
        "trace_names": trace_names,
    }


def summarize_agent_eval(
    records: List[Dict[str, Any]],
    *,
    config: Optional[AgentEvalConfig] = None,
) -> Dict[str, Any]:
    """Summarize agent pipeline evaluation records."""

    total = len(records)
    successes = [record for record in records if record.get("success")]
    errors = [record for record in records if record.get("error")]
    checks = [record.get("checks") or {} for record in successes]
    warning_counts: Counter[str] = Counter()
    intent_counts: Counter[str] = Counter()
    interpretation_mode_counts: Counter[str] = Counter()
    category_counts: Counter[str] = Counter()

    for record in successes:
        agent_result = record.get("agent") or {}
        category_counts.update([str(record.get("category") or "unknown")])
        intent = agent_result.get("intent") or {}
        intent_counts.update([str(intent.get("primary_domain") or "unknown")])
        interpretation = agent_result.get("interpretation") or {}
        interpretation_mode_counts.update([str(interpretation.get("mode") or "unknown")])
        record_warnings = set(str(item) for item in agent_result.get("warnings") or [])
        for stage in agent_result.get("trace") or []:
            record_warnings.update(str(item) for item in stage.get("warnings") or [])
        warning_counts.update(record_warnings)

    response_times = [float(record.get("response_time") or 0.0) for record in records]
    summary = {
        "timestamp": datetime.now().isoformat(),
        "config": config.as_dict() if config else None,
        "total_questions": total,
        "successes": len(successes),
        "errors": len(errors),
        "success_rate": _ratio(len(successes), total),
        "chart_success_rate": _check_rate(checks, "chart_ok"),
        "intent_success_rate": _check_rate(checks, "intent_ok"),
        "trace_complete_rate": _check_rate(checks, "trace_complete"),
        "interpretation_schema_rate": _check_rate(checks, "interpretation_schema_ok"),
        "llm_json_parse_rate": _check_rate(checks, "llm_json_parsed"),
        "average_response_time": sum(response_times) / len(response_times)
        if response_times
        else 0.0,
        "intent_distribution": dict(intent_counts),
        "interpretation_mode_distribution": dict(interpretation_mode_counts),
        "category_distribution": dict(category_counts),
        "warning_counts": dict(warning_counts),
        "error_samples": [
            {
                "question_id": record.get("question_id"),
                "case_id": record.get("case_id"),
                "error": record.get("error"),
            }
            for record in errors[:10]
        ],
        "records": records,
    }
    return summary


def save_agent_eval(summary: Dict[str, Any], output_dir: str = "logs") -> Dict[str, str]:
    """Save agent evaluation summary and JSONL records."""

    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = root / f"agent_eval_{timestamp}"
    run_dir.mkdir(parents=True, exist_ok=True)

    summary_path = run_dir / "summary.json"
    records_path = run_dir / "records.jsonl"
    with summary_path.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2)
    with records_path.open("w", encoding="utf-8") as handle:
        for record in summary.get("records") or []:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    return {
        "run_dir": str(run_dir),
        "summary": str(summary_path),
        "records": str(records_path),
    }


def format_agent_eval_summary(summary: Dict[str, Any]) -> str:
    """Render a compact terminal summary."""

    lines = [
        "Agent Evaluation Summary",
        "========================",
        f"Total Questions: {summary['total_questions']}",
        f"Successes: {summary['successes']}",
        f"Errors: {summary['errors']}",
        f"Success Rate: {summary['success_rate']:.2%}",
        f"Chart Success Rate: {summary['chart_success_rate']:.2%}",
        f"Intent Success Rate: {summary['intent_success_rate']:.2%}",
        f"Trace Complete Rate: {summary['trace_complete_rate']:.2%}",
        f"Interpretation Schema Rate: {summary['interpretation_schema_rate']:.2%}",
        f"LLM JSON Parse Rate: {summary['llm_json_parse_rate']:.2%}",
        f"Average Response Time: {summary['average_response_time']:.3f}s",
        "",
        "Intent Distribution:",
    ]
    for domain, count in sorted(summary["intent_distribution"].items()):
        lines.append(f"  - {domain}: {count}")
    if summary.get("warning_counts"):
        lines.extend(["", "Warnings:"])
        for warning, count in sorted(summary["warning_counts"].items()):
            lines.append(f"  - {warning}: {count}")
    return "\n".join(lines)


def _check_rate(checks: List[Dict[str, Any]], key: str) -> float:
    if not checks:
        return 0.0
    return _ratio(sum(1 for item in checks if item.get(key)), len(checks))


def _ratio(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


__all__ = [
    "AgentEvalConfig",
    "EXPECTED_TRACE",
    "build_agent_checks",
    "evaluate_agent_question",
    "evaluate_agent_questions",
    "format_agent_eval_summary",
    "load_agent_eval_questions",
    "save_agent_eval",
    "summarize_agent_eval",
]
