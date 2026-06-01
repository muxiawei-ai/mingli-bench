import unittest

from mingli_bench.chart_api import build_bazi_chart
from mingli_bench.interpretation import (
    INTERPRETATION_SCHEMA_VERSION,
    build_local_interpretation,
    interpretation_prompt_contract,
    parse_interpretation_response,
)
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

    def test_build_local_interpretation(self):
        interpretation = build_local_interpretation(self.report)
        self.assertEqual(interpretation.mode, "local")
        self.assertFalse(interpretation.parsed_from_response)
        self.assertEqual(interpretation.schema_version, INTERPRETATION_SCHEMA_VERSION)
        self.assertGreaterEqual(len(interpretation.sections), 3)
        self.assertIn("本地模式", interpretation.overview)

    def test_parse_json_interpretation_response(self):
        interpretation = parse_interpretation_response(
            """
```json
{
  "schema_version": "mingli_interpretation.v1",
  "overview": "结构化解读",
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

    def test_parse_plain_text_response_falls_back(self):
        interpretation = parse_interpretation_response("普通文本解读", self.report)
        self.assertEqual(interpretation.mode, "llm_text")
        self.assertFalse(interpretation.parsed_from_response)
        self.assertIn("llm_response_not_valid_json", interpretation.caveats)
        self.assertEqual(interpretation.raw_response, "普通文本解读")


if __name__ == "__main__":
    unittest.main()
