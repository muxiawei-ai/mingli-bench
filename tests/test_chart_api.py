import json
import unittest
from pathlib import Path

from mingli_bench.chart_api import ChartInput, build_bazi_chart


class ChartApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = json.loads(Path("data/fortune_api_results.json").read_text(encoding="utf-8"))

    def test_build_bazi_chart_from_solar_input(self):
        chart = build_bazi_chart(
            {
                "calendar_type": "solar",
                "year": 1978,
                "month": 4,
                "day": 5,
                "hour": 18,
                "minute": 0,
                "gender": "女",
                "country": "中国",
                "location": "台湾",
            }
        )
        self.assertEqual(chart.pillars.display(), "戊午 丙辰 丁酉 己酉")
        self.assertEqual(chart.day_master, "丁")
        self.assertEqual(chart.timezone["timezone"], "Asia/Taipei")
        self.assertEqual(chart.warnings, [])
        self.assertEqual(chart.as_dict()["pillars"]["month"], "丙辰")

    def test_build_bazi_chart_accepts_dataclass_input(self):
        chart = build_bazi_chart(
            ChartInput(
                calendar_type="solar",
                year=1974,
                month=4,
                day=28,
                hour=16,
                minute=40,
                location="usa",
                country="usa",
            )
        )
        self.assertEqual(chart.pillars.display(), "甲寅 戊辰 己亥 壬申")
        self.assertIn("ambiguous_usa_location_requires_state_or_city", chart.warnings)

    def test_build_bazi_chart_from_lunar_fixture_input(self):
        chart = build_bazi_chart(
            {
                "calendar_type": "lunar",
                "lunar_date": "一九七八年二月廿八",
                "hour": 18,
                "minute": 0,
                "location": "台湾",
                "country": "中国",
            }
        )
        self.assertEqual(chart.solar_date, "1978-04-05")
        self.assertEqual(chart.lunar["month"], 2)
        self.assertEqual(chart.pillars.display(), "戊午 丙辰 丁酉 己酉")
        self.assertEqual(chart.source, "lunar_fixture_lookup")
        self.assertIn("lunar_conversion_uses_fixture_index", chart.warnings)

    def test_build_bazi_chart_matches_fixture_birth_info(self):
        known_convention_differences = {"case_31"}
        for record in self.records:
            if record.get("status") != "success":
                continue
            birth_info = record.get("birth_info") or {}
            chart = record["api_response"]["data"]["data"]
            computed = build_bazi_chart(birth_info)

            with self.subTest(case_id=record["case_id"]):
                if record["case_id"] in known_convention_differences:
                    self.assertNotEqual(computed.pillars.display(), chart["chineseDate"])
                else:
                    self.assertEqual(computed.pillars.display(), chart["chineseDate"])


if __name__ == "__main__":
    unittest.main()
