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
