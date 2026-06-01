"""Helpers for normalizing OpenAI-compatible chat responses."""

from __future__ import annotations

from typing import Any, List, Optional


def extract_chat_message_text(message: Any) -> str:
    """Extract text from common OpenAI-compatible message shapes."""

    for field in ("content", "reasoning", "reasoning_content", "refusal"):
        text = _content_to_text(_get_value(message, field))
        if text:
            return text
    raise ValueError("chat message did not include text content")


def describe_chat_response(response: Any) -> str:
    """Return a concise, key-only description for debugging empty responses."""

    choices = _get_value(response, "choices") or []
    if not choices:
        return "choices=empty"
    choice = choices[0]
    message = _get_value(choice, "message")
    finish_reason = _get_value(choice, "finish_reason")
    content = _get_value(message, "content")
    reasoning = _get_value(message, "reasoning")
    reasoning_details = _get_value(message, "reasoning_details")
    return (
        f"finish_reason={finish_reason!r}, "
        f"content_type={type(content).__name__}, "
        f"has_reasoning={bool(reasoning)}, "
        f"has_reasoning_details={bool(reasoning_details)}"
    )


def _content_to_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, list):
        parts: List[str] = []
        for item in value:
            item_text = _content_part_to_text(item)
            if item_text:
                parts.append(item_text)
        return "\n".join(parts).strip()
    return str(value).strip()


def _content_part_to_text(item: Any) -> str:
    if isinstance(item, str):
        return item.strip()
    for field in ("text", "content"):
        text = _get_value(item, field)
        if isinstance(text, str) and text.strip():
            return text.strip()
    return ""


def _get_value(value: Any, key: str) -> Optional[Any]:
    if value is None:
        return None
    if isinstance(value, dict):
        return value.get(key)
    return getattr(value, key, None)
