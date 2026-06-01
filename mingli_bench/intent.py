"""Rule-based user-question intent parsing for the MingLi agent."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Tuple


DEFAULT_DOMAIN = "综合"

DOMAIN_KEYWORDS: Dict[str, Tuple[str, ...]] = {
    "事业": (
        "事业",
        "工作",
        "工作状况",
        "职业",
        "职业状况",
        "职场",
        "升职",
        "创业",
        "生意",
        "公司",
        "老板",
        "同事",
        "项目",
        "行业",
        "现职",
        "管理层",
        "打工",
        "受薪",
        "设计师",
        "设计衣服",
        "出名",
        "从事",
        "從事",
        "教师",
        "主管",
        "经纪",
        "会计",
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
        "横财",
        "横发",
        "六合彩",
        "房产",
        "买房",
        "公寓",
        "身家",
        "负债",
        "欠债",
        "破产",
        "融资",
        "产业",
        "积蓄",
        "财政",
        "资产",
        "存款",
        "入不敷出",
        "小康",
        "千万",
        "亿万",
        "financial",
        "money",
        "wealth",
    ),
    "婚姻": (
        "婚姻",
        "感情",
        "恋爱",
        "爱情",
        "对象",
        "伴侣",
        "配偶",
        "结婚",
        "結婚",
        "离婚",
        "未婚",
        "已婚",
        "独身",
        "婚恋",
        "桃花",
        "签字结婚",
        "relationship",
        "love",
        "marriage",
    ),
    "健康": (
        "健康",
        "身体",
        "疾病",
        "病",
        "生病",
        "养生",
        "医疗",
        "压力",
        "睡眠",
        "抑郁",
        "痴",
        "交通意外",
        "意外",
        "撞车",
        "车祸",
        "食药",
        "药",
        "遗传病",
        "堕胎",
        "流产",
        "病逝",
        "病亡",
        "住院",
        "手术",
        "器官",
        "心脏",
        "脑部",
        "双腿",
        "手肘",
        "癌",
        "癌症",
        "乳癌",
        "硬块",
        "开刀",
        "骨折",
        "受伤",
        "难产",
        "残疾",
        "身体不好",
        "不能生育",
        "health",
    ),
    "性格": (
        "性格",
        "个性",
        "人格",
        "脾气",
        "优势",
        "弱点",
        "天赋",
        "适合",
        "外貌",
        "样貌",
        "身材",
        "高挑",
        "瘦削",
        "肥胖",
        "矮小",
        "高瘦",
        "高大",
        "魁梧",
        "皮肤",
        "五官",
        "脸",
        "薄唇",
        "浓眉",
        "娇小",
        "健壮",
        "瘦长",
        "外表",
        "爱好",
        "装修风格",
        "自私",
        "慷慨",
        "内向",
        "外向",
        "情绪化",
        "personality",
        "strength",
    ),
    "学业": (
        "学业",
        "学习",
        "学历",
        "教育程度",
        "考试",
        "升学",
        "读书",
        "专业",
        "科系",
        "留学",
        "大学",
        "硕士",
        "研究生",
        "博士",
        "高中",
        "高职",
        "专科",
        "小学",
        "中学",
        "毕业",
        "文盲",
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
        "女儿",
        "男孩",
        "男婴",
        "女婴",
        "婴",
        "双胞胎",
        "子息",
        "子嗣",
        "生产",
        "怀孕",
        "得子",
        "育有",
        "没有子女",
        "父亲",
        "母亲",
        "父亲或母亲",
        "祖上",
        "祖母",
        "婆婆",
        "家里",
        "家境",
        "家庭背景",
        "父母离异",
        "父母离婚",
        "外婆",
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
        "岁运",
        "搬迁",
        "牢狱",
        "法庭",
        "刑事",
        "被告",
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
    question_part = normalized.split("选项", 1)[0]
    matched: Dict[str, List[str]] = {}
    scores: Dict[str, int] = {}
    first_positions: Dict[str, int] = {}
    for domain, keywords in DOMAIN_KEYWORDS.items():
        hits = _matched_keywords(normalized, keywords)
        if hits:
            matched[domain] = hits
            question_hits = _matched_keywords(question_part, keywords)
            scores[domain] = len(hits) + (4 * len(question_hits))
            first_positions[domain] = min(
                normalized.find(keyword.lower())
                for keyword in hits
                if normalized.find(keyword.lower()) >= 0
            )

    ranked = sorted(
        matched,
        key=lambda domain: (-scores[domain], first_positions[domain], domain),
    )
    if ranked:
        primary_domain = ranked[0]
        domains = ranked
        confidence = _confidence_from_matches(matched, scores)
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


def _confidence_from_matches(
    matched: Dict[str, List[str]],
    scores: Optional[Dict[str, int]] = None,
) -> float:
    total_hits = sum(len(hits) for hits in matched.values())
    top_score = max((scores or {}).values(), default=0)
    domain_bonus = min(len(matched), 3) * 0.08
    confidence = 0.38 + min(total_hits, 5) * 0.08 + min(top_score, 8) * 0.03 + domain_bonus
    return min(round(confidence, 2), 0.95)


__all__ = [
    "DEFAULT_DOMAIN",
    "DOMAIN_KEYWORDS",
    "QuestionIntent",
    "parse_question_intent",
]
