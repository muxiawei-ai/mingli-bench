import unittest

from mingli_bench.candidate_years import (
    SCORING_VARIANTS,
    build_candidate_year_scores,
    infer_timing_focus,
)


class CandidateYearScoringTests(unittest.TestCase):
    def test_infer_timing_focus(self):
        self.assertEqual(infer_timing_focus("此命何年结婚？"), "marriage_timing")
        self.assertEqual(infer_timing_focus("女儿于何年出生？"), "children_timing")
        self.assertEqual(infer_timing_focus("2020年生病？"), "health_timing")
        self.assertEqual(infer_timing_focus("何年发生大事？"), "general_timing")

    def test_build_candidate_year_scores(self):
        event_years = [
            {
                "year": 2007,
                "year_pillar": "丁亥",
                "branch_relation_to_day_master": "generates_day_master",
                "branch_interactions": [
                    {
                        "type": "six_clash",
                        "label": "巳亥冲",
                        "natal_position": "month",
                    },
                    {
                        "type": "three_meeting_partial",
                        "label": "亥丑半会水",
                        "matched_natal_positions": ["hour"],
                    },
                ],
            },
            {
                "year": 2009,
                "year_pillar": "己丑",
                "branch_relation_to_day_master": "controlled_by_day_master",
                "branch_interactions": [
                    {
                        "type": "same_branch",
                        "label": "丑丑同支",
                        "natal_position": "hour",
                    },
                    {
                        "type": "three_harmony_complete",
                        "label": "巳酉丑三合金局",
                        "matched_natal_positions": ["year", "month"],
                    },
                ],
            },
        ]
        option_semantics = [
            {"letter": "A", "text": "2007年"},
            {"letter": "B", "text": "2009年"},
            {"letter": "C", "text": "不是年份"},
        ]

        scores = build_candidate_year_scores(
            "此命有一名女儿于何年出生？",
            event_years,
            option_semantics,
        )
        by_letter = {item["letter"]: item for item in scores}

        self.assertEqual([item["letter"] for item in scores], ["A", "B"])
        self.assertEqual(by_letter["A"]["focus"], "children_timing")
        self.assertEqual(by_letter["A"]["year_pillar"], "丁亥")
        self.assertIn("hour", by_letter["A"]["matched_positions"])
        self.assertGreater(by_letter["B"]["score"], 0)
        self.assertIn("rank", by_letter["B"])
        self.assertEqual(
            set(by_letter["A"]["variant_scores"]),
            set(SCORING_VARIANTS),
        )
        self.assertEqual(
            set(by_letter["A"]["variant_ranks"]),
            set(SCORING_VARIANTS),
        )
        self.assertEqual(by_letter["A"]["score"], by_letter["A"]["variant_scores"]["default"])
        self.assertEqual(by_letter["A"]["rank"], by_letter["A"]["variant_ranks"]["default"])


if __name__ == "__main__":
    unittest.main()
