import json
import tempfile
import unittest
from pathlib import Path

from mingli_bench.agent_eval_report import (
    build_agent_eval_analysis,
    compare_agent_eval_runs,
    format_agent_eval_comparison,
    format_agent_eval_analysis,
    load_agent_eval_run,
)


class AgentEvalReportTests(unittest.TestCase):
    def test_build_and_format_agent_eval_analysis(self):
        records = [_candidate_year_record(), _wrong_health_record()]
        summary = {
            "total_questions": 2,
            "successes": 2,
            "answer_choice_accuracy": 0.5,
            "answer_choice_parse_rate": 1.0,
            "llm_json_parse_rate": 1.0,
            "average_response_time": 1.25,
            "warning_counts": {"llm_response_not_valid_json": 1},
        }

        analysis = build_agent_eval_analysis(summary, records, run_dir="run")

        self.assertEqual(analysis["wrong_answer_count"], 1)
        self.assertEqual(analysis["category_performance"][0]["category"], "健康")
        self.assertEqual(analysis["category_performance"][0]["accuracy"], 0.0)
        self.assertEqual(analysis["candidate_year_cases"][0]["default_top"], "A")
        self.assertEqual(analysis["candidate_year_cases"][0]["activation_top"], "C")
        self.assertTrue(
            analysis["candidate_year_cases"][0]["model_followed_activation"]
        )
        self.assertEqual(
            analysis["event_type_confusions"][0]["answer_event_type"],
            "mental_health",
        )
        self.assertEqual(
            analysis["event_type_confusions"][0]["predicted_event_type"],
            "traffic_accident",
        )
        health_diagnostic = _category_diagnostic(analysis, "健康")
        self.assertEqual(health_diagnostic["wrong"], 1)
        self.assertEqual(health_diagnostic["high_confidence_wrong_count"], 1)
        self.assertEqual(health_diagnostic["low_margin_wrong_count"], 0)
        self.assertAlmostEqual(
            health_diagnostic["wrong_average_score_gap_to_expected"],
            0.3,
        )
        self.assertEqual(health_diagnostic["event_type_guard_applied_count"], 1)
        self.assertEqual(health_diagnostic["event_type_guard_wrong_count"], 1)
        self.assertEqual(
            health_diagnostic["event_type_confusions"][0]["answer_event_type"],
            "mental_health",
        )
        year_diagnostic = _category_diagnostic(analysis, "婚姻")
        self.assertEqual(year_diagnostic["candidate_year_override_applied_count"], 1)
        self.assertEqual(year_diagnostic["candidate_year_override_correct_count"], 1)

        formatted = format_agent_eval_analysis(analysis)
        self.assertIn("Agent Eval Error Report", formatted)
        self.assertIn("Answer Accuracy: 50.00%", formatted)
        self.assertIn("Category Diagnostics", formatted)
        self.assertIn("high_confidence_wrong=1", formatted)
        self.assertIn("event_type_guard=0 correct / 1 wrong", formatted)
        self.assertIn("Event Type Confusions", formatted)
        self.assertIn("mental_health -> traffic_accident: 1", formatted)
        self.assertIn("q_health", formatted)
        self.assertIn("activation_top=C", formatted)

    def test_load_agent_eval_run(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            summary = {"total_questions": 1, "successes": 1}
            record = {"question_id": "q1", "success": True}
            (root / "summary.json").write_text(
                json.dumps(summary),
                encoding="utf-8",
            )
            (root / "records.jsonl").write_text(
                json.dumps(record) + "\n",
                encoding="utf-8",
            )

            loaded = load_agent_eval_run(str(root))

            self.assertEqual(loaded["summary"]["total_questions"], 1)
            self.assertEqual(loaded["records"][0]["question_id"], "q1")

    def test_compare_agent_eval_runs(self):
        base = {
            "run_dir": "base",
            "summary": {
                "answer_choice_accuracy": 0.5,
                "llm_json_parse_rate": 1.0,
                "average_response_time": 10.0,
                "config": {
                    "model_name": "sonnet",
                    "include_candidate_year_diagnostics": False,
                },
            },
            "records": [
                _record("q1", "健康", "A", "C", False, confidence=0.7),
                _record("q2", "婚姻", "B", "B", True, confidence=0.6),
            ],
        }
        candidate = {
            "run_dir": "candidate",
            "summary": {
                "answer_choice_accuracy": 0.5,
                "llm_json_parse_rate": 0.9,
                "average_response_time": 12.5,
                "config": {
                    "model_name": "sonnet",
                    "include_candidate_year_diagnostics": True,
                },
            },
            "records": [
                _record("q1", "健康", "A", "A", True, confidence=0.5),
                _record("q2", "婚姻", "B", "A", False, confidence=0.8),
            ],
        }

        comparison = compare_agent_eval_runs(base, candidate)

        self.assertEqual(comparison["shared_question_count"], 2)
        self.assertEqual(comparison["accuracy_delta"], 0.0)
        self.assertAlmostEqual(comparison["llm_json_parse_delta"], -0.1)
        self.assertEqual(comparison["average_response_time_delta"], 2.5)
        self.assertEqual(comparison["improvement_count"], 1)
        self.assertEqual(comparison["regression_count"], 1)
        self.assertEqual(comparison["changed_prediction_count"], 2)
        self.assertEqual(comparison["verdict"], "tied")
        self.assertEqual(comparison["recommendation"], "no_clear_gain")
        self.assertEqual(
            comparison["config_differences"],
            [
                {
                    "key": "include_candidate_year_diagnostics",
                    "base": False,
                    "candidate": True,
                }
            ],
        )

        formatted = format_agent_eval_comparison(comparison)
        self.assertIn("Agent Eval Comparison", formatted)
        self.assertIn("Verdict: tied", formatted)
        self.assertIn("include_candidate_year_diagnostics: False -> True", formatted)
        self.assertIn("delta=+0.00%", formatted)
        self.assertIn("q1", formatted)
        self.assertIn("q2", formatted)


def _candidate_year_record():
    return {
        "question_id": "q_year",
        "case_id": "case_1",
        "category": "婚姻",
        "question": "此命何年结婚？",
        "answer": "C",
        "predicted_answer": "C",
        "answer_correct": True,
        "success": True,
        "agent": {
            "report": {
                "candidate_year_scores": [
                    {
                        "letter": "A",
                        "year": 1999,
                        "score": 4.0,
                        "rank": 1,
                        "variant_scores": {
                            "activation_weighted": 3.0,
                        },
                        "variant_ranks": {
                            "activation_weighted": 2,
                        },
                    },
                    {
                        "letter": "C",
                        "year": 2006,
                        "score": 3.2,
                        "rank": 2,
                        "variant_scores": {
                            "activation_weighted": 4.0,
                        },
                        "variant_ranks": {
                            "activation_weighted": 1,
                        },
                    },
                ]
            },
            "interpretation": {"answer_confidence": 0.55},
        },
        "candidate_year_override": {
            "variant": "activation_weighted",
            "applied": True,
            "original_predicted_answer": "A",
            "override_answer": "C",
        },
    }


def _wrong_health_record():
    return {
        "question_id": "q_health",
        "case_id": "case_2",
        "category": "健康",
        "question": "此命发生何事？",
        "answer": "A",
        "predicted_answer": "C",
        "answer_correct": False,
        "success": True,
        "agent": {
            "report": {
                "option_semantics": [
                    {
                        "letter": "A",
                        "primary_event_type": "mental_health",
                    },
                    {
                        "letter": "C",
                        "primary_event_type": "traffic_accident",
                    },
                ]
            },
            "interpretation": {
                "answer_confidence": 0.82,
                "option_scores": {
                    "A": {"score": 0.4},
                    "C": {"score": 0.7},
                },
            },
        },
        "event_type_guard": {
            "guard": "cautious_traffic",
            "applied": True,
            "original_predicted_answer": "A",
            "replacement_answer": "C",
            "reason": "test_guard",
        },
    }


def _record(
    question_id,
    category,
    answer,
    predicted_answer,
    answer_correct,
    *,
    confidence,
):
    return {
        "question_id": question_id,
        "case_id": f"case_{question_id}",
        "category": category,
        "question": f"question {question_id}",
        "answer": answer,
        "predicted_answer": predicted_answer,
        "answer_correct": answer_correct,
        "success": True,
        "agent": {
            "interpretation": {
                "answer_confidence": confidence,
            }
        },
    }


def _category_diagnostic(analysis, category):
    for item in analysis["category_diagnostics"]:
        if item["category"] == category:
            return item
    raise AssertionError(f"missing category diagnostic: {category}")


if __name__ == "__main__":
    unittest.main()
