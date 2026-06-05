"""Tests for the standalone hexagram casting API.

These tests exercise HexagramInput, hexagram_input_from_datetime, and
cast_hexagram without requiring a BaziChart object.
"""
import unittest
from datetime import datetime

from mingli_bench.hexagram import (
    HexagramInput,
    cast_hexagram,
    hexagram_input_from_datetime,
)


# The 1978-04-05 18:00 case is the same reference used in test_hexagram.py
# (build_time_hexagram path), so we can assert identical numbers here.
_REF_DT = datetime(1978, 4, 5, 18, 0)
_REF_HI = HexagramInput(
    year_branch="午",
    month_number=4,
    day_number=5,
    hour_branch="酉",
    number_source="solar_input_proxy",
    source_type="birth_time",
    source_label="reference",
)


class HexagramInputFromDatetimeTests(unittest.TestCase):
    def test_solar_proxy_fields(self):
        hi = hexagram_input_from_datetime(_REF_DT, source_type="birth_time")
        self.assertEqual(hi.year_branch, "午")
        self.assertEqual(hi.hour_branch, "酉")
        self.assertEqual(hi.month_number, 4)
        self.assertEqual(hi.day_number, 5)
        self.assertEqual(hi.number_source, "solar_input_proxy")
        self.assertEqual(hi.source_type, "birth_time")
        self.assertIn("1978-04-05", hi.source_label)

    def test_lunar_override_sets_lunar_source(self):
        hi = hexagram_input_from_datetime(
            _REF_DT, source_type="birth_time", lunar_month=3, lunar_day=8
        )
        self.assertEqual(hi.month_number, 3)
        self.assertEqual(hi.day_number, 8)
        self.assertEqual(hi.number_source, "lunar_date")
        self.assertIn("农历", hi.source_label)

    def test_requires_both_lunar_params_or_neither(self):
        # Only lunar_month provided → falls back to solar proxy (no error)
        hi = hexagram_input_from_datetime(_REF_DT, lunar_month=3)
        self.assertEqual(hi.number_source, "solar_input_proxy")
        self.assertEqual(hi.month_number, _REF_DT.month)

    def test_question_time_source_type(self):
        dt = datetime(2024, 6, 15, 14, 30)
        hi = hexagram_input_from_datetime(dt, source_type="question_time")
        self.assertEqual(hi.source_type, "question_time")

    def test_default_source_type_is_casting_time(self):
        hi = hexagram_input_from_datetime(datetime(2024, 1, 1, 12, 0))
        self.assertEqual(hi.source_type, "casting_time")

    def test_frozen_dataclass_is_hashable(self):
        hi = hexagram_input_from_datetime(_REF_DT)
        self.assertIsNotNone(hash(hi))
        d = {hi: "ok"}
        self.assertEqual(d[hi], "ok")


class CastHexagramTests(unittest.TestCase):
    def test_matches_known_expected_values(self):
        """Results must match build_time_hexagram for the same reference case."""
        result = cast_hexagram(_REF_HI)
        self.assertEqual(result["primary"]["name"], "临卦")
        self.assertEqual(result["primary"]["number"], 19)
        self.assertEqual(result["changed"]["name"], "复卦")
        self.assertEqual(result["changed"]["number"], 24)
        self.assertEqual(result["moving_line"], 2)
        self.assertEqual(result["moving_line_name"], "九二")
        self.assertEqual(result["moving_line_text"], "咸临，吉，无不利。")
        self.assertEqual(result["moving_line_source"], "zhouyi_classic.v1")

    def test_all_schema_keys_present(self):
        result = cast_hexagram(_REF_HI)
        expected_keys = {
            "method", "source_type", "source_label", "basis",
            "number_source", "primary", "changed", "moving_line",
            "moving_line_name", "moving_line_text", "moving_line_note",
            "moving_line_source", "interpretation", "caveats", "line_details",
        }
        self.assertEqual(expected_keys, set(result) & expected_keys)

    def test_number_source_block_values(self):
        result = cast_hexagram(_REF_HI)
        ns = result["number_source"]
        self.assertEqual(ns["year_branch"], "午")
        self.assertEqual(ns["year_number"], 7)
        self.assertEqual(ns["month_number"], 4)
        self.assertEqual(ns["day_number"], 5)
        self.assertEqual(ns["hour_branch"], "酉")
        self.assertEqual(ns["hour_number"], 10)
        self.assertEqual(ns["calendar_source"], "solar_input_proxy")
        self.assertEqual(ns["upper_total"], 7 + 4 + 5)   # 16
        self.assertEqual(ns["lower_total"], 16 + 10)       # 26

    def test_six_line_details(self):
        result = cast_hexagram(_REF_HI)
        self.assertEqual(len(result["line_details"]), 6)
        self.assertEqual(result["line_details"][1]["text"], "咸临，吉，无不利。")

    def test_solar_caveat_present_for_proxy(self):
        result = cast_hexagram(_REF_HI)
        joined = "\n".join(result["caveats"])
        self.assertIn("公历输入", joined)

    def test_no_solar_caveat_when_lunar_provided(self):
        hi = hexagram_input_from_datetime(
            _REF_DT, source_type="birth_time", lunar_month=3, lunar_day=8
        )
        result = cast_hexagram(hi)
        joined = "\n".join(result["caveats"])
        self.assertNotIn("公历", joined)

    def test_question_time_mode_end_to_end(self):
        dt = datetime(2024, 6, 15, 14, 30)
        hi = hexagram_input_from_datetime(dt, source_type="question_time")
        result = cast_hexagram(hi)
        self.assertEqual(result["method"], "梅花易数时间法")
        self.assertEqual(result["source_type"], "question_time")
        self.assertIn(result["moving_line"], range(1, 7))
        self.assertIsNotNone(result["primary"]["name"])
        self.assertIsNotNone(result["changed"]["name"])

    def test_roundtrip_datetime_matches_manual_hi(self):
        """hexagram_input_from_datetime on the reference date should produce
        the same hexagram as the hand-crafted HexagramInput."""
        hi_auto = hexagram_input_from_datetime(_REF_DT, source_type="birth_time")
        r_auto = cast_hexagram(hi_auto)
        r_manual = cast_hexagram(_REF_HI)
        self.assertEqual(r_auto["primary"]["name"], r_manual["primary"]["name"])
        self.assertEqual(r_auto["moving_line"], r_manual["moving_line"])

    def test_method_label(self):
        result = cast_hexagram(_REF_HI)
        self.assertEqual(result["method"], "梅花易数时间法")

    def test_basis_contains_two_entries(self):
        result = cast_hexagram(_REF_HI)
        self.assertEqual(len(result["basis"]), 2)
        self.assertIn("上卦", result["basis"][0])
        self.assertIn("下卦", result["basis"][1])
        self.assertIn("动爻", result["basis"][1])


if __name__ == "__main__":
    unittest.main()
