"""Tests for DataLoader changes: seed-based shuffle, get_categories validation."""
import unittest

from mingli_bench.data.loader import DataLoader


class DataLoaderSeedTests(unittest.TestCase):
    def setUp(self):
        self.loader = DataLoader()

    def test_seed_produces_same_order_across_calls(self):
        q1 = self.loader.load_questions(shuffle=True, seed=42)
        q2 = self.loader.load_questions(shuffle=True, seed=42)
        self.assertEqual([q["id"] for q in q1], [q["id"] for q in q2])

    def test_different_seeds_produce_different_orders(self):
        q1 = self.loader.load_questions(shuffle=True, seed=1)
        q2 = self.loader.load_questions(shuffle=True, seed=2)
        # With 160 questions two different seeds are astronomically unlikely to
        # produce the same permutation.
        self.assertNotEqual([q["id"] for q in q1], [q["id"] for q in q2])

    def test_no_seed_does_not_raise(self):
        questions = self.loader.load_questions(shuffle=True, seed=None)
        self.assertGreater(len(questions), 0)

    def test_seed_with_sample_size_is_reproducible(self):
        q1 = self.loader.load_questions(shuffle=True, seed=7, sample_size=10)
        q2 = self.loader.load_questions(shuffle=True, seed=7, sample_size=10)
        self.assertEqual([q["id"] for q in q1], [q["id"] for q in q2])
        self.assertEqual(len(q1), 10)


class DataLoaderGetCategoriesTests(unittest.TestCase):
    def setUp(self):
        self.loader = DataLoader()

    def test_get_categories_returns_sorted_list(self):
        categories = self.loader.get_categories()
        self.assertIsInstance(categories, list)
        self.assertEqual(categories, sorted(categories))

    def test_get_categories_returns_only_validated_question_categories(self):
        """Categories should only include entries present in validated questions."""
        categories = self.loader.get_categories()
        # Every returned category must appear in validated questions.
        valid_questions = self.loader.load_questions(shuffle=False)
        valid_cats = {q["category"] for q in valid_questions if q.get("category")}
        self.assertEqual(set(categories), valid_cats)

    def test_get_categories_no_empty_strings(self):
        categories = self.loader.get_categories()
        self.assertTrue(all(c for c in categories))


if __name__ == "__main__":
    unittest.main()
