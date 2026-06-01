import unittest

from mingli_bench.charts import get_chart_summary, load_fortune_records


class ChartUtilityTests(unittest.TestCase):
    def test_load_fortune_records(self):
        records = load_fortune_records("data/fortune_api_results.json")
        self.assertGreater(len(records), 0)
        self.assertIn("case_id", records[0])

    def test_get_chart_summary(self):
        summary = get_chart_summary("case_1", path="data/fortune_api_results.json")
        self.assertEqual(summary["case_id"], "case_1")
        self.assertEqual(summary["bazi"]["chinese_date"], "甲寅 戊辰 己亥 壬申")
        self.assertEqual(summary["bazi"]["hour_pillar"], "壬申")
        self.assertEqual(summary["bazi"]["lunar"]["month"], 4)
        self.assertEqual(summary["bazi"]["lunar"]["day"], 7)
        self.assertGreaterEqual(len(summary["ziwei"]["palaces"]), 12)


if __name__ == "__main__":
    unittest.main()
