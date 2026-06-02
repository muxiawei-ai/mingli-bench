import json
import tempfile
import unittest
from pathlib import Path

from mingli_bench.agent_eval_report import (
    build_agent_eval_analysis,
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

        formatted = format_agent_eval_analysis(analysis)
        self.assertIn("Agent Eval Error Report", formatted)
        self.assertIn("Answer Accuracy: 50.00%", formatted)
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
    }


if __name__ == "__main__":
    unittest.main()
