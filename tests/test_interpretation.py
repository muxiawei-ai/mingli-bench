import unittest
import json

from mingli_bench.chart_api import build_bazi_chart
from mingli_bench.interpretation import (
    INTERPRETATION_SCHEMA_VERSION,
    build_local_interpretation,
    interpretation_prompt_contract,
    parse_interpretation_response,
)
from mingli_bench.intent import parse_question_intent
from mingli_bench.report import build_chart_report


class InterpretationContractTests(unittest.TestCase):
    def setUp(self):
        chart = build_bazi_chart(
            {
                "calendar_type": "solar",
                "year": 1978,
                "month": 4,
                "day": 5,
                "hour": 18,
                "location": "台湾",
            }
        )
        self.report = build_chart_report(chart, "分析事业")

    def test_prompt_contract_mentions_schema(self):
        contract = interpretation_prompt_contract()
        self.assertIn(INTERPRETATION_SCHEMA_VERSION, contract)
        self.assertIn("sections", contract)
        self.assertIn("answer_choice", contract)
        self.assertIn("option_scores", contract)
        self.assertIn("问事卦象参考", contract)

    def test_build_local_interpretation(self):
        intent = parse_question_intent("分析事业")
        interpretation = build_local_interpretation(self.report, intent)
        self.assertEqual(interpretation.mode, "local")
        self.assertFalse(interpretation.parsed_from_response)
        self.assertEqual(interpretation.schema_version, INTERPRETATION_SCHEMA_VERSION)
        self.assertGreaterEqual(len(interpretation.sections), 4)
        self.assertIn("本地模式", interpretation.overview)
        self.assertIn("事业问题路由", interpretation.to_markdown())

    def test_build_local_interpretation_separates_question_hexagram(self):
        chart = build_bazi_chart(
            {
                "calendar_type": "solar",
                "year": 1978,
                "month": 4,
                "day": 5,
                "hour": 18,
                "location": "台湾",
            }
        )
        report = build_chart_report(
            chart,
            "分析事业",
            hexagram_time_source="specified_time",
            hexagram_time="2026-06-05T20:52",
        )
        interpretation = build_local_interpretation(report, parse_question_intent("分析事业"))
        titles = [section.title for section in interpretation.sections]

        self.assertIn("本命卦象参考", titles)
        self.assertIn("问事卦象参考", titles)
        self.assertIn("指定时间起卦", interpretation.to_markdown())
        self.assertIn("question_hexagram.input_datetime", interpretation.to_markdown())

    def test_parse_json_interpretation_response(self):
        interpretation = parse_interpretation_response(
            """
```json
{
  "schema_version": "mingli_interpretation.v1",
  "overview": "结构化解读",
  "answer_choice": "B",
  "answer_confidence": 0.72,
  "option_scores": {
    "A": {"score": 0.2, "rationale": "证据弱"},
    "B": {"score": 0.72, "rationale": "证据较强"}
  },
  "sections": [
    {"title": "事业", "summary": "稳健输出", "evidence": ["x"], "caveats": []}
  ],
  "follow_up_questions": ["是否看近期？"],
  "caveats": ["审慎"]
}
```
""",
            self.report,
        )
        self.assertEqual(interpretation.mode, "llm_json")
        self.assertTrue(interpretation.parsed_from_response)
        self.assertEqual(interpretation.sections[0].title, "事业")
        self.assertEqual(interpretation.answer_choice, "B")
        self.assertEqual(interpretation.answer_confidence, 0.72)
        self.assertEqual(interpretation.option_scores["B"]["score"], 0.72)

    def test_parse_double_encoded_json_interpretation_response(self):
        payload = {
            "schema_version": "mingli_interpretation.v1",
            "overview": "双重编码也应解析",
            "sections": [
                {
                    "title": "排盘摘要",
                    "summary": "不是原始 JSON 字符串",
                    "evidence": ["pillars_text"],
                    "caveats": [],
                }
            ],
            "follow_up_questions": [],
            "caveats": [],
        }

        interpretation = parse_interpretation_response(
            json.dumps(json.dumps(payload, ensure_ascii=False), ensure_ascii=False),
            self.report,
        )

        self.assertEqual(interpretation.mode, "llm_json")
        self.assertTrue(interpretation.parsed_from_response)
        self.assertEqual(interpretation.overview, "双重编码也应解析")
        self.assertEqual(interpretation.sections[0].summary, "不是原始 JSON 字符串")

    def test_parse_json_with_literal_newlines_and_trailing_commas(self):
        response = """{
  "schema_version": "mingli_interpretation.v1",
  "overview": "第一行
第二行",
  "sections": [
    {
      "title": "追问分析",
      "summary": "第一段
第二段",
      "evidence": ["event_year=2026",],
      "caveats": [],
    },
  ],
  "follow_up_questions": [],
  "caveats": [],
}"""

        interpretation = parse_interpretation_response(response, self.report)

        self.assertEqual(interpretation.mode, "llm_json")
        self.assertTrue(interpretation.parsed_from_response)
        self.assertEqual(interpretation.overview, "第一行\n第二行")
        self.assertEqual(interpretation.sections[0].summary, "第一段\n第二段")

    def test_parse_plain_text_response_falls_back(self):
        interpretation = parse_interpretation_response("普通文本解读", self.report)
        self.assertEqual(interpretation.mode, "llm_text")
        self.assertFalse(interpretation.parsed_from_response)
        self.assertIn("llm_response_not_valid_json", interpretation.caveats)
        self.assertEqual(interpretation.raw_response, "普通文本解读")


if __name__ == "__main__":
    unittest.main()
