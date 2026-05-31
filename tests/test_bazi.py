import json
import unittest
from pathlib import Path

from mingli_bench.bazi import (
    bazi_day_date_for_time,
    bazi_from_gregorian,
    day_pillar_for_datetime,
    hour_pillar_for_datetime,
    year_pillar_for_date,
)


class BaziCoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = json.loads(Path("data/fortune_api_results.json").read_text(encoding="utf-8"))

    def test_case_1_partial_bazi(self):
        chart = bazi_from_gregorian("1974-04-28", hour=16, minute=40)
        self.assertEqual(chart["year_pillar"], "甲寅")
        self.assertEqual(chart["day_pillar"], "己亥")
        self.assertEqual(chart["hour_pillar"], "壬申")
        self.assertIsNone(chart["month_pillar"])
        self.assertIn("month_pillar_requires_solar_terms", chart["warnings"])

    def test_late_zi_hour_rolls_to_next_bazi_day(self):
        self.assertEqual(str(bazi_day_date_for_time("1966-10-18", 23)), "1966-10-19")
        self.assertEqual(day_pillar_for_datetime("1966-10-18", 23), "辛亥")
        self.assertEqual(hour_pillar_for_datetime("1966-10-18", 23, 15), "戊子")

    def test_day_and_hour_pillars_match_chart_fixtures(self):
        for record in self.records:
            if record.get("status") != "success":
                continue
            chart = record["api_response"]["data"]["data"]
            year_pillar, _month_pillar, day_pillar, hour_pillar = chart["chineseDate"].split()
            birth_info = record.get("birth_info") or {}
            solar_date = chart["solarDate"]
            hour = birth_info.get("hour")
            minute = birth_info.get("minute") or 0

            with self.subTest(case_id=record["case_id"]):
                self.assertEqual(day_pillar_for_datetime(solar_date, hour), day_pillar)
                if hour is not None:
                    self.assertEqual(hour_pillar_for_datetime(solar_date, hour, minute), hour_pillar)

                # Avoid Jan/Feb boundary conventions until solar-term/lunar-year
                # handling is implemented explicitly.
                if int(solar_date[5:7]) > 2:
                    self.assertEqual(year_pillar_for_date(solar_date), year_pillar)


if __name__ == "__main__":
    unittest.main()
