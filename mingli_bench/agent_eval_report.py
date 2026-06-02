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


IGNORED_CONFIG_DIFF_KEYS = {"output_dir", "save"}


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


def compare_agent_eval_runs(
    base: Dict[str, Any],
    candidate: Dict[str, Any],
) -> Dict[str, Any]:
    """Compare two loaded eval-agent runs on shared question IDs."""

    base_summary = base["summary"]
    candidate_summary = candidate["summary"]
    base_records = _records_by_question_id(base["records"])
    candidate_records = _records_by_question_id(candidate["records"])
    shared_ids = sorted(set(base_records) & set(candidate_records))
    improvements = []
    regressions = []
    changed_predictions = []
    category_totals: Counter[str] = Counter()
    base_category_correct: Counter[str] = Counter()
    candidate_category_correct: Counter[str] = Counter()

    for question_id in shared_ids:
        base_record = base_records[question_id]
        candidate_record = candidate_records[question_id]
        category = str(candidate_record.get("category") or base_record.get("category") or "unknown")
        category_totals.update([category])
        if base_record.get("answer_correct") is True:
            base_category_correct.update([category])
        if candidate_record.get("answer_correct") is True:
            candidate_category_correct.update([category])

        base_correct = base_record.get("answer_correct") is True
        candidate_correct = candidate_record.get("answer_correct") is True
        if not base_correct and candidate_correct:
            improvements.append(_comparison_sample(base_record, candidate_record))
        if base_correct and not candidate_correct:
            regressions.append(_comparison_sample(base_record, candidate_record))
        if base_record.get("predicted_answer") != candidate_record.get("predicted_answer"):
            changed_predictions.append(_comparison_sample(base_record, candidate_record))

    base_accuracy = base_summary.get("answer_choice_accuracy")
    candidate_accuracy = candidate_summary.get("answer_choice_accuracy")
    accuracy_delta = _optional_delta(candidate_accuracy, base_accuracy)
    llm_json_parse_delta = _optional_delta(
        candidate_summary.get("llm_json_parse_rate"),
        base_summary.get("llm_json_parse_rate"),
    )
    verdict = _comparison_verdict(
        accuracy_delta,
        improvement_count=len(improvements),
        regression_count=len(regressions),
        parse_delta=llm_json_parse_delta,
    )
    return {
        "base_run_dir": base.get("run_dir"),
        "candidate_run_dir": candidate.get("run_dir"),
        "verdict": verdict["verdict"],
        "recommendation": verdict["recommendation"],
        "config_differences": _config_differences(base_summary, candidate_summary),
        "shared_question_count": len(shared_ids),
        "base_accuracy": base_accuracy,
        "candidate_accuracy": candidate_accuracy,
        "accuracy_delta": accuracy_delta,
        "base_llm_json_parse_rate": base_summary.get("llm_json_parse_rate"),
        "candidate_llm_json_parse_rate": candidate_summary.get("llm_json_parse_rate"),
        "llm_json_parse_delta": llm_json_parse_delta,
        "base_average_response_time": base_summary.get("average_response_time"),
        "candidate_average_response_time": candidate_summary.get("average_response_time"),
        "average_response_time_delta": _optional_delta(
            candidate_summary.get("average_response_time"),
            base_summary.get("average_response_time"),
        ),
        "improvement_count": len(improvements),
        "regression_count": len(regressions),
        "changed_prediction_count": len(changed_predictions),
        "category_deltas": [
            {
                "category": category,
                "total": total,
                "base_correct": base_category_correct.get(category, 0),
                "candidate_correct": candidate_category_correct.get(category, 0),
                "base_accuracy": _ratio(base_category_correct.get(category, 0), total),
                "candidate_accuracy": _ratio(
                    candidate_category_correct.get(category, 0),
                    total,
                ),
                "accuracy_delta": _ratio(
                    candidate_category_correct.get(category, 0),
                    total,
                )
                - _ratio(base_category_correct.get(category, 0), total),
            }
            for category, total in sorted(category_totals.items())
        ],
        "improvements": improvements,
        "regressions": regressions,
        "changed_predictions": changed_predictions,
    }


