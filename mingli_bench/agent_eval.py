"""Agent pipeline evaluation helpers for MingLi-Bench."""

from __future__ import annotations

import json
import re
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional

from .agent import MingLiAgent
from .data.loader import DataLoader
from .interpretation import INTERPRETATION_SCHEMA_VERSION
from .models.base import ModelClient


EXPECTED_TRACE = ["input", "intent", "chart", "report", "prompt", "llm", "interpretation"]
SUPPORTED_INTENT_DOMAINS = {
    "事业",
    "财运",
    "婚姻",
    "健康",
    "性格",
    "学业",
    "家庭",
    "运势",
    "综合",
}
CATEGORY_TO_INTENT_DOMAIN = {
    "子女": "家庭",
    "外貌": "性格",
    "灾劫": "运势",
    "官非": "运势",
}
HIGH_CONFIDENCE_WRONG_THRESHOLD = 0.7
LOW_MARGIN_WRONG_THRESHOLD = 0.15


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
    include_candidate_year_diagnostics: bool = False
    candidate_year_override_variant: Optional[str] = None

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
            "include_candidate_year_diagnostics": (
                self.include_candidate_year_diagnostics
            ),
            "candidate_year_override_variant": self.candidate_year_override_variant,
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
    include_candidate_year_diagnostics: bool = False,
    candidate_year_override_variant: Optional[str] = None,
    record_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
) -> List[Dict[str, Any]]:
    """Run the local MingLi agent over benchmark questions."""

    records = []
    agent = MingLiAgent(
        model_client,
        include_candidate_year_diagnostics=include_candidate_year_diagnostics,
    )
    for question in questions:
        record = evaluate_agent_question(
            question,
            agent=agent,
            fortune_data_path=fortune_data_path,
            candidate_year_override_variant=candidate_year_override_variant,
        )
        records.append(record)
        if record_callback is not None:
            record_callback(record)
    return records


def evaluate_agent_question(
    question: Dict[str, Any],
    *,
    agent: MingLiAgent,
    fortune_data_path: Optional[str] = None,
    candidate_year_override_variant: Optional[str] = None,
) -> Dict[str, Any]:
    """Evaluate one benchmark question through the agent pipeline."""

    start_time = time.time()
    record = {
        "question_id": question.get("id"),
        "case_id": question.get("case_id"),
        "benchmark_year": question.get("benchmark_year"),
        "category": question.get("category"),
        "question": question.get("question"),
        "answer": question.get("answer"),
        "has_answer": question.get("has_answer"),
        "agent_question": None,
        "predicted_answer": None,
        "answer_correct": None,
        "success": False,
        "error": None,
        "response_time": 0.0,
        "agent": None,
        "checks": {},
    }
    try:
        birth_info = question.get("birth_info") or {}
        agent_question = format_agent_eval_question(question)
        record["agent_question"] = agent_question
        result = agent.run(
            birth_info,
            question=agent_question,
            fortune_data_path=fortune_data_path,
        )
        agent_dict = result.as_dict()
        record["agent"] = agent_dict
        record["checks"] = build_agent_checks(agent_dict)
        record["predicted_answer"] = extract_answer_choice(agent_dict)
        if candidate_year_override_variant:
            apply_candidate_year_override(record, candidate_year_override_variant)
        record["answer_correct"] = answer_choice_matches(
            record.get("answer"),
            record.get("predicted_answer"),
        )
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


def format_agent_eval_question(question: Dict[str, Any]) -> str:
    """Format benchmark question text plus options as agent question context."""

    lines = [str(question.get("question") or "").strip()]
    options = question.get("options") or []
    if options:
        lines.append("选项：")
        for option in options:
            if isinstance(option, dict):
                letter = option.get("letter") or "?"
                text = option.get("text") or ""
                lines.append(f"{letter}. {text}")
            else:
                lines.append(str(option))
    return "\n".join(line for line in lines if line)


def extract_answer_choice(agent_result: Dict[str, Any]) -> Optional[str]:
    """Extract a benchmark A-D answer choice from structured or text output."""

    interpretation = agent_result.get("interpretation") or {}
    explicit_choice = _normalize_answer_choice(interpretation.get("answer_choice"))
    if explicit_choice:
        return explicit_choice

    text_parts = [
        str(interpretation.get("overview") or ""),
        str(interpretation.get("raw_response") or ""),
    ]
    for section in interpretation.get("sections") or []:
        if isinstance(section, dict):
            text_parts.append(str(section.get("title") or ""))
            text_parts.append(str(section.get("summary") or ""))
    return _extract_answer_choice_from_text("\n".join(text_parts))


