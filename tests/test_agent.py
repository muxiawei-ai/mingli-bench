import unittest

from mingli_bench.agent import MingLiAgent, build_interpretation_prompt
from mingli_bench.chart_api import build_bazi_chart


class FakeModelClient:
    model_name = "fake-model"

    def generate(self, prompt: str) -> str:
        self.prompt = prompt
        return "这是一个测试解释。"


class FakeJsonModelClient:
    model_name = "fake-json-model"

    def generate(self, prompt: str) -> str:
        self.prompt = prompt
        return """
{
  "schema_version": "mingli_interpretation.v1",
  "overview": "这是结构化 JSON 解读。",
  "sections": [
    {
      "title": "事业",
      "summary": "以结构化方式回应事业问题。",
      "evidence": ["day_master=丁"],
      "caveats": ["保持审慎"]
    }
  ],
  "follow_up_questions": ["是否关注近期变化？"],
  "caveats": ["不可视为确定事实"]
}
"""


class MingLiAgentTests(unittest.TestCase):
    def test_build_interpretation_prompt_uses_chart_json(self):
        chart = build_bazi_chart(
            {
                "calendar_type": "solar",
                "year": 1978,
                "month": 4,
                "day": 5,
                "hour": 18,
                "location": "台湾",
                "country": "中国",
            }
        )
        prompt = build_interpretation_prompt(chart, "分析事业")
        self.assertIn("分析事业", prompt)
        self.assertIn("戊午", prompt)
        self.assertIn("本地 report JSON", prompt)
        self.assertIn("JSON 输出契约", prompt)
        self.assertIn("mingli_interpretation.v1", prompt)
        self.assertIn("不要重新发明或猜测四柱", prompt)

    def test_agent_without_model_returns_prompt_only(self):
        result = MingLiAgent().run(
            {
                "calendar_type": "solar",
                "year": 1978,
                "month": 4,
                "day": 5,
                "hour": 18,
                "location": "台湾",
                "country": "中国",
            },
            question="分析性格",
        )
        self.assertIsNone(result.response)
        self.assertIsNone(result.model)
        self.assertIn("llm_not_called", result.warnings)
        self.assertEqual(result.chart.pillars.display(), "戊午 丙辰 丁酉 己酉")
        self.assertEqual(result.report.summary["pillars_text"], "戊午 丙辰 丁酉 己酉")
        self.assertIn("report", result.as_dict())
        self.assertEqual(
            [stage.name for stage in result.trace],
            ["input", "chart", "report", "prompt", "llm", "interpretation"],
        )
        self.assertEqual(result.trace[-2].status, "skipped")
        self.assertEqual(result.interpretation.mode, "local")
        self.assertIn("trace", result.as_dict())
        self.assertIn("interpretation", result.as_dict())

    def test_agent_with_model_returns_response(self):
        model = FakeModelClient()
        result = MingLiAgent(model).run(
            {
                "calendar_type": "solar",
                "year": 1978,
                "month": 4,
                "day": 5,
                "hour": 18,
                "location": "台湾",
                "country": "中国",
            }
        )
        self.assertEqual(result.response, "这是一个测试解释。")
        self.assertEqual(result.model, "fake-model")
        self.assertNotIn("llm_not_called", result.warnings)
        self.assertIn("本地 report JSON", model.prompt)
        self.assertEqual(result.trace[-2].status, "completed")
        self.assertEqual(result.trace[-2].data["model"], "fake-model")
        self.assertEqual(result.interpretation.mode, "llm_text")
        self.assertIn("llm_response_not_valid_json", result.interpretation.caveats)

    def test_agent_with_json_model_returns_structured_interpretation(self):
        model = FakeJsonModelClient()
        result = MingLiAgent(model).run(
            {
                "calendar_type": "solar",
                "year": 1978,
                "month": 4,
                "day": 5,
                "hour": 18,
                "location": "台湾",
                "country": "中国",
            },
            question="分析事业",
        )
        self.assertEqual(result.interpretation.mode, "llm_json")
        self.assertTrue(result.interpretation.parsed_from_response)
        self.assertEqual(result.interpretation.sections[0].title, "事业")
        self.assertIn("结构化 JSON 解读", result.interpretation.to_markdown())

    def test_agent_trace_contains_chart_and_prompt_metadata(self):
        result = MingLiAgent().run(
            {
                "calendar_type": "solar",
                "year": 1978,
                "month": 4,
                "day": 5,
                "hour": 18,
                "location": "台湾",
                "country": "中国",
            },
            question="分析事业",
        )
        trace = {stage.name: stage.as_dict() for stage in result.trace}
        self.assertEqual(trace["chart"]["data"]["pillars_text"], "戊午 丙辰 丁酉 己酉")
        self.assertGreater(trace["prompt"]["data"]["prompt_chars"], 1000)
        self.assertEqual(trace["llm"]["warnings"], ["llm_not_called"])
        self.assertEqual(trace["interpretation"]["data"]["mode"], "local")


if __name__ == "__main__":
    unittest.main()
