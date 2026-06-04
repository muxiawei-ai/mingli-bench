import unittest

from mingli_bench.chart_api import build_bazi_chart
from mingli_bench.hexagram import build_time_hexagram, lookup_hexagram


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
