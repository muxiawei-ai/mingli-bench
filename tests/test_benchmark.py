import unittest

from mingli_bench.benchmark import FortuneTellingBenchmark


class DummyModelClient:
    model_name = "dummy-model"

    def generate(self, prompt: str) -> str:
        return "答案：A"


class FortuneTellingBenchmarkTests(unittest.TestCase):
    def setUp(self):
        self.benchmark = FortuneTellingBenchmark(DummyModelClient())

    def test_extract_answer_uses_shared_patterns_and_valid_options(self):
        self.assertEqual(self.benchmark._extract_answer("答案：H"), "H")
        self.assertEqual(self.benchmark._extract_answer("分析略。最终选择：c"), "C")
        self.assertIsNone(self.benchmark._extract_answer("答案：Z"))

    def test_prepare_prompt_handles_explicit_option_letters(self):
        prompt = self.benchmark._prepare_prompt(
            {
                "id": "q_explicit",
                "question": "选择哪一项？",
                "birth_info": {"raw": "公历 1990-01-01 子时"},
                "options": [
                    {"letter": "B", "text": "乙"},
                    {"letter": "A", "text": "甲"},
                ],
            },
            use_cot=False,
        )

        self.assertIn("A. 甲", prompt)
        self.assertIn("B. 乙", prompt)

    def test_prepare_prompt_handles_mixed_option_formats(self):
        prompt = self.benchmark._prepare_prompt(
            {
                "id": "q_mixed",
                "question": "选择哪一项？",
                "birth_info": {"raw": "公历 1990-01-01 子时"},
                "options": [
                    {"letter": "A", "text": "甲"},
                    "乙",
                    {"text": "丙"},
                ],
            },
            use_cot=False,
        )

        self.assertIn("A. 甲", prompt)
        self.assertIn("B. 乙", prompt)
        self.assertIn("C. 丙", prompt)

    def test_evaluate_records_seed_question_ids_and_run_metadata(self):
        first = self.benchmark.evaluate(
            sample_size=3,
            shuffle_options=False,
            seed=42,
            max_workers=1,
        )
        second = self.benchmark.evaluate(
            sample_size=3,
            shuffle_options=False,
            seed=42,
            max_workers=1,
        )

        self.assertEqual(first["seed"], 42)
        self.assertEqual(first["question_ids"], second["question_ids"])
        self.assertEqual(len(first["question_ids"]), 3)
        self.assertIn("git_commit", first["run_metadata"])


if __name__ == "__main__":
    unittest.main()