def apply_candidate_year_override(record: Dict[str, Any], variant: str) -> Dict[str, Any]:
    """Override predicted answers for candidate-year questions using a local variant."""

    original_answer = _normalize_answer_choice(record.get("predicted_answer"))
    override_answer = candidate_year_variant_top_choice(record, variant)
    metadata = {
        "variant": variant,
        "applied": False,
        "original_predicted_answer": original_answer,
        "override_answer": override_answer,
    }
    record["model_predicted_answer"] = original_answer
    if override_answer:
        record["predicted_answer"] = override_answer
        metadata["applied"] = True
    record["candidate_year_override"] = metadata
    return record


def answer_choice_matches(answer: Any, predicted_answer: Any) -> Optional[bool]:
    """Return whether a predicted A-D answer matches the benchmark answer."""

    normalized_answer = _normalize_answer_choice(answer)
    if not normalized_answer:
        return None
    normalized_prediction = _normalize_answer_choice(predicted_answer)
    if not normalized_prediction:
        return False
    return normalized_answer == normalized_prediction


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
    intent_category_confusion: Counter[tuple] = Counter()
    intent_alignment_total = 0
    intent_alignment_correct = 0
    answer_total = 0
    answer_parsed = 0
    answer_correct = 0
    answer_choice_confusion: Counter[tuple] = Counter()
    answer_event_type_confusion: Counter[tuple] = Counter()
    answer_event_type_total = 0
    answer_event_type_match = 0
    answer_event_type_mismatch = 0
    answer_event_type_unknown_expected = 0
    answer_event_type_unparsed_prediction = 0
    answer_score_diagnostics = []
    candidate_year_total = 0
    candidate_year_top_correct = 0
    candidate_year_model_agree = 0
    candidate_year_answer_candidate = 0
    candidate_year_model_candidate = 0
    candidate_year_answer_rank_counts: Counter[str] = Counter()
    candidate_year_model_rank_counts: Counter[str] = Counter()
    candidate_year_focus_counts: Counter[str] = Counter()
    candidate_year_variant_top_correct: Counter[str] = Counter()
    candidate_year_variant_answer_rank_counts: defaultdict[str, Counter[str]] = defaultdict(
        Counter
    )
    candidate_year_best_rank_variant_counts: Counter[str] = Counter()
    candidate_year_variants_seen = set()
    candidate_year_focus_totals: Counter[str] = Counter()
    candidate_year_focus_variants_seen: defaultdict[str, set] = defaultdict(set)
    candidate_year_focus_variant_top_correct: defaultdict[str, Counter[str]] = defaultdict(
        Counter
    )
    candidate_year_diagnostic_samples = []
    answer_error_samples = []
    clarification_samples = []

    for record in successes:
        agent_result = record.get("agent") or {}
        category = str(record.get("category") or "unknown")
        category_counts.update([category])
        intent = agent_result.get("intent") or {}
        primary_domain = str(intent.get("primary_domain") or "unknown")
        expected_domain = expected_intent_domain(category)
        intent_counts.update([primary_domain])
        intent_category_confusion.update([(expected_domain, primary_domain)])
        intent_alignment_total += 1
        if expected_domain == primary_domain:
            intent_alignment_correct += 1
        expected_answer = _normalize_answer_choice(record.get("answer"))
        predicted_answer = _normalize_answer_choice(record.get("predicted_answer"))
        if expected_answer:
            answer_total += 1
            top_candidate = top_candidate_year_choice(record)
            if top_candidate:
                candidate_year_total += 1
                answer_candidate = candidate_year_choice(record, expected_answer)
                predicted_candidate = candidate_year_choice(record, predicted_answer)
                focus = _candidate_year_scores(record)[0].get("focus") or "unknown"
                candidate_year_focus_counts.update([str(focus)])
                candidate_year_focus_totals.update([str(focus)])
                if answer_candidate:
                    candidate_year_answer_candidate += 1
                    candidate_year_variants_seen.update(
                        str(variant)
                        for variant in (answer_candidate.get("variant_ranks") or {})
                    )
                    candidate_year_answer_rank_counts.update(
                        [str(answer_candidate.get("rank") or "unknown")]
                    )
                    _update_candidate_year_variant_diagnostics(
                        record,
                        expected_answer,
                        answer_candidate,
                        candidate_year_variant_top_correct,
                        candidate_year_variant_answer_rank_counts,
                        candidate_year_best_rank_variant_counts,
                    )
                    _update_candidate_year_focus_variant_diagnostics(
                        record,
                        expected_answer,
                        str(focus),
                        answer_candidate,
                        candidate_year_focus_variants_seen,
                        candidate_year_focus_variant_top_correct,
                    )
                else:
                    candidate_year_answer_rank_counts.update(["not_candidate"])
                if predicted_candidate:
                    candidate_year_model_candidate += 1
                    candidate_year_model_rank_counts.update(
                        [str(predicted_candidate.get("rank") or "unknown")]
                    )
                else:
                    candidate_year_model_rank_counts.update(["not_candidate"])
                if top_candidate == expected_answer:
                    candidate_year_top_correct += 1
                if top_candidate == predicted_answer:
                    candidate_year_model_agree += 1
                if len(candidate_year_diagnostic_samples) < 10:
                    candidate_year_diagnostic_samples.append(
                        candidate_year_diagnostic_sample(record)
                    )
            expected_event_type = option_event_type(record, expected_answer)
            predicted_event_type = option_event_type(record, predicted_answer)
            if expected_event_type or predicted_event_type:
                if expected_event_type:
                    answer_event_type_total += 1
                    if expected_event_type == predicted_event_type:
                        answer_event_type_match += 1
                    else:
                        answer_event_type_mismatch += 1
                else:
                    answer_event_type_unknown_expected += 1
                if expected_event_type and not predicted_event_type:
                    answer_event_type_unparsed_prediction += 1
                answer_event_type_confusion.update(
                    [
                        (
                            expected_event_type or "unknown",
                            predicted_event_type or "unparsed",
                        )
                    ]
                )
            answer_diagnostic = build_answer_score_diagnostic(record)
            if answer_diagnostic:
                answer_score_diagnostics.append(answer_diagnostic)
            if predicted_answer:
                answer_parsed += 1
                answer_choice_confusion.update([(expected_answer, predicted_answer)])
                if predicted_answer == expected_answer:
                    answer_correct += 1
            if predicted_answer != expected_answer and len(answer_error_samples) < 10:
                answer_error_samples.append(
                    _answer_error_sample(record, answer_diagnostic)
                )
        if intent.get("needs_clarification") and len(clarification_samples) < 10:
            clarification_samples.append(
                {
                    "question_id": record.get("question_id"),
                    "case_id": record.get("case_id"),
                    "category": category,
                    "expected_domain": expected_domain,
                    "primary_domain": primary_domain,
                    "question": record.get("question"),
                }
            )
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
        "intent_category_alignment_rate": _ratio(
            intent_alignment_correct,
            intent_alignment_total,
        ),
        "answer_choice_total": answer_total,
        "answer_choice_parse_rate": _ratio(answer_parsed, answer_total),
        "answer_choice_accuracy": _ratio(answer_correct, answer_total),
        "answer_choice_accuracy_on_parsed": _ratio(answer_correct, answer_parsed),
        "answer_choice_confusion": _nested_confusion(answer_choice_confusion),
        "answer_event_type_confusion": _nested_confusion(answer_event_type_confusion),
        "answer_event_type_total": answer_event_type_total,
        "answer_event_type_match_rate": _ratio(
            answer_event_type_match,
            answer_event_type_total,
        ),
        "answer_event_type_mismatch_count": answer_event_type_mismatch,
        "answer_event_type_unknown_expected_count": answer_event_type_unknown_expected,
        "answer_event_type_unparsed_prediction_count": (
            answer_event_type_unparsed_prediction
        ),
        "candidate_year_score_total": candidate_year_total,
        "candidate_year_top_choice_accuracy": _ratio(
            candidate_year_top_correct,
            candidate_year_total,
        ),
        "candidate_year_model_agreement_rate": _ratio(
            candidate_year_model_agree,
            candidate_year_total,
        ),
        "candidate_year_answer_candidate_rate": _ratio(
            candidate_year_answer_candidate,
            candidate_year_total,
        ),
        "candidate_year_model_candidate_rate": _ratio(
            candidate_year_model_candidate,
            candidate_year_total,
        ),
        "candidate_year_answer_rank_distribution": dict(
            candidate_year_answer_rank_counts
        ),
        "candidate_year_model_rank_distribution": dict(
            candidate_year_model_rank_counts
        ),
        "candidate_year_focus_distribution": dict(candidate_year_focus_counts),
        "candidate_year_variant_top_choice_accuracy": {
            variant: _ratio(
                candidate_year_variant_top_correct.get(variant, 0),
                candidate_year_total,
            )
            for variant in sorted(candidate_year_variants_seen)
        },
        "candidate_year_variant_override_accuracy": (
            _candidate_year_variant_override_accuracy(
                successes,
                sorted(candidate_year_variants_seen),
            )
        ),
        "candidate_year_variant_answer_rank_distribution": {
            variant: dict(counts)
            for variant, counts in sorted(
                candidate_year_variant_answer_rank_counts.items()
            )
        },
        "candidate_year_best_rank_variant_distribution": dict(
            candidate_year_best_rank_variant_counts
        ),
        "candidate_year_focus_variant_top_choice_accuracy": {
            focus: {
                variant: _ratio(
                    candidate_year_focus_variant_top_correct[focus].get(variant, 0),
                    candidate_year_focus_totals[focus],
                )
                for variant in sorted(candidate_year_focus_variants_seen[focus])
            }
            for focus in sorted(candidate_year_focus_totals)
        },
        "candidate_year_diagnostic_samples": candidate_year_diagnostic_samples,
        "answer_score_diagnostics": _summarize_answer_score_diagnostics(
            answer_score_diagnostics
        ),
        "answer_error_samples": answer_error_samples,
        "average_response_time": sum(response_times) / len(response_times)
        if response_times
        else 0.0,
        "intent_distribution": dict(intent_counts),
        "intent_category_confusion": _nested_confusion(intent_category_confusion),
        "clarification_samples": clarification_samples,
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

    paths = start_agent_eval_run(output_dir)
    write_agent_eval_summary(summary, paths["summary"])
    for record in summary.get("records") or []:
        append_agent_eval_record(record, paths["records"])
    return paths


