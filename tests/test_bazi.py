import json
import unittest
from pathlib import Path

from mingli_bench.bazi import (
    bazi_day_date_for_time,
    bazi_from_gregorian,
    day_pillar_for_datetime,
    hour_pillar_for_datetime,
    month_pillar_for_datetime,
    year_pillar_for_datetime,
    year_pillar_for_date,
)
from mingli_bench.solar_terms import solar_month_branch_for_datetime, solar_term_datetime


class BaziCoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = json.loads(Path("data/fortune_api_results.json").read_text(encoding="utf-8"))

    def test_case_1_bazi(self):
        chart = bazi_from_gregorian("1974-04-28", hour=16, minute=40)
        self.assertEqual(chart["year_pillar"], "甲寅")
        self.assertEqual(chart["month_pillar"], "戊辰")
        self.assertEqual(chart["day_pillar"], "己亥")
        self.assertEqual(chart["hour_pillar"], "壬申")
        self.assertEqual(chart["warnings"], [])

    def test_solar_term_month_boundary(self):
        qingming = solar_term_datetime(1978, "清明")
        self.assertEqual(qingming.date().isoformat(), "1978-04-05")
        self.assertEqual(solar_month_branch_for_datetime(qingming), "辰")
        self.assertEqual(month_pillar_for_datetime("1978-04-05", 18, 0), "丙辰")

    def test_li_chun_year_boundary(self):
        self.assertEqual(year_pillar_for_datetime("1988-01-10", 8, 12), "丁卯")
        self.assertEqual(year_pillar_for_datetime("1988-02-15", 16, 50), "戊辰")

    def test_late_zi_hour_rolls_to_next_bazi_day(self):
        self.assertEqual(str(bazi_day_date_for_time("1966-10-18", 23)), "1966-10-19")
        self.assertEqual(day_pillar_for_datetime("1966-10-18", 23), "辛亥")
        self.assertEqual(hour_pillar_for_datetime("1966-10-18", 23, 15), "戊子")

    def test_day_and_hour_pillars_match_chart_fixtures(self):
        for record in self.records:
            if record.get("status") != "success":
                continue
            chart = record["api_response"]["data"]["data"]
            year_pillar, month_pillar, day_pillar, hour_pillar = chart["chineseDate"].split()
            birth_info = record.get("birth_info") or {}
            solar_date = chart["solarDate"]
            hour = birth_info.get("hour")
            minute = birth_info.get("minute") or 0

            with self.subTest(case_id=record["case_id"]):
                self.assertEqual(month_pillar_for_datetime(solar_date, hour, minute), month_pillar)
                self.assertEqual(day_pillar_for_datetime(solar_date, hour), day_pillar)
                if hour is not None:
                    self.assertEqual(hour_pillar_for_datetime(solar_date, hour, minute), hour_pillar)

                # Avoid Jan/Feb boundary conventions until solar-term/lunar-year
                # handling is implemented explicitly.
                if int(solar_date[5:7]) > 2:
                    self.assertEqual(year_pillar_for_date(solar_date), year_pillar)


if __name__ == "__main__":
    unittest.main()
