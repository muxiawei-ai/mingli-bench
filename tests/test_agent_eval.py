import json
import tempfile
import unittest
from pathlib import Path

from mingli_bench.agent_eval import (
    AgentEvalConfig,
    EXPECTED_TRACE,
    evaluate_agent_questions,
    expected_intent_domain,
    format_agent_eval_summary,
    load_agent_eval_questions,
    save_agent_eval,
    summarize_agent_eval,
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
        self.assertIn("clarification_samples", summary)
        self.assertIn("llm_not_called", summary["warning_counts"])
        self.assertEqual(summary["warning_counts"]["llm_not_called"], 2)
        self.assertEqual(records[0]["checks"]["trace_names"], EXPECTED_TRACE)

    def test_format_agent_eval_summary(self):
        questions = load_agent_eval_questions(AgentEvalConfig(sample_size=1))
        records = evaluate_agent_questions(questions)
        summary = summarize_agent_eval(records)
        formatted = format_agent_eval_summary(summary)
        self.assertIn("Agent Evaluation Summary", formatted)
        self.assertIn("Intent/Category Alignment Rate", formatted)
        self.assertIn("Trace Complete Rate", formatted)

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

    def test_expected_intent_domain(self):
        self.assertEqual(expected_intent_domain("事业"), "事业")
        self.assertEqual(expected_intent_domain("子女"), "家庭")
        self.assertEqual(expected_intent_domain("外貌"), "性格")
        self.assertEqual(expected_intent_domain("unknown"), "综合")


if __name__ == "__main__":
    unittest.main()
