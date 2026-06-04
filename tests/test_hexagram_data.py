import unittest

from mingli_bench.hexagram_data import (
    HEXAGRAM_TEXTS,
    TEXT_COVERAGE,
    get_hexagram_text,
    get_line_text,
    has_hexagram_text,
    validate_hexagram_texts,
)


class HexagramDataTests(unittest.TestCase):
    def test_complete_corpus_has_64_hexagrams_and_384_lines(self):
        self.assertEqual(validate_hexagram_texts(), [])
        self.assertEqual(set(HEXAGRAM_TEXTS), set(range(1, 65)))
        self.assertEqual(
            sum(len(item["lines"]) for item in HEXAGRAM_TEXTS.values()),
            384,
        )

    def test_full_corpus_contains_jing_and_sheng(self):
        jing = get_hexagram_text(48)
        sheng = get_hexagram_text(46)

        self.assertIsNotNone(jing)
        self.assertIsNotNone(sheng)
        assert jing is not None
        assert sheng is not None
        self.assertEqual(jing["theme"], "资源、基础、汲取与公共供养")
        self.assertIn("改邑不改井", jing["judgment"])
        self.assertIn("积小以高大", sheng["image"])
        self.assertEqual(jing["coverage"], TEXT_COVERAGE)

    def test_line_text_lookup_uses_one_based_line_index(self):
        line = get_line_text(48, 5)

        self.assertIsNotNone(line)
        assert line is not None
        self.assertEqual(line["text"], "井洌，寒泉食。")
        self.assertEqual(line["source"], "zhouyi_classic.v1")

    def test_all_valid_hexagrams_are_covered(self):
        self.assertTrue(has_hexagram_text(10))
        self.assertEqual(get_hexagram_text(10)["judgment"], "履虎尾，不咥人，亨。")
        self.assertEqual(get_line_text(10, 6)["text"], "视履考祥，其旋元吉。")

    def test_invalid_hexagram_returns_none(self):
        self.assertFalse(has_hexagram_text(65))
        self.assertIsNone(get_hexagram_text(65))
        self.assertIsNone(get_line_text(65, 1))


if __name__ == "__main__":
    unittest.main()
