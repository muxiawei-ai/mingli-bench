import unittest

from mingli_bench.bazi_profile import (
    BAZI_PROFILE_SCHEMA_VERSION,
    build_bazi_profile,
    ten_god_for,
)
from mingli_bench.chart_api import build_bazi_chart


class BaziProfileTests(unittest.TestCase):
    def test_ten_god_for_day_stem(self):
        self.assertEqual(ten_god_for("丁", "火", "yin"), "比肩")
        self.assertEqual(ten_god_for("丁", "火", "yang"), "劫财")
        self.assertEqual(ten_god_for("丁", "木", "yang"), "正印")
        self.assertEqual(ten_god_for("丁", "木", "yin"), "偏印")
        self.assertEqual(ten_god_for("丁", "土", "yin"), "食神")
        self.assertEqual(ten_god_for("丁", "土", "yang"), "伤官")
        self.assertEqual(ten_god_for("丁", "金", "yin"), "偏财")
        self.assertEqual(ten_god_for("丁", "金", "yang"), "正财")
        self.assertEqual(ten_god_for("丁", "水", "yin"), "七杀")
        self.assertEqual(ten_god_for("丁", "水", "yang"), "正官")

    def test_build_bazi_profile_for_known_chart(self):
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
        profile = build_bazi_profile(chart)

        self.assertEqual(profile["schema_version"], BAZI_PROFILE_SCHEMA_VERSION)
        self.assertEqual(profile["day_master"]["stem"], "丁")
        self.assertEqual(profile["day_master"]["polarity"], "yin")
        self.assertEqual(len(profile["visible_characters"]), 8)
        self.assertEqual(profile["ten_god_summary"]["劫财"], 2)
        self.assertEqual(profile["ten_god_summary"]["偏财"], 2)
        self.assertEqual(profile["ten_god_groups"]["peer"]["count"], 3)
        self.assertEqual(profile["ten_god_groups"]["output"]["count"], 3)
        self.assertEqual(profile["ten_god_groups"]["wealth"]["count"], 2)
        self.assertEqual(profile["day_master_strength"]["level"], "self_supported")
        self.assertIn("印星/支持未见", [item["label"] for item in profile["structure_signals"]])
        self.assertIn("support_index", profile["structure_signals"][0]["summary"])

    def test_build_bazi_profile_handles_missing_hour(self):
        chart = build_bazi_chart(
            {
                "calendar_type": "solar",
                "year": 1978,
                "month": 4,
                "day": 5,
            }
        )
        profile = build_bazi_profile(chart)

        self.assertEqual(len(profile["visible_characters"]), 6)
        self.assertIn("时柱缺失", [item["label"] for item in profile["practical_focus"]])
        self.assertIn("时柱未知", [item["label"] for item in profile["structure_signals"]])


if __name__ == "__main__":
    unittest.main()
