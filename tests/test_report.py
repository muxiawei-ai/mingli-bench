import unittest

from mingli_bench.chart_api import build_bazi_chart
from mingli_bench.report import (
    build_chart_report,
    build_element_profile,
    classify_element_count,
    relation_to_day_master,
)


class ChartReportTests(unittest.TestCase):
    def test_classify_element_count(self):
        self.assertEqual(classify_element_count(0), "absent")
        self.assertEqual(classify_element_count(1), "light")
        self.assertEqual(classify_element_count(2), "present")
        self.assertEqual(classify_element_count(3), "high")

    def test_relation_to_day_master(self):
        self.assertEqual(relation_to_day_master("火", "火"), "same_as_day_master")
        self.assertEqual(relation_to_day_master("土", "火"), "generated_by_day_master")
        self.assertEqual(relation_to_day_master("木", "火"), "generates_day_master")
        self.assertEqual(relation_to_day_master("金", "火"), "controlled_by_day_master")
        self.assertEqual(relation_to_day_master("水", "火"), "controls_day_master")

    def test_build_element_profile_has_all_five_elements(self):
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
        profile = build_element_profile(chart)
        self.assertEqual([signal.element for signal in profile], ["木", "火", "土", "金", "水"])
        self.assertEqual(sum(signal.count for signal in profile), 8)

    def test_build_chart_report(self):
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
        report = build_chart_report(chart, "分析事业")
        self.assertEqual(report.summary["pillars_text"], "戊午 丙辰 丁酉 己酉")
        self.assertEqual(report.strongest_elements, ["火", "土"])
        self.assertEqual(report.missing_elements, ["木", "水"])
        self.assertTrue(report.input_quality["has_birth_time"])
        self.assertIn("本地报告只整理排盘结构", report.to_markdown())

    def test_build_chart_report_extracts_event_years(self):
        chart = build_bazi_chart(
            {
                "calendar_type": "solar",
                "year": 1974,
                "month": 4,
                "day": 28,
                "hour": 16,
                "minute": 40,
                "location": "usa",
                "country": "usa",
            }
        )
        report = build_chart_report(
            chart,
            "此命1996年发生何事？选项：A. 2008年 B. 1996年",
        )
        self.assertEqual([item["year"] for item in report.event_years], [1996, 2008])
        self.assertEqual(report.event_years[0]["year_pillar"], "丙子")
        self.assertEqual(report.event_years[0]["age"], 22)
        self.assertEqual(report.event_years[0]["nominal_age"], 23)
        self.assertEqual(report.event_years[0]["stem_element"], "火")
        self.assertEqual(report.event_years[0]["branch_element"], "水")
        self.assertEqual(
            report.event_years[0]["stem_relation_to_day_master"],
            "generates_day_master",
        )
        self.assertEqual(
            report.event_years[0]["branch_relation_to_day_master"],
            "controlled_by_day_master",
        )
        labels = [
            interaction["label"]
            for interaction in report.event_years[0]["branch_interactions"]
        ]
        self.assertIn("申子辰三合水局", labels)
        self.assertEqual(report.event_years[1]["year_pillar"], "戊子")
        self.assertIn("1996: 丙子", report.to_markdown())
        self.assertIn("申子辰三合水局", report.to_markdown())

    def test_report_followups_for_missing_time_and_location(self):
        chart = build_bazi_chart(
            {
                "calendar_type": "solar",
                "year": 1978,
                "month": 4,
                "day": 5,
            }
        )
        report = build_chart_report(chart, "")
        self.assertFalse(report.input_quality["has_birth_time"])
        self.assertGreaterEqual(len(report.follow_up_questions), 2)
        self.assertIn("出生时间未知", "\n".join(report.caveats))


if __name__ == "__main__":
    unittest.main()
