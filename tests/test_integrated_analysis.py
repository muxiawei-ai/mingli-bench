import unittest

from mingli_bench.chart_api import build_bazi_chart
from mingli_bench.hexagram import build_time_hexagram
from mingli_bench.hexagram_rules import build_hexagram_reading
from mingli_bench.integrated_analysis import (
    INTEGRATED_ANALYSIS_SCHEMA_VERSION,
    build_integrated_analysis,
)
from mingli_bench.report import build_element_profile


class IntegratedAnalysisTests(unittest.TestCase):
    def test_build_integrated_analysis_links_bazi_and_hexagram(self):
        chart = build_bazi_chart(
            {
                "calendar_type": "solar",
                "year": 1978,
                "month": 4,
                "day": 5,
                "hour": 18,
                "location": "台湾",
                "country": "中国",
            }
        )
        hexagram = build_time_hexagram(chart)
        assert hexagram is not None
        hexagram["reading"] = build_hexagram_reading(hexagram, "分析事业")

        analysis = build_integrated_analysis(
            question="分析事业",
            summary={
                "pillars_text": chart.pillars.display(),
                "day_master": chart.day_master,
                "day_master_element": chart.day_master_element,
            },
            element_profile=build_element_profile(chart),
            strongest_elements=["火", "土"],
            missing_elements=["木", "水"],
            event_years=[],
            hexagram=hexagram,
        )

        assert analysis is not None
        self.assertEqual(analysis["schema_version"], INTEGRATED_ANALYSIS_SCHEMA_VERSION)
        self.assertEqual(analysis["domain"], "事业")
        self.assertIn("日主丁", analysis["overview"])
        self.assertIn("临卦", analysis["overview"])
        self.assertEqual(
            [section["title"] for section in analysis["sections"]],
            ["八字底盘", "卦象触发", "交叉印证", "事业综合框架"],
        )
        signal_types = {signal["type"] for signal in analysis["alignment_signals"]}
        self.assertIn("reinforces_existing_pattern", signal_types)
        self.assertIn("points_to_missing_element", signal_types)
        self.assertGreaterEqual(len(analysis["next_questions"]), 2)

    def test_build_integrated_analysis_requires_hexagram(self):
        analysis = build_integrated_analysis(
            question="分析事业",
            summary={"day_master": "丁", "day_master_element": "火"},
            element_profile=[],
            strongest_elements=[],
            missing_elements=[],
            event_years=[],
            hexagram=None,
        )

        self.assertIsNone(analysis)


if __name__ == "__main__":
    unittest.main()
