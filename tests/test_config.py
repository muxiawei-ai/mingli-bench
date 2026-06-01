import os
import tempfile
import unittest
from unittest.mock import patch

from mingli_bench.utils.config import load_config


class ConfigTests(unittest.TestCase):
    def test_generic_llm_env_populates_openrouter_config(self):
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as env_file:
            env_file.write("LLM_API_KEY=generic-key\n")
            env_file.write("LLM_MODEL=google/gemini-2.5-pro\n")
            env_file.write("LLM_BASE_URL=https://openrouter.ai/api/v1\n")
            env_path = env_file.name

        try:
            with patch.dict(os.environ, {}, clear=True):
                config = load_config(env_path)
        finally:
            os.unlink(env_path)

        self.assertEqual(config["default_model"], "google/gemini-2.5-pro")
        self.assertEqual(config["openrouter"]["api_key"], "generic-key")
        self.assertEqual(config["openrouter"]["base_url"], "https://openrouter.ai/api/v1")
        self.assertEqual(config["openai"]["api_key"], "generic-key")

    def test_provider_specific_openrouter_env_overrides_generic_env(self):
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as env_file:
            env_file.write("LLM_API_KEY=generic-key\n")
            env_file.write("LLM_BASE_URL=https://generic.example/v1\n")
            env_file.write("OPENROUTER_API_KEY=openrouter-key\n")
            env_file.write("OPENROUTER_BASE_URL=https://openrouter.example/v1\n")
            env_path = env_file.name

        try:
            with patch.dict(os.environ, {}, clear=True):
                config = load_config(env_path)
        finally:
            os.unlink(env_path)

        self.assertEqual(config["openrouter"]["api_key"], "openrouter-key")
        self.assertEqual(config["openrouter"]["base_url"], "https://openrouter.example/v1")


if __name__ == "__main__":
    unittest.main()
