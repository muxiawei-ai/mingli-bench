import unittest

from mingli_bench.chart_api import build_bazi_chart
from mingli_bench.hexagram import (
    build_time_hexagram,
    build_time_hexagram_from_datetime,
    build_time_hexagram_from_numbers,
    lookup_hexagram,
)


class HexagramTests(unittest.TestCase):
    def test_lookup_hexagram_by_trigrams(self):
        hexagram = lookup_hexagram("坎", "巽", role="本卦")
        self.assertEqual(hexagram["name"], "井卦")
        self.assertEqual(hexagram["symbol"], "䷯")
        self.assertEqual(hexagram["number"], 48)
        self.assertEqual(hexagram["lines"], ["yin", "yang", "yang", "yin", "yang", "yin"])
        self.assertEqual(hexagram["theme"], "资源、基础、汲取与公共供养")
        self.assertIn("改邑不改井", hexagram["judgment"])
        self.assertEqual(hexagram["text_source"], "zhouyi_classic.v1")

    def test_time_hexagram_from_known_chart(self):
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
        hexagram = build_time_hexagram(chart)

        self.assertIsNotNone(hexagram)
        assert hexagram is not None
        self.assertEqual(hexagram["method"], "梅花易数时间法")
        self.assertEqual(hexagram["schema_version"], "hexagram.v1")
        self.assertEqual(hexagram["time_source"], "birth_time")
        self.assertEqual(hexagram["time_source_label"], "出生时间起卦")
        self.assertEqual(hexagram["input_datetime"], "1978-04-05T18:00")
        self.assertEqual(hexagram["number_source"]["year_branch"], "午")
        self.assertEqual(hexagram["number_source"]["year_number"], 7)
        self.assertEqual(hexagram["number_source"]["month_number"], 4)
        self.assertEqual(hexagram["number_source"]["day_number"], 5)
        self.assertEqual(hexagram["number_source"]["hour_branch"], "酉")
        self.assertEqual(hexagram["number_source"]["hour_number"], 10)
        self.assertEqual(hexagram["primary"]["name"], "临卦")
        self.assertEqual(hexagram["primary"]["number"], 19)
        self.assertEqual(hexagram["changed"]["name"], "复卦")
        self.assertEqual(hexagram["changed"]["number"], 24)
        self.assertEqual(hexagram["moving_line"], 2)
        self.assertEqual(hexagram["moving_line_name"], "九二")
        self.assertEqual(hexagram["moving_line_text"], "咸临，吉，无不利。")
        self.assertEqual(hexagram["moving_line_source"], "zhouyi_classic.v1")
        self.assertIn("元亨", hexagram["primary"]["judgment"])
        self.assertIn("七日来复", hexagram["changed"]["judgment"])
        self.assertEqual(hexagram["line_details"][1]["text"], "咸临，吉，无不利。")
        self.assertIn("公历输入", "\n".join(hexagram["caveats"]))

    def test_chart_hexagram_entrypoint_rejects_question_time_label(self):
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

        with self.assertRaisesRegex(ValueError, "birth_time"):
            build_time_hexagram(chart, time_source="question_time")

    def test_time_hexagram_from_manual_numbers_matches_chart_path(self):
        hexagram = build_time_hexagram_from_numbers(
            year_branch="午",
            month_number="4",
            day_number="5",
            hour_branch="酉",
        )

        self.assertEqual(hexagram["time_source"], "manual_numbers")
        self.assertEqual(hexagram["time_source_label"], "手动数字起卦")
        self.assertEqual(hexagram["primary"]["name"], "临卦")
        self.assertEqual(hexagram["changed"]["name"], "复卦")
        self.assertEqual(hexagram["moving_line_name"], "九二")
        self.assertEqual(hexagram["number_source"]["calendar_source"], "manual_numbers")

    def test_time_hexagram_from_datetime_uses_specified_time_source(self):
        hexagram = build_time_hexagram_from_datetime(
            "2026-06-05T20:52",
            time_source="specified_time",
        )

        self.assertEqual(hexagram["time_source"], "specified_time")
        self.assertEqual(hexagram["time_source_label"], "指定时间起卦")
        self.assertEqual(hexagram["input_datetime"], "2026-06-05T20:52")
        self.assertEqual(hexagram["number_source"]["year_branch"], "午")
        self.assertEqual(hexagram["number_source"]["month_number"], 6)
        self.assertEqual(hexagram["number_source"]["day_number"], 5)
        self.assertEqual(hexagram["number_source"]["hour_branch"], "戌")
        self.assertEqual(hexagram["primary"]["name"], "大过卦")
        self.assertEqual(hexagram["changed"]["name"], "恒卦")
        self.assertEqual(hexagram["moving_line_name"], "九五")

    def test_time_hexagram_from_date_uses_noon_caveat(self):
        hexagram = build_time_hexagram_from_datetime("2026-06-05")

        self.assertEqual(hexagram["input_datetime"], "2026-06-05T12:00")
        self.assertIn("午时 12:00", "\n".join(hexagram["caveats"]))

    def test_lookup_all_valid_hexagrams_have_text_source(self):
        hexagram = lookup_hexagram("乾", "兑", role="本卦")

        self.assertEqual(hexagram["name"], "履卦")
        self.assertEqual(hexagram["judgment"], "履虎尾，不咥人，亨。")
        self.assertEqual(hexagram["text_source"], "zhouyi_classic.v1")
        self.assertEqual(hexagram["text_coverage"], "full_64")

    def test_time_hexagram_requires_birth_hour(self):
        chart = build_bazi_chart(
            {
                "calendar_type": "solar",
                "year": 1978,
                "month": 4,
                "day": 5,
            }
        )
        self.assertIsNone(build_time_hexagram(chart))


if __name__ == "__main__":
    unittest.main()
