import unittest

from mingli_bench.chart_api import build_bazi_chart
from mingli_bench.hexagram import build_time_hexagram
from mingli_bench.hexagram_rules import build_hexagram_reading


class HexagramRulesTests(unittest.TestCase):
    def test_build_hexagram_reading_for_career_question(self):
        chart = build_bazi_chart(
            {
                "calendar_type": "solar",
                "year": 1978,
                "month": 4,
                "day": 5,
                "hour": 18,
                "location": "台湾",
            }
        )
        hexagram = build_time_hexagram(chart)
        reading = build_hexagram_reading(hexagram, "分析事业")

        self.assertIsNotNone(reading)
        assert reading is not None
        self.assertEqual(reading["schema_version"], "hexagram_reading.v1")
        self.assertEqual(reading["domain"], "事业")
        self.assertIn("临卦", reading["overview"])
        self.assertIn("复卦", reading["overview"])
        self.assertEqual(
            [section["title"] for section in reading["sections"]],
            ["本卦主轴", "动爻焦点", "变卦方向", "事业问题提示"],
        )
        self.assertIn("内部响应与执行位", reading["sections"][1]["summary"])
        self.assertIn("咸临，吉，无不利", reading["sections"][1]["summary"])

    def test_build_hexagram_reading_returns_none_without_hexagram(self):
        self.assertIsNone(build_hexagram_reading(None, "分析事业"))


if __name__ == "__main__":
    unittest.main()
