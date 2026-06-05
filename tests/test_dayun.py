import unittest

from mingli_bench.chart_api import build_bazi_chart
from mingli_bench.dayun import (
    DAYUN_SCHEMA_VERSION,
    build_dayun_analysis,
    dayun_direction,
    normalize_gender,
)


class DayunTests(unittest.TestCase):
    def test_normalize_gender(self):
        self.assertEqual(normalize_gender("女"), "female")
        self.assertEqual(normalize_gender("male"), "male")
        self.assertEqual(normalize_gender(" M "), "male")
        self.assertIsNone(normalize_gender(""))
        self.assertIsNone(normalize_gender("unknown"))

    def test_dayun_direction(self):
        self.assertEqual(dayun_direction("male", "yang").value, "forward")
        self.assertEqual(dayun_direction("female", "yin").value, "forward")
        self.assertEqual(dayun_direction("male", "yin").value, "backward")
        self.assertEqual(dayun_direction("female", "yang").value, "backward")

    def test_build_dayun_analysis_requires_gender(self):
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

        analysis = build_dayun_analysis(chart)

        self.assertEqual(analysis["schema_version"], DAYUN_SCHEMA_VERSION)
        self.assertFalse(analysis["available"])
        self.assertIn("gender", analysis["missing_inputs"])
        self.assertEqual(analysis["cycles"], [])

    def test_build_dayun_analysis_with_event_overlay(self):
        chart = build_bazi_chart(
            {
                "calendar_type": "solar",
                "year": 1990,
                "month": 8,
                "day": 16,
                "hour": 9,
                "minute": 30,
                "gender": "女",
                "country": "中国",
                "location": "上海",
            }
        )

        analysis = build_dayun_analysis(
            chart,
            event_years=[
                {
                    "year": 2026,
                    "year_pillar": "丙午",
                    "branch": "午",
                    "age": 36,
                }
            ],
        )

        self.assertTrue(analysis["available"])
        self.assertEqual(analysis["direction"], "backward")
        self.assertEqual(analysis["direction_label"], "逆排")
        self.assertGreater(analysis["start_timing"]["start_age_years"], 0)
        self.assertEqual(len(analysis["cycles"]), 10)
        self.assertEqual(analysis["cycles"][0]["pillar"], "癸未")
        self.assertEqual(analysis["event_overlays"][0]["year"], 2026)
        self.assertIsNotNone(analysis["event_overlays"][0]["active_cycle"])


if __name__ == "__main__":
    unittest.main()