def start_agent_eval_run(output_dir: str = "logs") -> Dict[str, str]:
    """Create an evaluation run directory and touch output files."""

    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = root / f"agent_eval_{timestamp}"
    run_dir.mkdir(parents=True, exist_ok=True)

    summary_path = run_dir / "summary.json"
    records_path = run_dir / "records.jsonl"
    records_path.touch()
    return {
        "run_dir": str(run_dir),
        "summary": str(summary_path),
        "records": str(records_path),
    }


def append_agent_eval_record(record: Dict[str, Any], records_path: str) -> None:
    """Append one agent evaluation record to a JSONL file."""

    with Path(records_path).open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def write_agent_eval_summary(summary: Dict[str, Any], summary_path: str) -> None:
    """Write an agent evaluation summary JSON file."""

    with Path(summary_path).open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2)


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
        f"Intent/Category Alignment Rate: {summary['intent_category_alignment_rate']:.2%}",
        f"Answer Choice Parse Rate: {summary['answer_choice_parse_rate']:.2%}",
        f"Answer Choice Accuracy: {summary['answer_choice_accuracy']:.2%}",
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
    if summary.get("answer_event_type_confusion"):
        lines.extend(["", "Event Type Diagnostics:"])
        lines.append(
            "  - Match Rate: "
            f"{summary.get('answer_event_type_match_rate', 0.0):.2%}"
        )
        lines.append(
            "  - Mismatch Count: "
            f"{summary.get('answer_event_type_mismatch_count', 0)}"
        )
        lines.append(
            "  - Unknown Expected Count: "
            f"{summary.get('answer_event_type_unknown_expected_count', 0)}"
        )
        lines.append(
            "  - Unparsed Prediction Count: "
            f"{summary.get('answer_event_type_unparsed_prediction_count', 0)}"
        )
        lines.extend(["", "Answer Event Type Confusion:"])
        for expected_type, actuals in sorted(
            summary["answer_event_type_confusion"].items()
        ):
            actual_text = ", ".join(
                f"{actual_type}: {count}"
                for actual_type, count in sorted(actuals.items())
            )
            lines.append(f"  - {expected_type} -> {actual_text}")
    if summary.get("candidate_year_score_total"):
        lines.extend(["", "Candidate Year Diagnostics:"])
        lines.append(
            f"  - Candidate Year Records: {summary['candidate_year_score_total']}"
        )
        lines.append(
            "  - Top Candidate vs Answer: "
            f"{summary['candidate_year_top_choice_accuracy']:.2%}"
        )
        lines.append(
            "  - Model vs Top Candidate: "
            f"{summary['candidate_year_model_agreement_rate']:.2%}"
        )
        lines.append(
            "  - Answer In Candidate Set: "
            f"{summary['candidate_year_answer_candidate_rate']:.2%}"
        )
        if summary.get("candidate_year_answer_rank_distribution"):
            rank_text = ", ".join(
                f"{rank}: {count}"
                for rank, count in sorted(
                    summary["candidate_year_answer_rank_distribution"].items()
                )
            )
            lines.append(f"  - Answer Rank Distribution: {rank_text}")
        if summary.get("candidate_year_variant_top_choice_accuracy"):
            variant_text = ", ".join(
                f"{variant}: {accuracy:.2%}"
                for variant, accuracy in sorted(
                    summary["candidate_year_variant_top_choice_accuracy"].items()
                )
            )
            lines.append(f"  - Variant Top Accuracy: {variant_text}")
        if summary.get("candidate_year_variant_override_accuracy"):
            override_text = ", ".join(
                f"{variant}: {accuracy:.2%}"
                for variant, accuracy in sorted(
                    summary["candidate_year_variant_override_accuracy"].items()
                )
            )
            lines.append(f"  - Overall Accuracy With Variant Override: {override_text}")
        if summary.get("candidate_year_focus_variant_top_choice_accuracy"):
            lines.append("  - Focus Variant Top Accuracy:")
            for focus, accuracies in sorted(
                summary["candidate_year_focus_variant_top_choice_accuracy"].items()
            ):
                focus_variant_text = ", ".join(
                    f"{variant}: {accuracy:.2%}"
                    for variant, accuracy in sorted(accuracies.items())
                )
                lines.append(f"    - {focus}: {focus_variant_text}")
    diagnostics = summary.get("answer_score_diagnostics") or {}
    if diagnostics.get("scored_records") or diagnostics.get("records_with_confidence"):
        lines.extend(["", "Answer Score Diagnostics:"])
        lines.append(f"  - Scored Records: {diagnostics.get('scored_records', 0)}")
        lines.append(
            "  - Average Answer Confidence: "
            f"{_format_optional_rate(diagnostics.get('average_answer_confidence'))}"
        )
        lines.append(
            "  - Wrong Average Score Gap: "
            f"{_format_optional_float(diagnostics.get('wrong_average_score_gap_to_expected'))}"
        )
        lines.append(
            "  - High Confidence Wrong Count: "
            f"{diagnostics.get('high_confidence_wrong_count', 0)}"
        )
        lines.append(
            "  - Low Margin Wrong Count: "
            f"{diagnostics.get('low_margin_wrong_count', 0)}"
        )
    return "\n".join(lines)


