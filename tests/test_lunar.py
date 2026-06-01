import unittest

from mingli_bench.lunar import (
    lunar_from_solar_date,
    parse_chinese_lunar_date,
    solar_from_lunar_date,
)


class LunarUtilityTests(unittest.TestCase):
    def test_parse_regular_lunar_date(self):
        lunar = parse_chinese_lunar_date("一九七八年二月廿八")
        self.assertEqual(lunar.as_dict(), {
            "year": 1978,
            "month": 2,
            "day": 28,
            "is_leap_month": False,
        })

    def test_parse_leap_and_winter_months(self):
        leap = parse_chinese_lunar_date("一九八四年闰十月十七")
        self.assertEqual(leap.year, 1984)
        self.assertEqual(leap.month, 10)
        self.assertEqual(leap.day, 17)
        self.assertTrue(leap.is_leap_month)

        winter = parse_chinese_lunar_date("一九七一年冬月廿二")
        self.assertEqual(winter.month, 11)
        self.assertEqual(winter.day, 22)

    def test_fixture_backed_lunar_from_solar(self):
        result = lunar_from_solar_date("1978-04-05")
        self.assertEqual(result["case_id"], "case_13")
        self.assertEqual(result["lunar"]["year"], 1978)
        self.assertEqual(result["lunar"]["month"], 2)
        self.assertEqual(result["lunar"]["day"], 28)

    def test_fixture_backed_solar_from_lunar(self):
        result = solar_from_lunar_date("一九七八年二月廿八")
        self.assertEqual(result["case_id"], "case_13")
        self.assertEqual(result["solar_date"], "1978-04-05")


if __name__ == "__main__":
    unittest.main()
