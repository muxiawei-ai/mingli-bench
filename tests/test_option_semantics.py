import unittest

from mingli_bench.option_semantics import analyze_option_semantics, extract_options


class OptionSemanticsTests(unittest.TestCase):
    def test_extract_options_from_multiline_text(self):
        options = extract_options(
            "此命1996年发生何事？\n"
            "A. 患上严重抑郁痴\n"
            "B. 回港认识现任妻子\n"
            "C. 交通意外，撞车，人平安\n"
            "D. 得到一笔意外之财"
        )

        self.assertEqual([option["letter"] for option in options], ["A", "B", "C", "D"])
        self.assertEqual(options[0]["text"], "患上严重抑郁痴")

    def test_analyze_option_semantics_labels_event_types(self):
        diagnostics = analyze_option_semantics(
            "选项：A. 患上严重抑郁痴 B. 回港认识现任妻子 "
            "C. 交通意外，撞车，人平安 D. 得到一笔意外之财"
        )
        by_letter = {item["letter"]: item for item in diagnostics}

        self.assertEqual(by_letter["A"]["primary_event_type"], "mental_health")
        self.assertIn("health_illness", by_letter["A"]["event_types"])
        self.assertEqual(by_letter["B"]["primary_event_type"], "relationship_marriage")
        self.assertIn("travel_migration", by_letter["B"]["event_types"])
        self.assertEqual(by_letter["C"]["primary_event_type"], "traffic_accident")
        self.assertEqual(by_letter["D"]["primary_event_type"], "wealth_gain")
        self.assertIn("抑郁", by_letter["A"]["matched_keywords"]["mental_health"])

    def test_analyze_option_semantics_labels_timing_years(self):
        diagnostics = analyze_option_semantics(
            "选项：A. 1999 B. 2002 C. 2006 D. 到2022年为止，单身"
        )
        by_letter = {item["letter"]: item for item in diagnostics}

        self.assertEqual(by_letter["A"]["primary_event_type"], "timing_year")
        self.assertEqual(by_letter["C"]["labels"], ["年份/时间点"])
        self.assertEqual(by_letter["D"]["primary_event_type"], "relationship_marriage")


if __name__ == "__main__":
    unittest.main()
