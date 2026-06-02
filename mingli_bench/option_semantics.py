"""Text-derived semantic labels for benchmark answer options.

The labels in this module are deterministic reading aids. They describe option
text only and must not be treated as gold answers.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List


OPTION_PATTERN = re.compile(
    r"(?:(?<=^)|(?<=[\s\n\r:：项]))([A-Da-d])\s*[\.\u3001\uff0e:：)]\s*",
    flags=re.MULTILINE,
)

EVENT_TYPE_KEYWORDS = [
    (
        "traffic_accident",
        "交通意外",
        "健康",
        ["交通", "撞车", "车祸", "车", "驾驶", "事故", "人平安"],
    ),
    (
        "mental_health",
        "精神/心理健康",
        "健康",
        ["抑郁", "焦虑", "精神", "心理", "失眠", "痴", "痴呆", "疯", "神经"],
    ),
    (
        "health_illness",
        "身体疾病/健康事件",
        "健康",
        ["患", "病", "疾病", "住院", "手术", "受伤", "伤", "医疗", "身体"],
    ),
    (
        "relationship_marriage",
        "婚恋/伴侣",
        "婚姻",
        ["妻", "夫", "结婚", "离婚", "婚", "恋", "女友", "男友", "感情", "配偶", "认识现任", "单身"],
    ),
    (
        "wealth_gain",
        "财运/得财",
        "财运",
        ["财", "钱", "奖金", "横财", "发财", "得财", "投资", "股票", "得到一笔"],
    ),
    (
        "career_job",
        "事业/工作",
        "事业",
        ["工作", "事业", "升职", "职位", "公司", "创业", "失业", "职业", "老板"],
    ),
    (
        "education",
        "学业/考试",
        "学业",
        ["学", "考试", "大学", "读书", "毕业", "成绩", "入学"],
    ),
    (
        "family_children",
        "家庭/子女",
        "家庭",
        ["子女", "孩子", "儿子", "女儿", "怀孕", "生子", "父", "母", "家庭"],
    ),
    (
        "legal_conflict",
        "官非/法律冲突",
        "官非",
        ["官非", "诉讼", "法律", "法院", "警察", "坐牢", "牢狱", "纠纷"],
    ),
    (
        "travel_migration",
        "迁移/远行",
        "运势",
        ["回港", "移民", "搬", "迁", "出国", "旅行", "远行", "回国"],
    ),
    (
        "death_loss",
        "丧失/死亡",
        "灾劫",
        ["死亡", "去世", "过世", "丧", "离世"],
    ),
]


def extract_options(text: str) -> List[Dict[str, str]]:
    """Extract A-D option text from free-form question text."""

    matches = list(OPTION_PATTERN.finditer(text or ""))
    options = []
    seen = set()
    for index, match in enumerate(matches):
        letter = match.group(1).upper()
        if letter in seen:
            continue
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        option_text = _clean_option_text((text or "")[start:end])
        if option_text:
            seen.add(letter)
            options.append({"letter": letter, "text": option_text})
    return options


def analyze_option_semantics(text: str) -> List[Dict[str, Any]]:
    """Return text-derived event-type labels for A-D options."""

    diagnostics = []
    for option in extract_options(text):
        matched_keywords: Dict[str, List[str]] = {}
        event_types = []
        broad_domains = []
        labels = []
        for event_type, label, domain, keywords in EVENT_TYPE_KEYWORDS:
            matches = [keyword for keyword in keywords if keyword in option["text"]]
            if matches:
                matched_keywords[event_type] = matches
                event_types.append(event_type)
                labels.append(label)
                if domain not in broad_domains:
                    broad_domains.append(domain)
        if not event_types and re.fullmatch(r"(?:19|20)\d{2}", option["text"]):
            event_types.append("timing_year")
            labels.append("年份/时间点")
            broad_domains.append("运势")
        diagnostics.append(
            {
                "letter": option["letter"],
                "text": option["text"],
                "primary_event_type": event_types[0] if event_types else "unknown",
                "event_types": event_types,
                "labels": labels,
                "broad_domains": broad_domains,
                "matched_keywords": matched_keywords,
                "note": "option_semantics_are_text_derived_not_gold_labels",
            }
        )
    return diagnostics


def _clean_option_text(text: str) -> str:
    cleaned = re.sub(r"\s+", " ", text or "").strip()
    return cleaned.strip("；;，,。 ")


__all__ = [
    "EVENT_TYPE_KEYWORDS",
    "analyze_option_semantics",
    "extract_options",
]
