import unittest

from mingli_bench.bazi import bazi_from_birth_info
from mingli_bench.locations import resolve_timezone


class LocationNormalizationTests(unittest.TestCase):
    def test_resolve_known_asia_locations(self):
        hong_kong = resolve_timezone("香港", country="中国")
        self.assertEqual(hong_kong.timezone, "Asia/Hong_Kong")
        self.assertEqual(hong_kong.utc_offset_hours, 8.0)
        self.assertEqual(hong_kong.warnings, ())

        miyazaki = resolve_timezone("宫崎县")
        self.assertEqual(miyazaki.timezone, "Asia/Tokyo")
        self.assertEqual(miyazaki.utc_offset_hours, 9.0)

    def test_ambiguous_usa_location_warns_and_defaults(self):
        resolved = resolve_timezone("usa")
        self.assertEqual(resolved.confidence, "default")
        self.assertEqual(resolved.utc_offset_hours, 8.0)
        self.assertIn("ambiguous_usa_location_requires_state_or_city", resolved.warnings)

    def test_bazi_from_birth_info_includes_timezone_metadata(self):
        chart = bazi_from_birth_info(
            {
                "raw": "女命：西历1978年04月05日17：00-19：00酉时  台湾生",
                "gender": "女",
                "year": 1978,
                "month": 4,
                "day": 5,
                "hour": 18,
                "minute": 0,
                "country": "中国",
                "location": "台湾",
                "calendar_type": "solar",
            }
        )
        self.assertEqual(chart["year_pillar"], "戊午")
        self.assertEqual(chart["month_pillar"], "丙辰")
        self.assertEqual(chart["day_pillar"], "丁酉")
        self.assertEqual(chart["hour_pillar"], "己酉")
        self.assertEqual(chart["timezone"]["timezone"], "Asia/Taipei")
        self.assertEqual(chart["warnings"], [])


if __name__ == "__main__":
    unittest.main()
