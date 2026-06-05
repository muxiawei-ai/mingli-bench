"""Local response cache wrapper for model clients."""

from __future__ import annotations

import hashlib
import json
import re
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from .base import ModelClient


DEFAULT_LLM_CACHE_DIR = ".cache/mingli_bench/llm"
LLM_CACHE_SCHEMA_VERSION = "mingli_llm_cache.v1"


class CachedModelClient(ModelClient):
    """Wrap a model client and cache exact prompt responses on disk."""

    def __init__(
        self,
        wrapped: ModelClient,
        *,
        cache_dir: str = DEFAULT_LLM_CACHE_DIR,
    ):
        self.wrapped = wrapped
        self.model_name = wrapped.model_name
        self.temperature = getattr(wrapped, "temperature", None)
        self.max_tokens = getattr(wrapped, "max_tokens", None)
        self.config = getattr(wrapped, "config", {})
        self.cache_dir = Path(cache_dir)
        self.last_cache_hit: Optional[bool] = None
        self.last_cache_key: Optional[str] = None
        self.last_cache_path: Optional[str] = None
        self._lock = threading.Lock()

    def generate(self, prompt: str, **kwargs: Any) -> str:
        """Return a cached model response, or call the wrapped client on miss."""

        key = self.cache_key(prompt, kwargs)
        path = self.cache_path(key)
        self.last_cache_key = key
        self.last_cache_path = str(path)
        with self._lock:
            cached = self._read_cache(path)
            if cached is not None:
                self.last_cache_hit = True
                return cached
            response = self.wrapped.generate(prompt, **kwargs)
            self._write_cache(path, prompt, response, kwargs)
            self.last_cache_hit = False
            return response

    def cache_key(self, prompt: str, kwargs: Optional[Dict[str, Any]] = None) -> str:
        payload = {
            "schema_version": LLM_CACHE_SCHEMA_VERSION,
            "client_class": self.wrapped.__class__.__name__,
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "safe_config": self._safe_config(),
            "kwargs": kwargs or {},
            "prompt": prompt,
        }
        encoded = json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def cache_path(self, key: str) -> Path:
        model_dir = _safe_path_part(self.model_name)
        return self.cache_dir / model_dir / f"{key}.json"

    def validate_api_key(self) -> bool:
        return self.wrapped.validate_api_key()

    def get_config(self) -> Dict[str, Any]:
        config = self.wrapped.get_config()
        config["cache_dir"] = str(self.cache_dir)
        return config

    def _safe_config(self) -> Dict[str, Any]:
        raw = self.wrapped.get_config()
        return {
            key: value
            for key, value in raw.items()
            if "key" not in str(key).lower() and "secret" not in str(key).lower()
        }

    def _read_cache(self, path: Path) -> Optional[str]:
        if not path.exists():
            return None
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
        if payload.get("schema_version") != LLM_CACHE_SCHEMA_VERSION:
            return None
        response = payload.get("response")
        return response if isinstance(response, str) else None

    def _write_cache(
        self,
        path: Path,
        prompt: str,
        response: str,
        kwargs: Dict[str, Any],
    ) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema_version": LLM_CACHE_SCHEMA_VERSION,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "model_name": self.model_name,
            "client_class": self.wrapped.__class__.__name__,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "kwargs": kwargs,
            "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
            "prompt_chars": len(prompt),
            "response": response,
        }
        temp_path = path.with_suffix(".tmp")
        temp_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        temp_path.replace(path)


def maybe_wrap_cached_model_client(
    model_client: Optional[ModelClient],
    *,
    cache_dir: str = DEFAULT_LLM_CACHE_DIR,
    enabled: bool = True,
) -> Optional[ModelClient]:
    """Return a cached wrapper unless caching is disabled or no client exists."""

    if model_client is None or not enabled or isinstance(model_client, CachedModelClient):
        return model_client
    return CachedModelClient(model_client, cache_dir=cache_dir)


def _safe_path_part(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("._")
    return cleaned or "model"


__all__ = [
    "CachedModelClient",
    "DEFAULT_LLM_CACHE_DIR",
    "LLM_CACHE_SCHEMA_VERSION",
    "maybe_wrap_cached_model_client",
]
