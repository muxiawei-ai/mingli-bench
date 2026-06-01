import unittest

from mingli_bench.intent import DEFAULT_DOMAIN, parse_question_intent


class QuestionIntentTests(unittest.TestCase):
    def test_parse_career_and_personality_question(self):
        intent = parse_question_intent("分析事业和性格")
        self.assertEqual(intent.primary_domain, "事业")
        self.assertIn("事业", intent.domains)
        self.assertIn("性格", intent.domains)
        self.assertGreater(intent.confidence, 0.5)
        self.assertIn("事业", intent.matched_keywords)

    def test_parse_relationship_question(self):
        intent = parse_question_intent("我未来的婚姻和感情怎么样")
        self.assertEqual(intent.primary_domain, "婚姻")
        self.assertIn("关系倾向", intent.section_hints)
        self.assertFalse(intent.needs_clarification)

    def test_parse_health_question(self):
        intent = parse_question_intent("健康和睡眠要注意什么")
        self.assertEqual(intent.primary_domain, "健康")
        self.assertIn("健康", intent.matched_keywords)
        self.assertIn("睡眠", intent.matched_keywords["健康"])

    def test_parse_unknown_question_needs_clarification(self):
        intent = parse_question_intent("帮我看看")
        self.assertEqual(intent.primary_domain, DEFAULT_DOMAIN)
        self.assertTrue(intent.needs_clarification)
        self.assertLess(intent.confidence, 0.5)


if __name__ == "__main__":
    unittest.main()
