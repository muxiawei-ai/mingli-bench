"""Readable error reports for saved MingLi agent evaluation runs."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional

from .agent_eval import (
    build_answer_score_diagnostic,
    candidate_year_variant_top_choice,
    option_event_type,
    top_candidate_year_choice,
)


def load_agent_eval_run(run_dir: str) -> Dict[str, Any]:
    """Load summary and JSONL records from one saved eval-agent run."""

    root = Path(run_dir)
    summary_path = root / "summary.json"
    records_path = root / "records.jsonl"
    if not summary_path.exists():
        raise FileNotFoundError(f"missing summary.json in {run_dir}")
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    records = []
    if records_path.exists():
        records = [
            json.loads(line)
            for line in records_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
    else:
        records = list(summary.get("records") or [])
    return {
        "run_dir": str(root),
        "summary": summary,
        "records": records,
    }


def build_agent_eval_analysis(
    summary: Dict[str, Any],
    records: List[Dict[str, Any]],
    *,
    run_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """Build a compact structured analysis for one eval-agent run."""

    category_totals: Counter[str] = Counter()
    category_correct: Counter[str] = Counter()
    wrong_answers = []
    candidate_year_cases = []
    for record in records:
        if not record.get("success"):
            continue
        category = str(record.get("category") or "unknown")
        category_totals.update([category])
        if record.get("answer_correct") is True:
            category_correct.update([category])
        if record.get("answer_correct") is False:
            wrong_answers.append(_wrong_answer_sample(record))
        default_top = top_candidate_year_choice(record)
        if default_top:
            candidate_year_cases.append(_candidate_year_case(record, default_top))

    return {
        "run_dir": run_dir,
        "total_questions": summary.get("total_questions", len(records)),
        "successes": summary.get("successes"),
        "answer_choice_accuracy": summary.get("answer_choice_accuracy"),
        "answer_choice_parse_rate": summary.get("answer_choice_parse_rate"),
        "llm_json_parse_rate": summary.get("llm_json_parse_rate"),
        "average_response_time": summary.get("average_response_time"),
        "wrong_answer_count": len(wrong_answers),
        "warning_counts": summary.get("warning_counts") or {},
        "category_performance": [
            {
                "category": category,
                "total": total,
                "correct": category_correct.get(category, 0),
                "accuracy": _ratio(category_correct.get(category, 0), total),
            }
            for category, total in sorted(category_totals.items())
        ],
        "wrong_answers": wrong_answers,
        "candidate_year_cases": candidate_year_cases,
        "answer_score_diagnostics": summary.get("answer_score_diagnostics") or {},
        "candidate_year_variant_top_choice_accuracy": summary.get(
            "candidate_year_variant_top_choice_accuracy"
        )
        or {},
        "candidate_year_focus_variant_top_choice_accuracy": summary.get(
            "candidate_year_focus_variant_top_choice_accuracy"
        )
        or {},
    }


def format_agent_eval_analysis(analysis: Dict[str, Any]) -> str:
    """Render structured eval analysis as compact terminal Markdown."""

    lines = [
        "Agent Eval Error Report",
        "=======================",
    ]
    if analysis.get("run_dir"):
        lines.append(f"Run: {analysis['run_dir']}")
    lines.extend(
        [
            f"Total Questions: {analysis.get('total_questions')}",
            f"Successes: {analysis.get('successes')}",
            f"Answer Accuracy: {_format_rate(analysis.get('answer_choice_accuracy'))}",
            f"Answer Parse Rate: {_format_rate(analysis.get('answer_choice_parse_rate'))}",
            f"LLM JSON Parse Rate: {_format_rate(analysis.get('llm_json_parse_rate'))}",
            f"Average Response Time: {_format_float(analysis.get('average_response_time'))}s",
            f"Wrong Answers: {analysis.get('wrong_answer_count')}",
            "",
            "Category Performance:",
        ]
    )
    for item in analysis.get("category_performance") or []:
        lines.append(
            "  - "
            f"{item['category']}: {item['correct']}/{item['total']} "
            f"({_format_rate(item['accuracy'])})"
        )

    if analysis.get("warning_counts"):
        lines.extend(["", "Warnings:"])
        for warning, count in sorted(analysis["warning_counts"].items()):
            lines.append(f"  - {warning}: {count}")

    if analysis.get("wrong_answers"):
        lines.extend(["", "Wrong Answers:"])
        for item in analysis["wrong_answers"]:
            lines.append(
                "  - "
                f"{item['question_id']} [{item['category']}]: "
                f"{item['answer']} -> {item['predicted_answer']} "
                f"(confidence={_format_rate(item.get('answer_confidence'))}, "
                f"event={item.get('answer_event_type') or 'unknown'}"
                f"->{item.get('predicted_event_type') or 'unknown'})"
            )
            if item.get("score_gap_to_expected") is not None:
                lines.append(
                    "    score_gap_to_expected="
                    f"{_format_float(item['score_gap_to_expected'])}"
                )
            lines.append(f"    question={item.get('question')}")

    if analysis.get("candidate_year_cases"):
        lines.extend(["", "Candidate Year Cases:"])
        for item in analysis["candidate_year_cases"]:
            lines.append(
                "  - "
                f"{item['question_id']} [{item['category']}]: "
                f"answer={item['answer']}, predicted={item['predicted_answer']}, "
                f"default_top={item['default_top']}, "
                f"activation_top={item['activation_top']}, "
                f"model_followed_activation={item['model_followed_activation']}"
            )

    return "\n".join(lines)


def _wrong_answer_sample(record: Dict[str, Any]) -> Dict[str, Any]:
    diagnostic = build_answer_score_diagnostic(record) or {}
    interpretation = ((record.get("agent") or {}).get("interpretation") or {})
    return {
        "question_id": record.get("question_id"),
        "case_id": record.get("case_id"),
        "category": record.get("category"),
        "question": record.get("question"),
        "answer": record.get("answer"),
        "predicted_answer": record.get("predicted_answer"),
        "answer_confidence": interpretation.get("answer_confidence"),
        "answer_event_type": option_event_type(record, record.get("answer")),
        "predicted_event_type": option_event_type(
            record,
            record.get("predicted_answer"),
        ),
        "expected_score": diagnostic.get("expected_score"),
        "predicted_score": diagnostic.get("predicted_score"),
        "score_gap_to_expected": diagnostic.get("score_gap_to_expected"),
    }


def _candidate_year_case(
    record: Dict[str, Any],
    default_top: str,
) -> Dict[str, Any]:
    activation_top = candidate_year_variant_top_choice(record, "activation_weighted")
    return {
        "question_id": record.get("question_id"),
        "case_id": record.get("case_id"),
        "category": record.get("category"),
        "question": record.get("question"),
        "answer": record.get("answer"),
        "predicted_answer": record.get("predicted_answer"),
        "default_top": default_top,
        "activation_top": activation_top,
        "model_followed_default": default_top == record.get("predicted_answer"),
        "model_followed_activation": activation_top == record.get("predicted_answer"),
        "activation_matches_answer": activation_top == record.get("answer"),
    }


def _ratio(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def _format_rate(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"{float(value):.2%}"


def _format_float(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"{float(value):.3f}"


__all__ = [
    "build_agent_eval_analysis",
    "format_agent_eval_analysis",
    "load_agent_eval_run",
]
