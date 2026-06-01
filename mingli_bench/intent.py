"""Rule-based user-question intent parsing for the MingLi agent."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Tuple


DEFAULT_DOMAIN = "综合"

DOMAIN_KEYWORDS: Dict[str, Tuple[str, ...]] = {
    "事业": (
        "事业",
        "工作",
        "职业",
        "职场",
        "升职",
        "创业",
        "生意",
        "公司",
        "老板",
        "同事",
        "项目",
        "offer",
        "career",
        "business",
        "job",
    ),
    "财运": (
        "财",
        "财运",
        "财富",
        "收入",
        "赚钱",
        "钱",
        "投资",
        "理财",
        "偏财",
        "正财",
        "financial",
        "money",
        "wealth",
    ),
    "婚姻": (
        "婚姻",
        "感情",
        "恋爱",
        "对象",
        "伴侣",
        "配偶",
        "结婚",
        "离婚",
        "桃花",
        "relationship",
        "love",
        "marriage",
    ),
    "健康": (
        "健康",
        "身体",
        "疾病",
        "病",
        "养生",
        "医疗",
        "压力",
        "睡眠",
        "health",
    ),
    "性格": (
        "性格",
        "人格",
        "脾气",
        "优势",
        "弱点",
        "天赋",
        "适合",
        "personality",
        "strength",
    ),
    "学业": (
        "学业",
        "学习",
        "考试",
        "升学",
        "读书",
        "专业",
        "留学",
        "study",
        "school",
        "exam",
    ),
    "家庭": (
        "家庭",
        "父母",
        "亲人",
        "家人",
        "子女",
        "孩子",
        "parent",
        "family",
        "children",
    ),
    "运势": (
        "运势",
        "流年",
        "大运",
        "今年",
        "明年",
        "未来",
        "阶段",
        "什么时候",
        "时间",
        "timing",
        "future",
    ),
}

DOMAIN_SECTION_HINTS: Dict[str, Tuple[str, ...]] = {
    "事业": ("排盘摘要", "事业倾向", "行动建议"),
    "财运": ("排盘摘要", "财务倾向", "风险提示"),
    "婚姻": ("排盘摘要", "关系倾向", "沟通建议"),
    "健康": ("排盘摘要", "健康关注", "非医疗提示"),
    "性格": ("排盘摘要", "性格结构", "优势与盲点"),
    "学业": ("排盘摘要", "学习倾向", "规划建议"),
    "家庭": ("排盘摘要", "家庭关系", "边界与沟通"),
    "运势": ("排盘摘要", "阶段观察", "关键追问"),
    DEFAULT_DOMAIN: ("排盘摘要", "综合观察", "建议追问"),
}


@dataclass(frozen=True)
class QuestionIntent:
    """Structured intent parsed from a user question."""

    question: str
    primary_domain: str
    domains: List[str]
    confidence: float
    matched_keywords: Dict[str, List[str]]
    section_hints: List[str]
    needs_clarification: bool

    def as_dict(self) -> Dict[str, Any]:
        return {
            "question": self.question,
            "primary_domain": self.primary_domain,
            "domains": self.domains,
            "confidence": self.confidence,
            "matched_keywords": self.matched_keywords,
            "section_hints": self.section_hints,
            "needs_clarification": self.needs_clarification,
        }


def parse_question_intent(question: str) -> QuestionIntent:
    """Parse a user question into coarse MingLi analysis domains."""

    normalized = question.strip().lower()
    matched: Dict[str, List[str]] = {}
    for domain, keywords in DOMAIN_KEYWORDS.items():
        hits = _matched_keywords(normalized, keywords)
        if hits:
            matched[domain] = hits

    ranked = sorted(
        matched,
        key=lambda domain: (-len(matched[domain]), domain),
    )
    if ranked:
        primary_domain = ranked[0]
        domains = ranked
        confidence = _confidence_from_matches(matched)
    else:
        primary_domain = DEFAULT_DOMAIN
        domains = [DEFAULT_DOMAIN]
        confidence = 0.2 if normalized else 0.0

    needs_clarification = primary_domain == DEFAULT_DOMAIN or len(domains) > 3
    return QuestionIntent(
        question=question,
        primary_domain=primary_domain,
        domains=domains,
        confidence=confidence,
        matched_keywords=matched,
        section_hints=list(DOMAIN_SECTION_HINTS.get(primary_domain, DOMAIN_SECTION_HINTS[DEFAULT_DOMAIN])),
        needs_clarification=needs_clarification,
    )


def _matched_keywords(text: str, keywords: Iterable[str]) -> List[str]:
    return [keyword for keyword in keywords if keyword.lower() in text]


def _confidence_from_matches(matched: Dict[str, List[str]]) -> float:
    total_hits = sum(len(hits) for hits in matched.values())
    domain_bonus = min(len(matched), 3) * 0.08
    confidence = 0.42 + min(total_hits, 5) * 0.1 + domain_bonus
    return min(round(confidence, 2), 0.95)


__all__ = [
    "DEFAULT_DOMAIN",
    "DOMAIN_KEYWORDS",
    "QuestionIntent",
    "parse_question_intent",
]
