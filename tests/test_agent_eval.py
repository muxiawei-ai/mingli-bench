import json
import tempfile
import unittest
from pathlib import Path

from mingli_bench.agent_eval import (
    AgentEvalConfig,
    EXPECTED_TRACE,
    append_agent_eval_record,
    answer_choice_matches,
    evaluate_agent_questions,
    expected_intent_domain,
    extract_answer_choice,
    format_agent_eval_question,
    format_agent_eval_summary,
    load_agent_eval_questions,
    option_event_type,
    save_agent_eval,
    start_agent_eval_run,
    summarize_agent_eval,
    write_agent_eval_summary,
)


class AgentEvalTests(unittest.TestCase):
    def test_load_agent_eval_questions(self):
        questions = load_agent_eval_questions(AgentEvalConfig(sample_size=3))
        self.assertEqual(len(questions), 3)
        self.assertIn("birth_info", questions[0])

    def test_evaluate_agent_questions_and_summary(self):
        questions = load_agent_eval_questions(AgentEvalConfig(sample_size=2))
        records = evaluate_agent_questions(questions)
        summary = summarize_agent_eval(records, config=AgentEvalConfig(sample_size=2))

        self.assertEqual(summary["total_questions"], 2)
        self.assertEqual(summary["successes"], 2)
        self.assertEqual(summary["errors"], 0)
        self.assertEqual(summary["chart_success_rate"], 1.0)
        self.assertEqual(summary["trace_complete_rate"], 1.0)
        self.assertEqual(summary["interpretation_schema_rate"], 1.0)
        self.assertIn("intent_category_alignment_rate", summary)
        self.assertIn("intent_category_confusion", summary)
        self.assertIn("answer_choice_accuracy", summary)
        self.assertIn("clarification_samples", summary)
        self.assertIn("llm_not_called", summary["warning_counts"])
        self.assertEqual(summary["warning_counts"]["llm_not_called"], 2)
        self.assertEqual(records[0]["checks"]["trace_names"], EXPECTED_TRACE)
        self.assertIn("选项", records[0]["agent_question"])

    def test_format_agent_eval_summary(self):
        questions = load_agent_eval_questions(AgentEvalConfig(sample_size=1))
        records = evaluate_agent_questions(questions)
        summary = summarize_agent_eval(records)
        formatted = format_agent_eval_summary(summary)
        self.assertIn("Agent Evaluation Summary", formatted)
        self.assertIn("Intent/Category Alignment Rate", formatted)
        self.assertIn("Answer Choice Accuracy", formatted)
        self.assertIn("Trace Complete Rate", formatted)

    def test_answer_score_diagnostics(self):
        record = {
            "question_id": "q1",
            "case_id": "case_1",
            "category": "健康",
            "question": "此命发生何事？",
            "answer": "A",
            "predicted_answer": "B",
            "answer_correct": False,
            "success": True,
            "error": None,
            "response_time": 0.1,
            "checks": {
                "chart_ok": True,
                "intent_ok": True,
                "trace_complete": True,
                "interpretation_schema_ok": True,
                "llm_json_parsed": True,
            },
            "agent": {
                "intent": {"primary_domain": "健康"},
                "interpretation": {
                    "mode": "llm_json",
                    "answer_confidence": 0.82,
                    "option_scores": {
                        "A": {"score": 0.70, "rationale": "接近"},
                        "B": {"score": 0.75, "rationale": "略高"},
                        "C": {"score": 0.20, "rationale": "较弱"},
                        "D": {"score": 0.10, "rationale": "较弱"},
                    },
                },
                "warnings": [],
                "trace": [],
            },
        }

        summary = summarize_agent_eval([record])
        diagnostics = summary["answer_score_diagnostics"]

        self.assertEqual(diagnostics["records_with_confidence"], 1)
        self.assertEqual(diagnostics["scored_records"], 1)
        self.assertEqual(diagnostics["high_confidence_wrong_count"], 1)
        self.assertEqual(diagnostics["low_margin_wrong_count"], 1)
        self.assertEqual(diagnostics["wrong_average_score_gap_to_expected"], 0.05)
        self.assertEqual(summary["answer_error_samples"][0]["expected_score"], 0.70)

        formatted = format_agent_eval_summary(summary)
        self.assertIn("Answer Score Diagnostics", formatted)
        self.assertIn("High Confidence Wrong Count: 1", formatted)

    def test_answer_event_type_confusion(self):
        record = {
            "question_id": "q1",
            "case_id": "case_1",
            "category": "健康",
            "question": "此命1996年发生何事？",
            "answer": "A",
            "predicted_answer": "C",
            "answer_correct": False,
            "success": True,
            "error": None,
            "response_time": 0.1,
            "checks": {
                "chart_ok": True,
                "intent_ok": True,
                "trace_complete": True,
                "interpretation_schema_ok": True,
                "llm_json_parsed": True,
            },
            "agent": {
                "intent": {"primary_domain": "健康"},
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
                    "mode": "llm_json",
                    "answer_confidence": 0.52,
                },
                "warnings": [],
                "trace": [],
            },
        }

        self.assertEqual(option_event_type(record, "A"), "mental_health")
        summary = summarize_agent_eval([record])

        self.assertEqual(
            summary["answer_event_type_confusion"],
            {"mental_health": {"traffic_accident": 1}},
        )
        self.assertEqual(
            summary["answer_error_samples"][0]["answer_event_type"],
            "mental_health",
        )
        self.assertEqual(
            summary["answer_error_samples"][0]["predicted_event_type"],
            "traffic_accident",
        )
        self.assertIn("mental_health -> traffic_accident: 1", format_agent_eval_summary(summary))

    def test_save_agent_eval(self):
        questions = load_agent_eval_questions(AgentEvalConfig(sample_size=1))
        records = evaluate_agent_questions(questions)
        summary = summarize_agent_eval(records)
        with tempfile.TemporaryDirectory() as tmpdir:
            paths = save_agent_eval(summary, output_dir=tmpdir)
            summary_path = Path(paths["summary"])
            records_path = Path(paths["records"])
            self.assertTrue(summary_path.exists())
            self.assertTrue(records_path.exists())
            parsed = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(parsed["total_questions"], 1)
            self.assertEqual(len(records_path.read_text(encoding="utf-8").splitlines()), 1)

    def test_incremental_agent_eval_writes_records_before_summary(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            paths = start_agent_eval_run(tmpdir)
            append_agent_eval_record({"question_id": "q1"}, paths["records"])
            append_agent_eval_record({"question_id": "q2"}, paths["records"])

            records_path = Path(paths["records"])
            summary_path = Path(paths["summary"])
            self.assertEqual(len(records_path.read_text(encoding="utf-8").splitlines()), 2)
            self.assertFalse(summary_path.exists())

            write_agent_eval_summary({"total_questions": 2}, paths["summary"])
            self.assertTrue(summary_path.exists())

    def test_expected_intent_domain(self):
        self.assertEqual(expected_intent_domain("事业"), "事业")
        self.assertEqual(expected_intent_domain("子女"), "家庭")
        self.assertEqual(expected_intent_domain("外貌"), "性格")
        self.assertEqual(expected_intent_domain("unknown"), "综合")

    def test_format_agent_eval_question_includes_options(self):
        question = {
            "question": "发生何事？",
            "options": [
                {"letter": "A", "text": "工作升职"},
                {"letter": "B", "text": "身体生病"},
            ],
        }
        formatted = format_agent_eval_question(question)
        self.assertIn("发生何事", formatted)
        self.assertIn("A. 工作升职", formatted)
        self.assertIn("B. 身体生病", formatted)

    def test_extract_answer_choice_prefers_structured_field(self):
        agent_result = {
            "interpretation": {
                "answer_choice": "b",
                "overview": "选项A也可能。",
                "sections": [],
            }
        }
        self.assertEqual(extract_answer_choice(agent_result), "B")

    def test_extract_answer_choice_from_text(self):
        agent_result = {
            "interpretation": {
                "overview": "综合来看，选项C的契合度最高。",
                "sections": [],
            }
        }
        self.assertEqual(extract_answer_choice(agent_result), "C")

    def test_answer_choice_matches(self):
        self.assertTrue(answer_choice_matches("B", "b"))
        self.assertFalse(answer_choice_matches("A", "D"))
        self.assertIsNone(answer_choice_matches(None, "A"))


if __name__ == "__main__":
    unittest.main()
