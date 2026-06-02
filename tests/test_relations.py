import unittest

from mingli_bench.relations import analyze_branch_interactions


class BranchRelationTests(unittest.TestCase):
    def test_analyze_branch_interactions_detects_complete_three_harmony(self):
        interactions = analyze_branch_interactions(
            "子",
            {"year": "寅", "month": "辰", "day": "亥", "hour": "申"},
        )
        labels = [interaction["label"] for interaction in interactions]

        self.assertIn("申子辰三合水局", labels)
        complete = next(
            interaction
            for interaction in interactions
            if interaction["label"] == "申子辰三合水局"
        )
        self.assertEqual(complete["type"], "three_harmony_complete")
        self.assertEqual(complete["element"], "水")
        self.assertEqual(complete["matched_natal_positions"], ["month", "hour"])

    def test_analyze_branch_interactions_detects_clash_and_harmony(self):
        interactions = analyze_branch_interactions(
            "子",
            {"year": "午", "month": "丑"},
        )
        labels = [interaction["label"] for interaction in interactions]

        self.assertIn("子午冲", labels)
        self.assertIn("子丑合土", labels)


if __name__ == "__main__":
    unittest.main()
