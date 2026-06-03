from types import SimpleNamespace
import unittest
from unittest.mock import patch

from mingli_bench.models.openai_client import OpenAIClient


class FakeCompletions:
    def __init__(self, errors):
        self.calls = 0
        self.errors = list(errors)

    def create(self, **params):
        self.calls += 1
        if self.errors:
            raise self.errors.pop(0)
        message = SimpleNamespace(content="ok")
        choice = SimpleNamespace(message=message)
        return SimpleNamespace(choices=[choice])


class OpenAIClientRetryTests(unittest.TestCase):
    def _client_with_completions(self, completions):
        client = OpenAIClient(
            model_name="anthropic/claude-sonnet-4.6",
            api_key="test-key",
            base_url="https://openrouter.ai/api/v1",
        )
        client.max_retries = 1
        client.retry_delay = 0
        client.client = SimpleNamespace(
            chat=SimpleNamespace(completions=completions)
        )
        return client

    @patch("time.sleep", return_value=None)
    def test_retries_transient_connection_error(self, _sleep):
        completions = FakeCompletions([RuntimeError("Connection error.")])
        client = self._client_with_completions(completions)

        self.assertEqual(client.generate("hello"), "ok")
        self.assertEqual(completions.calls, 2)

    @patch("time.sleep", return_value=None)
    def test_does_not_retry_non_transient_error(self, _sleep):
        completions = FakeCompletions([ValueError("bad request shape")])
        client = self._client_with_completions(completions)

        with self.assertRaises(ValueError):
            client.generate("hello")
        self.assertEqual(completions.calls, 1)


if __name__ == "__main__":
    unittest.main()
