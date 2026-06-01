"""
Configuration management for Fortune Telling Benchmark.
"""

import os
from typing import Dict, Any, Optional

try:
    from dotenv import load_dotenv as _python_dotenv_load
except ImportError:  # pragma: no cover - exercised when optional deps are absent
    _python_dotenv_load = None

from .path_utils import find_file_in_hierarchy


def _load_env_file(path: str) -> None:
    """Load simple KEY=VALUE pairs from an env file.

    python-dotenv is used when installed. The small fallback keeps core utilities
    and CI usable without optional LLM dependencies.
    """

    if _python_dotenv_load is not None:
        _python_dotenv_load(path)
        return

    with open(path, "r", encoding="utf-8") as env_file:
        for raw_line in env_file:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


def load_config(env_file: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from environment variables and .env file.

    Simplified configuration loading:
    - OPENROUTER_API_KEY: Unified API key for all OpenRouter models
    - OPENROUTER_BASE_URL: OpenRouter base URL (default: https://openrouter.ai/api/v1)
    - {PROVIDER}_API_KEY: Native API keys (OPENAI_API_KEY, ANTHROPIC_API_KEY, etc.)
    - {PROVIDER}_BASE_URL: Optional base URLs for native APIs

    Args:
        env_file: Path to .env file (default: .env in project root)

    Returns:
        Configuration dictionary
    """
    # Load .env file
    if env_file:
        _load_env_file(env_file)
    else:
        # Try to find .env file
        env_path = find_file_in_hierarchy(".env")
        if env_path:
            _load_env_file(env_path)

    default_max_tokens = int(os.getenv("MAX_TOKENS", "8192"))
    default_temperature = float(os.getenv("TEMPERATURE", "0.0"))
    generic_api_key = os.getenv("LLM_API_KEY")
    generic_base_url = os.getenv("LLM_BASE_URL")
    generic_model = os.getenv("LLM_MODEL")

    # Build configuration
    config = {
        # General settings
        "max_workers": int(os.getenv("MAX_WORKERS", "5")),
        "timeout": int(os.getenv("TIMEOUT", "30")),
        "max_tokens": default_max_tokens,
        "temperature": default_temperature,
        "default_model": generic_model,

        # OpenRouter configuration
        "openrouter": {
            "api_key": os.getenv("OPENROUTER_API_KEY") or generic_api_key,
            "base_url": os.getenv("OPENROUTER_BASE_URL")
            or generic_base_url
            or "https://openrouter.ai/api/v1",
            "temperature": default_temperature,
            "max_tokens": default_max_tokens,
        },

        # Native OpenAI configuration
        "openai": {
            "api_key": os.getenv("OPENAI_API_KEY") or generic_api_key,
            "base_url": os.getenv("OPENAI_BASE_URL") or generic_base_url,
            "temperature": default_temperature,
            "max_tokens": default_max_tokens,
        },

        # Native Anthropic configuration
        "anthropic": {
            "api_key": os.getenv("CLAUDE_API_KEY") or os.getenv("ANTHROPIC_API_KEY"),
            "base_url": os.getenv("CLAUDE_BASE_URL") or os.getenv("ANTHROPIC_BASE_URL"),
            "temperature": default_temperature,
            "max_tokens": default_max_tokens,
        },

        # Native Google configuration
        "google": {
            "api_key": os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"),
            "base_url": os.getenv("GEMINI_BASE_URL") or os.getenv("GOOGLE_BASE_URL"),
            "temperature": default_temperature,
            "max_tokens": default_max_tokens,
        },

        # Native DeepSeek configuration
        "deepseek": {
            "api_key": os.getenv("DEEPSEEK_API_KEY"),
            "base_url": os.getenv("DEEPSEEK_BASE_URL"),
            "temperature": default_temperature,
            "max_tokens": default_max_tokens,
        },

        # Doubao configuration
        "doubao": {
            "api_key": os.getenv("DOUBAO_API_KEY"),
            "base_url": os.getenv("DOUBAO_BASE_URL"),
            "endpoint_id": os.getenv("DOUBAO_ENDPOINT_ID"),
            "temperature": default_temperature,
            "max_tokens": default_max_tokens,
        },
    }

    return config