def build_answer_score_diagnostic(record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Extract answer confidence and option-score diagnostics from a record."""

    expected_answer = _normalize_answer_choice(record.get("answer"))
    if not expected_answer:
        return None

    predicted_answer = _normalize_answer_choice(record.get("predicted_answer"))
    interpretation = ((record.get("agent") or {}).get("interpretation") or {})
    option_scores = _extract_option_scores(interpretation.get("option_scores"))
    answer_confidence = _optional_float(interpretation.get("answer_confidence"))
    if not option_scores and answer_confidence is None:
        return None

    expected_score = option_scores.get(expected_answer)
    predicted_score = option_scores.get(predicted_answer) if predicted_answer else None
    predicted_margin = _predicted_score_margin(option_scores, predicted_answer)
    score_gap_to_expected = None
    if predicted_score is not None and expected_score is not None:
        score_gap_to_expected = predicted_score - expected_score

    return {
        "question_id": record.get("question_id"),
        "case_id": record.get("case_id"),
        "category": record.get("category"),
        "answer": expected_answer,
        "predicted_answer": predicted_answer,
        "answer_correct": record.get("answer_correct"),
        "answer_confidence": answer_confidence,
        "option_scores": option_scores,
        "expected_score": expected_score,
        "predicted_score": predicted_score,
        "expected_rank": _score_rank(option_scores, expected_answer),
        "predicted_margin": predicted_margin,
        "score_gap_to_expected": score_gap_to_expected,
    }


def _summarize_answer_score_diagnostics(
    diagnostics: List[Dict[str, Any]],
) -> Dict[str, Any]:
    confidence_values = [
        item["answer_confidence"]
        for item in diagnostics
        if item.get("answer_confidence") is not None
    ]
    scored = [item for item in diagnostics if item.get("option_scores")]
    correct = [item for item in diagnostics if item.get("answer_correct") is True]
    wrong = [item for item in diagnostics if item.get("answer_correct") is False]
    high_confidence_wrong = [
        item
        for item in wrong
        if (item.get("answer_confidence") or 0.0) >= HIGH_CONFIDENCE_WRONG_THRESHOLD
    ]
    low_margin_wrong = [
        item
        for item in wrong
        if item.get("score_gap_to_expected") is not None
        and abs(float(item["score_gap_to_expected"])) <= LOW_MARGIN_WRONG_THRESHOLD
    ]
    return {
        "records_with_confidence": len(confidence_values),
        "scored_records": len(scored),
        "average_answer_confidence": _average_optional(confidence_values),
        "correct_average_answer_confidence": _average_optional(
            item.get("answer_confidence")
            for item in correct
            if item.get("answer_confidence") is not None
        ),
        "wrong_average_answer_confidence": _average_optional(
            item.get("answer_confidence")
            for item in wrong
            if item.get("answer_confidence") is not None
        ),
        "average_predicted_margin": _average_optional(
            item.get("predicted_margin")
            for item in scored
            if item.get("predicted_margin") is not None
        ),
        "wrong_average_predicted_margin": _average_optional(
            item.get("predicted_margin")
            for item in wrong
            if item.get("predicted_margin") is not None
        ),
        "wrong_average_score_gap_to_expected": _average_optional(
            item.get("score_gap_to_expected")
            for item in wrong
            if item.get("score_gap_to_expected") is not None
        ),
        "high_confidence_wrong_threshold": HIGH_CONFIDENCE_WRONG_THRESHOLD,
        "high_confidence_wrong_count": len(high_confidence_wrong),
        "high_confidence_wrong_samples": [
            _answer_diagnostic_sample(item) for item in high_confidence_wrong[:5]
        ],
        "low_margin_wrong_threshold": LOW_MARGIN_WRONG_THRESHOLD,
        "low_margin_wrong_count": len(low_margin_wrong),
        "low_margin_wrong_samples": [
            _answer_diagnostic_sample(item) for item in low_margin_wrong[:5]
        ],
    }


def _answer_error_sample(
    record: Dict[str, Any],
    diagnostic: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    sample = {
        "question_id": record.get("question_id"),
        "case_id": record.get("case_id"),
        "category": record.get("category"),
        "answer": _normalize_answer_choice(record.get("answer")),
        "predicted_answer": _normalize_answer_choice(record.get("predicted_answer")),
        "answer_event_type": option_event_type(record, record.get("answer")),
        "predicted_event_type": option_event_type(
            record,
            record.get("predicted_answer"),
        ),
        "question": record.get("question"),
    }
    if diagnostic:
        sample.update(_answer_diagnostic_sample(diagnostic))
    return sample


def option_event_type(record: Dict[str, Any], answer: Any) -> Optional[str]:
    """Return the text-derived event type for one answer option."""

    letter = _normalize_answer_choice(answer)
    if not letter:
        return None
    option_semantics = (
        ((record.get("agent") or {}).get("report") or {}).get("option_semantics")
        or []
    )
    for item in option_semantics:
        if item.get("letter") == letter:
            return str(item.get("primary_event_type") or "unknown")
    return None


def top_candidate_year_choice(record: Dict[str, Any]) -> Optional[str]:
    """Return the highest-ranked local candidate-year letter for one record."""

    scores = _candidate_year_scores(record)
    if not scores:
        return None
    ranked = sorted(
        scores,
        key=lambda item: (int(item.get("rank") or 999), -float(item.get("score") or 0.0)),
    )
    return _normalize_answer_choice(ranked[0].get("letter"))


def candidate_year_choice(
    record: Dict[str, Any],
    answer: Any,
) -> Optional[Dict[str, Any]]:
    """Return candidate-year score metadata for one answer option."""

    letter = _normalize_answer_choice(answer)
    if not letter:
        return None
    for item in _candidate_year_scores(record):
        if _normalize_answer_choice(item.get("letter")) == letter:
            return item
    return None


def candidate_year_diagnostic_sample(record: Dict[str, Any]) -> Dict[str, Any]:
    """Build a compact candidate-year diagnostic sample."""

    scores = _candidate_year_scores(record)
    top_choice = top_candidate_year_choice(record)
    answer_candidate = candidate_year_choice(record, record.get("answer"))
    predicted_candidate = candidate_year_choice(record, record.get("predicted_answer"))
    return {
        "question_id": record.get("question_id"),
        "case_id": record.get("case_id"),
        "category": record.get("category"),
        "answer": _normalize_answer_choice(record.get("answer")),
        "predicted_answer": _normalize_answer_choice(record.get("predicted_answer")),
        "top_candidate_year_choice": top_choice,
        "answer_candidate_rank": _candidate_rank(answer_candidate),
        "answer_candidate_score": _candidate_score(answer_candidate),
        "predicted_candidate_rank": _candidate_rank(predicted_candidate),
        "predicted_candidate_score": _candidate_score(predicted_candidate),
        "question": record.get("question"),
        "candidate_year_scores": [
            {
                "letter": item.get("letter"),
                "year": item.get("year"),
                "year_pillar": item.get("year_pillar"),
                "score": item.get("score"),
                "rank": item.get("rank"),
                "focus": item.get("focus"),
                "variant_scores": item.get("variant_scores") or {},
                "variant_ranks": item.get("variant_ranks") or {},
                "interaction_labels": item.get("interaction_labels") or [],
                "matched_positions": item.get("matched_positions") or [],
            }
            for item in scores
        ],
    }


def _update_candidate_year_variant_diagnostics(
    record: Dict[str, Any],
    expected_answer: str,
    answer_candidate: Dict[str, Any],
    variant_top_correct: Counter[str],
    variant_answer_rank_counts: defaultdict[str, Counter[str]],
    best_rank_variant_counts: Counter[str],
) -> None:
    variant_ranks = answer_candidate.get("variant_ranks") or {}
    if not variant_ranks:
        return
    for variant, rank in variant_ranks.items():
        variant_answer_rank_counts[str(variant)].update([str(rank or "unknown")])
        if candidate_year_variant_top_choice(record, str(variant)) == expected_answer:
            variant_top_correct.update([str(variant)])

    numeric_ranks = {
        str(variant): int(rank)
        for variant, rank in variant_ranks.items()
        if _looks_like_int(rank)
    }
    if not numeric_ranks:
        return
    best_rank = min(numeric_ranks.values())
    for variant, rank in numeric_ranks.items():
        if rank == best_rank:
            best_rank_variant_counts.update([variant])


def _update_candidate_year_focus_variant_diagnostics(
    record: Dict[str, Any],
    expected_answer: str,
    focus: str,
    answer_candidate: Dict[str, Any],
    focus_variants_seen: defaultdict[str, set],
    focus_variant_top_correct: defaultdict[str, Counter[str]],
) -> None:
    for variant in answer_candidate.get("variant_ranks") or {}:
        variant_name = str(variant)
        focus_variants_seen[focus].add(variant_name)
        if candidate_year_variant_top_choice(record, variant_name) == expected_answer:
            focus_variant_top_correct[focus].update([variant_name])


def candidate_year_variant_top_choice(
    record: Dict[str, Any],
    variant: str,
) -> Optional[str]:
    """Return the top candidate-year letter for one scoring variant."""

    scores = _candidate_year_scores(record)
    if not scores:
        return None
    ranked = sorted(
        scores,
        key=lambda item: (
            int((item.get("variant_ranks") or {}).get(variant) or 999),
            -float((item.get("variant_scores") or {}).get(variant) or 0.0),
        ),
    )
    return _normalize_answer_choice(ranked[0].get("letter"))


def _candidate_year_variant_override_accuracy(
    records: List[Dict[str, Any]],
    variants: List[str],
) -> Dict[str, float]:
    """Estimate accuracy if variant top choices override candidate-year questions."""

    if not variants:
        return {}
    totals: Counter[str] = Counter()
    correct: Counter[str] = Counter()
    for record in records:
        expected_answer = _normalize_answer_choice(record.get("answer"))
        if not expected_answer:
            continue
        predicted_answer = _normalize_answer_choice(record.get("predicted_answer"))
        has_candidate_year_scores = bool(_candidate_year_scores(record))
        for variant in variants:
            totals.update([variant])
            if has_candidate_year_scores:
                final_answer = candidate_year_variant_top_choice(record, variant)
            else:
                final_answer = predicted_answer
            if final_answer == expected_answer:
                correct.update([variant])
    return {variant: _ratio(correct[variant], totals[variant]) for variant in variants}


def _candidate_year_scores(record: Dict[str, Any]) -> List[Dict[str, Any]]:
    return (
        ((record.get("agent") or {}).get("report") or {}).get("candidate_year_scores")
        or []
    )


def _candidate_rank(item: Optional[Dict[str, Any]]) -> Optional[int]:
    if not item:
        return None
    try:
        return int(item.get("rank"))
    except (TypeError, ValueError):
        return None


def _candidate_score(item: Optional[Dict[str, Any]]) -> Optional[float]:
    if not item:
        return None
    try:
        return float(item.get("score"))
    except (TypeError, ValueError):
        return None


def _looks_like_int(value: Any) -> bool:
    try:
        int(value)
    except (TypeError, ValueError):
        return False
    return True


def _answer_diagnostic_sample(item: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "question_id": item.get("question_id"),
        "case_id": item.get("case_id"),
        "category": item.get("category"),
        "answer": item.get("answer"),
        "predicted_answer": item.get("predicted_answer"),
        "answer_confidence": item.get("answer_confidence"),
        "expected_score": item.get("expected_score"),
        "predicted_score": item.get("predicted_score"),
        "expected_rank": item.get("expected_rank"),
        "predicted_margin": item.get("predicted_margin"),
        "score_gap_to_expected": item.get("score_gap_to_expected"),
        "option_scores": item.get("option_scores") or {},
    }


def _extract_option_scores(value: Any) -> Dict[str, float]:
    if not isinstance(value, dict):
        return {}
    scores = {}
    for key, raw_item in value.items():
        letter = _normalize_answer_choice(key)
        if not letter:
            continue
        raw_score = raw_item.get("score") if isinstance(raw_item, dict) else raw_item
        score = _optional_float(raw_score)
        if score is not None:
            scores[letter] = score
    return scores


def _predicted_score_margin(
    option_scores: Dict[str, float],
    predicted_answer: Optional[str],
) -> Optional[float]:
    if not predicted_answer or predicted_answer not in option_scores:
        return None
    other_scores = [
        score for letter, score in option_scores.items() if letter != predicted_answer
    ]
    if not other_scores:
        return None
    return option_scores[predicted_answer] - max(other_scores)


def _score_rank(
    option_scores: Dict[str, float],
    answer: Optional[str],
) -> Optional[int]:
    if not answer or answer not in option_scores:
        return None
    ranked = sorted(option_scores.items(), key=lambda item: item[1], reverse=True)
    for index, (letter, _) in enumerate(ranked, start=1):
        if letter == answer:
            return index
    return None


def _optional_float(value: Any) -> Optional[float]:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _average_optional(values: Iterable[float]) -> Optional[float]:
    collected = [float(value) for value in values]
    if not collected:
        return None
    return round(sum(collected) / len(collected), 4)


def _format_optional_float(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"{float(value):.3f}"


def _format_optional_rate(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"{float(value):.2%}"


def _check_rate(checks: List[Dict[str, Any]], key: str) -> float:
    if not checks:
        return 0.0
    return _ratio(sum(1 for item in checks if item.get(key)), len(checks))


def _ratio(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def _normalize_answer_choice(value: Any) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip().upper()
    return text if text in {"A", "B", "C", "D"} else None


def _extract_answer_choice_from_text(text: str) -> Optional[str]:
    patterns = [
        r"(?:最终|答案|选择|倾向于|最(?:可能|符合|吻合|接近)|概率最高|契合度最高).*?(?:选项)?\s*([A-D])",
        r"(?:选项|option)\s*([A-D]).{0,20}(?:最(?:可能|符合|吻合|接近)|概率最高|契合度最高)",
        r"([A-D])\s*(?:选项|option).{0,20}(?:最(?:可能|符合|吻合|接近)|概率最高|契合度最高)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
        if match:
            return _normalize_answer_choice(match.group(1))
    return None


def expected_intent_domain(category: str) -> str:
    """Map benchmark categories to the closest agent intent domain."""

    if category in CATEGORY_TO_INTENT_DOMAIN:
        return CATEGORY_TO_INTENT_DOMAIN[category]
    if category in SUPPORTED_INTENT_DOMAINS:
        return category
    return "综合"


def _nested_confusion(counter: Counter[tuple]) -> Dict[str, Dict[str, int]]:
    nested: Dict[str, Dict[str, int]] = {}
    for (expected, actual), count in counter.items():
        nested.setdefault(str(expected), {})[str(actual)] = count
    return nested


__all__ = [
    "AgentEvalConfig",
    "EXPECTED_TRACE",
    "append_agent_eval_record",
    "candidate_year_choice",
    "candidate_year_variant_top_choice",
    "expected_intent_domain",
    "answer_choice_matches",
    "build_answer_score_diagnostic",
    "build_agent_checks",
    "evaluate_agent_question",
    "evaluate_agent_questions",
    "extract_answer_choice",
    "format_agent_eval_summary",
    "format_agent_eval_question",
    "load_agent_eval_questions",
    "option_event_type",
    "save_agent_eval",
    "start_agent_eval_run",
    "summarize_agent_eval",
    "top_candidate_year_choice",
    "write_agent_eval_summary",
]
