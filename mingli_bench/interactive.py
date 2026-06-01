"""Interactive command helpers for the local MingLi agent."""

from __future__ import annotations

import json
from typing import Any, Callable, Dict, Iterable, Optional, Tuple

from .agent import AgentResult, DEFAULT_AGENT_QUESTION


InputFunc = Callable[[str], str]
OutputFunc = Callable[[str], None]


def _prompt(
    label: str,
    *,
    default: Optional[str] = None,
    input_func: InputFunc = input,
) -> str:
    suffix = f" [{default}]" if default not in (None, "") else ""
    value = input_func(f"{label}{suffix}: ").strip()
    if not value and default is not None:
        return default
    return value


def normalize_calendar_type(value: str) -> str:
    """Normalize user-facing calendar-type text."""

    normalized = value.strip().lower()
    if normalized in {"solar", "gregorian", "公历", "陽曆", "阳历", "西历", "新历"}:
        return "solar"
    if normalized in {"lunar", "农历", "農曆", "阴历", "陰曆", "旧历"}:
        return "lunar"
    raise ValueError("calendar type must be 公历/solar or 农历/lunar")


def parse_time_text(value: str) -> Tuple[Optional[int], int]:
    """Parse ``HH:MM`` or ``HH`` into hour/minute."""

    cleaned = value.strip()
    if not cleaned:
        return None, 0
    if ":" in cleaned:
        hour_text, minute_text = cleaned.split(":", 1)
    else:
        hour_text, minute_text = cleaned, "0"
    hour = int(hour_text)
    minute = int(minute_text)
    if not 0 <= hour <= 23:
        raise ValueError("hour must be in 0..23")
    if not 0 <= minute <= 59:
        raise ValueError("minute must be in 0..59")
    return hour, minute


def collect_agent_input(
    *,
    input_func: InputFunc = input,
    output_func: OutputFunc = print,
) -> Tuple[Dict[str, Any], str]:
    """Ask for birth data and return ``(chart_input, question)``."""

    output_func("MingLi local agent")
    output_func("输入出生信息；直接回车会使用方括号里的默认值。")

    calendar_type = normalize_calendar_type(
        _prompt("日期类型 公历/农历", default="公历", input_func=input_func)
    )
    payload: Dict[str, Any] = {"calendar_type": calendar_type}

    if calendar_type == "lunar":
        lunar_date = _prompt(
            "农历日期（如 一九八四年闰十月十七；留空则逐项输入）",
            input_func=input_func,
        )
        if lunar_date:
            payload["lunar_date"] = lunar_date
        else:
            payload["year"] = int(_prompt("农历年", input_func=input_func))
            payload["month"] = int(_prompt("农历月", input_func=input_func))
            payload["day"] = int(_prompt("农历日", input_func=input_func))
            leap = _prompt("是否闰月 y/N", default="N", input_func=input_func).lower()
            payload["is_leap_month"] = leap in {"y", "yes", "是", "true", "1"}
    else:
        payload["year"] = int(_prompt("公历年", input_func=input_func))
        payload["month"] = int(_prompt("公历月", input_func=input_func))
        payload["day"] = int(_prompt("公历日", input_func=input_func))

    hour, minute = parse_time_text(_prompt("出生时间 HH:MM（未知可留空）", input_func=input_func))
    payload["hour"] = hour
    payload["minute"] = minute

    gender = _prompt("性别（可留空）", input_func=input_func)
    if gender:
        payload["gender"] = gender
    country = _prompt("国家/地区（可留空）", input_func=input_func)
    if country:
        payload["country"] = country
    location = _prompt("出生地（如 台湾、香港、malaysia；可留空）", input_func=input_func)
    if location:
        payload["location"] = location

    question = _prompt("你想问什么", default=DEFAULT_AGENT_QUESTION, input_func=input_func)
    return payload, question


def prompt_for_model_choice(
    *,
    input_func: InputFunc = input,
) -> Optional[str]:
    """Ask whether to call an LLM and return the model name if requested."""

    wants_llm = _prompt("是否调用 LLM y/N", default="N", input_func=input_func).lower()
    if wants_llm not in {"y", "yes", "是", "true", "1"}:
        return None
    return _prompt(
        "模型名",
        default="google/gemini-2.5-pro",
        input_func=input_func,
    )


def format_agent_result(
    result: AgentResult,
    *,
    as_json: bool = False,
    show_prompt: bool = False,
) -> str:
    """Format an ``AgentResult`` for terminal output."""

    if as_json:
        return json.dumps(result.as_dict(), ensure_ascii=False, indent=2)

    lines = [
        "=== MingLi Agent Result ===",
        result.report.to_markdown(),
    ]
    if result.warnings:
        lines.append(f"Warnings: {', '.join(result.warnings)}")
    if result.response:
        lines.extend(["", "=== 结构化解读 ===", result.interpretation.to_markdown()])
    elif show_prompt:
        lines.extend(["", "=== Prompt Preview ===", result.prompt])
    return "\n".join(lines)


def inputs_from_iterable(values: Iterable[str]) -> InputFunc:
    """Create an input function for tests."""

    iterator = iter(values)

    def _inner(_prompt_text: str) -> str:
        return next(iterator)

    return _inner


__all__ = [
    "collect_agent_input",
    "format_agent_result",
    "inputs_from_iterable",
    "normalize_calendar_type",
    "parse_time_text",
    "prompt_for_model_choice",
]
