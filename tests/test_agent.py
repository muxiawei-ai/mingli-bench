import unittest

from mingli_bench.agent import MingLiAgent, build_interpretation_prompt
from mingli_bench.chart_api import build_bazi_chart


class FakeModelClient:
    model_name = "fake-model"

    def generate(self, prompt: str) -> str:
        self.prompt = prompt
        return "这是一个测试解释。"


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


if __name__ == "__main__":
    unittest.main()
