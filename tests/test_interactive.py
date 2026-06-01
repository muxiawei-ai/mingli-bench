import unittest

from mingli_bench.agent import MingLiAgent
from mingli_bench.interactive import (
    collect_agent_input,
    format_agent_result,
    inputs_from_iterable,
    normalize_calendar_type,
    parse_time_text,
)


class InteractiveAgentTests(unittest.TestCase):
    def test_normalize_calendar_type(self):
        self.assertEqual(normalize_calendar_type("公历"), "solar")
        self.assertEqual(normalize_calendar_type("solar"), "solar")
        self.assertEqual(normalize_calendar_type("农历"), "lunar")
        self.assertEqual(normalize_calendar_type("lunar"), "lunar")

    def test_parse_time_text(self):
        self.assertEqual(parse_time_text("18:30"), (18, 30))
        self.assertEqual(parse_time_text("9"), (9, 0))
        self.assertEqual(parse_time_text(""), (None, 0))

    def test_collect_agent_input_solar(self):
        prompts = []
        payload, question = collect_agent_input(
            input_func=inputs_from_iterable(
                [
                    "公历",
                    "1978",
                    "4",
                    "5",
                    "18:00",
                    "女",
                    "中国",
                    "台湾",
                    "分析事业",
                ]
            ),
            output_func=prompts.append,
        )
        self.assertEqual(payload["calendar_type"], "solar")
        self.assertEqual(payload["year"], 1978)
        self.assertEqual(payload["hour"], 18)
        self.assertEqual(payload["location"], "台湾")
        self.assertEqual(question, "分析事业")

    def test_collect_agent_input_lunar_text(self):
        payload, question = collect_agent_input(
            input_func=inputs_from_iterable(
                [
                    "农历",
                    "一九七八年二月廿八",
                    "18",
                    "",
                    "中国",
                    "台湾",
                    "",
                ]
            ),
            output_func=lambda _line: None,
        )
        self.assertEqual(payload["calendar_type"], "lunar")
        self.assertEqual(payload["lunar_date"], "一九七八年二月廿八")
        self.assertEqual(payload["hour"], 18)
        self.assertIn("八字命盘", question)

    def test_format_agent_result_human_readable(self):
        result = MingLiAgent().run(
            {
                "calendar_type": "solar",
                "year": 1978,
                "month": 4,
                "day": 5,
                "hour": 18,
                "location": "台湾",
            },
            question="分析事业",
        )
        formatted = format_agent_result(result)
        self.assertIn("四柱: 戊午 丙辰 丁酉 己酉", formatted)
        self.assertIn("Prompt Preview", formatted)


if __name__ == "__main__":
    unittest.main()
