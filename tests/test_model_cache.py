import json
import tempfile
import unittest
from pathlib import Path

from mingli_bench.models.cache import CachedModelClient


class CountingModelClient:
    model_name = "provider/test-model"
    temperature = 0.0
    max_tokens = 128
    config = {"base_url": "https://example.test", "api_key": "secret-key"}

    def __init__(self):
        self.calls = 0

    def generate(self, prompt: str, **kwargs):
        self.calls += 1
        return f"response:{self.calls}:{prompt}:{kwargs.get('tag', '')}"

    def validate_api_key(self):
        return True

    def get_config(self):
        return {
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            **self.config,
        }


class CachedModelClientTests(unittest.TestCase):
    def test_exact_prompt_cache_hit_skips_wrapped_call(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            wrapped = CountingModelClient()
            client = CachedModelClient(wrapped, cache_dir=tmpdir)

            first = client.generate("hello", tag="a")
            self.assertFalse(client.last_cache_hit)
            second = client.generate("hello", tag="a")
            self.assertTrue(client.last_cache_hit)

            self.assertEqual(first, second)
            self.assertEqual(wrapped.calls, 1)
            self.assertTrue(Path(client.last_cache_path).exists())

    def test_cache_key_changes_with_generation_kwargs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            wrapped = CountingModelClient()
            client = CachedModelClient(wrapped, cache_dir=tmpdir)

            first = client.generate("hello", tag="a")
            second = client.generate("hello", tag="b")

            self.assertNotEqual(first, second)
            self.assertEqual(wrapped.calls, 2)

    def test_cache_file_does_not_store_api_key(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            wrapped = CountingModelClient()
            client = CachedModelClient(wrapped, cache_dir=tmpdir)

            client.generate("hello")
            payload = json.loads(Path(client.last_cache_path).read_text(encoding="utf-8"))

            self.assertNotIn("secret-key", json.dumps(payload, ensure_ascii=False))
            self.assertIsInstance(payload["prompt_sha256"], str)
            self.assertEqual(len(payload["prompt_sha256"]), 64)
            self.assertEqual(payload["response"], "response:1:hello:")


if __name__ == "__main__":
    unittest.main()
