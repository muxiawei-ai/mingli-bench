import unittest

from mingli_bench.hexagram_data import (
    get_hexagram_text,
    get_line_text,
    has_hexagram_text,
)


class HexagramDataTests(unittest.TestCase):
    def test_initial_subset_contains_jing_and_sheng(self):
        jing = get_hexagram_text(48)
        sheng = get_hexagram_text(46)

        self.assertIsNotNone(jing)
        self.assertIsNotNone(sheng)
        assert jing is not None
        assert sheng is not None
        self.assertEqual(jing["theme"], "资源、基础、汲取与公共供养")
        self.assertIn("改邑不改井", jing["judgment"])
        self.assertIn("积小以高大", sheng["image"])

    def test_line_text_lookup_uses_one_based_line_index(self):
        line = get_line_text(48, 5)

        self.assertIsNotNone(line)
        assert line is not None
        self.assertEqual(line["text"], "井洌，寒泉食。")
        self.assertEqual(line["source"], "zhouyi_classic.v1")

    def test_uncovered_hexagram_returns_none(self):
        self.assertFalse(has_hexagram_text(10))
        self.assertIsNone(get_hexagram_text(10))
        self.assertIsNone(get_line_text(10, 1))


if __name__ == "__main__":
    unittest.main()