def format_agent_eval_comparison(comparison: Dict[str, Any]) -> str:
    """Render an A/B eval comparison for terminal output."""

    lines = [
        "Agent Eval Comparison",
        "=====================",
        f"Base: {comparison.get('base_run_dir')}",
        f"Candidate: {comparison.get('candidate_run_dir')}",
        f"Verdict: {comparison.get('verdict')}",
        f"Recommendation: {comparison.get('recommendation')}",
        f"Shared Questions: {comparison.get('shared_question_count')}",
        "Accuracy: "
        f"{_format_rate(comparison.get('base_accuracy'))} -> "
        f"{_format_rate(comparison.get('candidate_accuracy'))} "
        f"(delta={_format_signed_rate(comparison.get('accuracy_delta'))})",
        "LLM JSON Parse: "
        f"{_format_rate(comparison.get('base_llm_json_parse_rate'))} -> "
        f"{_format_rate(comparison.get('candidate_llm_json_parse_rate'))} "
        f"(delta={_format_signed_rate(comparison.get('llm_json_parse_delta'))})",
        "Average Response Time: "
        f"{_format_float(comparison.get('base_average_response_time'))}s -> "
        f"{_format_float(comparison.get('candidate_average_response_time'))}s "
        f"(delta={_format_signed_float(comparison.get('average_response_time_delta'))}s)",
        f"Improvements: {comparison.get('improvement_count')}",
        f"Regressions: {comparison.get('regression_count')}",
        f"Changed Predictions: {comparison.get('changed_prediction_count')}",
    ]
    if comparison.get("config_differences"):
        lines.extend(["", "Config Differences:"])
        for item in comparison["config_differences"]:
            lines.append(
                "  - "
                f"{item['key']}: {item.get('base')} -> {item.get('candidate')}"
            )
    lines.extend(["", "Category Deltas:"])
    for item in comparison.get("category_deltas") or []:
        lines.append(
            "  - "
            f"{item['category']}: "
            f"{item['base_correct']}/{item['total']} -> "
            f"{item['candidate_correct']}/{item['total']} "
            f"(delta={_format_signed_rate(item['accuracy_delta'])})"
        )

    if comparison.get("improvements"):
        lines.extend(["", "Improvements:"])
        for item in comparison["improvements"]:
            lines.append(_format_comparison_sample(item))

    if comparison.get("regressions"):
        lines.extend(["", "Regressions:"])
        for item in comparison["regressions"]:
            lines.append(_format_comparison_sample(item))

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


def _records_by_question_id(records: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    return {
        str(record.get("question_id")): record
        for record in records
        if record.get("question_id")
    }


def _comparison_verdict(
    accuracy_delta: Optional[float],
    *,
    improvement_count: int,
    regression_count: int,
    parse_delta: Optional[float],
) -> Dict[str, str]:
    if accuracy_delta is None:
        return {
            "verdict": "insufficient_data",
            "recommendation": "inspect_runs_manually",
        }
    if accuracy_delta < 0:
        return {
            "verdict": "regressed",
            "recommendation": "reject_candidate",
        }
    if accuracy_delta > 0 and regression_count == 0 and (
        parse_delta is None or parse_delta >= 0
    ):
        return {
            "verdict": "improved",
            "recommendation": "candidate_passed_initial_gate",
        }
    if accuracy_delta > 0:
        return {
            "verdict": "mixed_improvement",
            "recommendation": "review_changed_questions",
        }
    if regression_count > improvement_count:
        return {
            "verdict": "mixed_regression",
            "recommendation": "reject_or_rework_candidate",
        }
    if improvement_count > regression_count:
        return {
            "verdict": "mixed_tie",
            "recommendation": "review_changed_questions",
        }
    return {
        "verdict": "tied",
        "recommendation": "no_clear_gain",
    }


def _config_differences(
    base_summary: Dict[str, Any],
    candidate_summary: Dict[str, Any],
) -> List[Dict[str, Any]]:
    base_config = base_summary.get("config") or {}
    candidate_config = candidate_summary.get("config") or {}
    keys = sorted((set(base_config) | set(candidate_config)) - IGNORED_CONFIG_DIFF_KEYS)
    return [
        {
            "key": key,
            "base": base_config.get(key),
            "candidate": candidate_config.get(key),
        }
        for key in keys
        if base_config.get(key) != candidate_config.get(key)
    ]


def _comparison_sample(
    base_record: Dict[str, Any],
    candidate_record: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "question_id": candidate_record.get("question_id"),
        "category": candidate_record.get("category") or base_record.get("category"),
        "question": candidate_record.get("question") or base_record.get("question"),
        "answer": candidate_record.get("answer") or base_record.get("answer"),
        "base_predicted_answer": base_record.get("predicted_answer"),
        "candidate_predicted_answer": candidate_record.get("predicted_answer"),
        "base_correct": base_record.get("answer_correct"),
        "candidate_correct": candidate_record.get("answer_correct"),
        "base_confidence": (
            ((base_record.get("agent") or {}).get("interpretation") or {}).get(
                "answer_confidence"
            )
        ),
        "candidate_confidence": (
            ((candidate_record.get("agent") or {}).get("interpretation") or {}).get(
                "answer_confidence"
            )
        ),
    }


def _format_comparison_sample(item: Dict[str, Any]) -> str:
    return (
        "  - "
        f"{item['question_id']} [{item['category']}]: "
        f"answer={item['answer']}, "
        f"base={item['base_predicted_answer']} "
        f"({_format_rate(item.get('base_confidence'))}), "
        f"candidate={item['candidate_predicted_answer']} "
        f"({_format_rate(item.get('candidate_confidence'))})"
    )


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


def _format_signed_rate(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"{float(value):+.2%}"


def _format_signed_float(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"{float(value):+.3f}"


def _optional_delta(candidate_value: Any, base_value: Any) -> Optional[float]:
    if candidate_value is None or base_value is None:
        return None
    return float(candidate_value) - float(base_value)


__all__ = [
    "build_agent_eval_analysis",
    "compare_agent_eval_runs",
    "format_agent_eval_comparison",
    "format_agent_eval_analysis",
    "load_agent_eval_run",
]
