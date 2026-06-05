"""
Data schema definitions for Fortune Telling Benchmark.
"""

from typing import Any, Dict, List, Optional, TypedDict, Union
from dataclasses import dataclass


class OptionDict(TypedDict):
    """Option structure in question."""
    letter: str
    text: str


class BirthInfoDict(TypedDict):
    """Birth information structure."""
    raw: str
    gender: Optional[str]
    year: Optional[Union[int, str]]
    month: Optional[Union[int, str]]
    day: Optional[Union[int, str]]
    hour: Optional[Union[int, str]]
    minute: Optional[Union[int, str]]
    calendar_type: str
    country: Optional[str]
    location: Optional[str]


class QuestionDict(TypedDict):
    """Question structure in dataset."""
    id: str
    question_number: int
    benchmark_year: Optional[int]
    case_id: str
    birth_info: BirthInfoDict
    question: str
    options: List[OptionDict]
    answer: str
    category: str
    provider: Optional[str]


class DatasetDict(TypedDict):
    """Dataset structure."""
    benchmark_name: str
    version: str
    description: Optional[str]
    language: Optional[str]
    total_questions: int
    questions: List[QuestionDict]


@dataclass
class EvaluationResult:
    """Single evaluation result."""
    question_id: str
    category: str
    benchmark_year: Optional[int]
    question: str
    options: List[OptionDict]
    correct_answer: str
    predicted_answer: Optional[str]
    correct: bool
    response: Optional[str]
    response_time: float
    error: Optional[str] = None
    option_shuffle_info: Optional[Dict[str, Any]] = None
    prompt: Optional[str] = None



# Question categories
QUESTION_CATEGORIES = {
    '意外': ['发生何事', '交通意外', '意外'],
    '事业': ['事业', '工作', '升职', '生意'],
    '婚姻': ['结婚', '婚姻', '离异', '单身', '太太', '老公', '夫妻', '感情'],
    '学业': ['学历', '毕业', '升学', '留学', '大学', '考试', '学习', '成绩'],
    '财运': ['得财', '输了', '赚了', '负债', '存款', '月光族', '财富', '金钱', '投资'],
    '家庭': ['父母', '兄弟姐妹', '祖母', '孩子', '仔女', '子女', '家人', '家庭'],
    '性格': ['性格', '自私', '付出', '强势', '固执', '性情', '脾气', '性格'],
    '健康': ['健康', '疾病', '身体', '病痛', '医院', '手术', '健康', '生病', '过世', '逝世'],
    '综合': []  # Default category
}

# Valid answer options
VALID_OPTIONS = 'ABCDEFGH'

# Answer patterns for extraction (applied in priority order; match is uppercased after)
ANSWER_PATTERNS = [
    r'答案[：:]\s*([A-Za-z])',
    r'答案是[：:]?\s*([A-Za-z])',
    r'选择[：:]\s*([A-Za-z])',
    r'选[：:]?\s*([A-Za-z])',
    r'我选择\s*([A-Za-z])',
    r'应该选\s*([A-Za-z])',
    r'正确答案[是：:]\s*([A-Za-z])',
    r'^([A-Za-z])[\.、。]',
    r'^([A-Za-z])$',
    r'[。，]([A-Za-z])[。]?$',
]

# Answer markers in raw data
ANSWER_MARKERS = [
    '（正确答案）', '(正确答案)', 
    '【正确答案】', '[正确答案]',
    '（答案）', '(答案)',
    '（正确）', '(正确)',
    '※',  # Some questions use special marks
    '*'   # Some questions use asterisk
]
