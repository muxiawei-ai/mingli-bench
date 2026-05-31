import unittest

from mingli_bench.calendar import (
    count_five_elements,
    hour_branch,
    parse_bazi_pillars,
    sexagenary_index,
    sexagenary_name,
)


class CalendarHelperTests(unittest.TestCase):
    def test_sexagenary_cycle_round_trip(self):
        self.assertEqual(sexagenary_name(0), "甲子")
        self.assertEqual(sexagenary_name(59), "癸亥")
        self.assertEqual(sexagenary_index("甲子"), 0)
        self.assertEqual(sexagenary_index("癸亥"), 59)

    def test_hour_branch(self):
        self.assertEqual(hour_branch(23), "子")
        self.assertEqual(hour_branch(0), "子")
        self.assertEqual(hour_branch(1), "丑")
        self.assertEqual(hour_branch(15), "申")
        self.assertEqual(hour_branch(22), "亥")

    def test_parse_bazi_pillars(self):
        summary = parse_bazi_pillars("甲寅 戊辰 己亥 壬申")
        self.assertEqual(summary["year_pillar"], "甲寅")
        self.assertEqual(summary["day_master"], "己")
        self.assertEqual(summary["day_master_element"], "土")
        self.assertEqual(summary["five_elements_summary"]["木"], 2)

    def test_count_five_elements_rejects_unknown_characters(self):
        with self.assertRaises(ValueError):
            count_five_elements(["甲X"])


if __name__ == "__main__":
    unittest.main()
