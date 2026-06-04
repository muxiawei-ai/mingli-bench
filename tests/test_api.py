import json
import threading
import unittest
import urllib.request

from mingli_bench.api import agent_response, chart_response, create_server


class LocalApiTests(unittest.TestCase):
    def test_chart_response(self):
        response = chart_response(
            {
                "calendar_type": "solar",
                "year": 1978,
                "month": 4,
                "day": 5,
                "hour": 18,
                "location": "台湾",
            }
        )
        self.assertEqual(response["pillars_text"], "戊午 丙辰 丁酉 己酉")
        self.assertEqual(response["timezone"]["timezone"], "Asia/Taipei")

    def test_agent_response_accepts_wrapped_chart_input(self):
        response = agent_response(
            {
                "chart_input": {
                    "calendar_type": "solar",
                    "year": 1978,
                    "month": 4,
                    "day": 5,
                    "hour": 18,
                    "location": "台湾",
                },
                "question": "分析事业",
            }
        )
        self.assertEqual(response["report"]["summary"]["pillars_text"], "戊午 丙辰 丁酉 己酉")
        self.assertEqual(response["report"]["hexagram"]["primary"]["name"], "临卦")
        self.assertEqual(response["report"]["hexagram"]["changed"]["name"], "复卦")
        self.assertEqual(response["report"]["hexagram"]["moving_line_name"], "九二")
        self.assertEqual(response["report"]["hexagram"]["moving_line_text"], "咸临，吉，无不利。")
        self.assertEqual(response["report"]["hexagram"]["moving_line_source"], "zhouyi_classic.v1")
        self.assertEqual(response["intent"]["primary_domain"], "事业")
        self.assertIn("llm_not_called", response["warnings"])
        trace = {stage["name"]: stage for stage in response["trace"]}
        self.assertEqual(trace["llm"]["status"], "skipped")
        self.assertEqual(response["interpretation"]["mode"], "local")

    def test_http_health_and_agent_endpoints(self):
        server = create_server("127.0.0.1", 0)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        host, port = server.server_address
        base_url = f"http://{host}:{port}"
        try:
            with urllib.request.urlopen(f"{base_url}/health", timeout=5) as response:
                health = json.loads(response.read().decode("utf-8"))
            self.assertEqual(health["status"], "ok")
            self.assertIn("/", health["endpoints"])

            with urllib.request.urlopen(f"{base_url}/", timeout=5) as response:
                html = response.read().decode("utf-8")
            self.assertIn("MingLi Agent", html)
            self.assertIn("agentForm", html)
            self.assertIn("demoButton", html)
            self.assertIn("buildDemoReportData", html)
            self.assertIn("加载示例", html)
            self.assertIn("followUpForm", html)
            self.assertIn("继续追问", html)
            self.assertIn("解读边界", html)
            self.assertIn("[hidden]", html)
            self.assertIn("history-item", html)
            self.assertIn("意图识别", html)
            self.assertIn("escapeControlCharsInJsonStrings", html)
            self.assertIn("模型返回了结构化内容", html)
            self.assertIn("报告导出", html)
            self.assertIn("copyMarkdownButton", html)
            self.assertIn("buildMarkdownReport", html)
            self.assertIn("downloadHtmlButton", html)
            self.assertIn("buildPrintableHtmlReport", html)
            self.assertIn("下载 HTML", html)
            self.assertIn("summary-card", html)
            self.assertIn("print-tip", html)
            self.assertIn("turn-number", html)
            self.assertIn("htmlSummaryCard", html)
            self.assertIn("hexagramPanel", html)
            self.assertIn("renderHexagramModule", html)
            self.assertIn("renderPrintableHexagramSection", html)
            self.assertIn("hex-print-module", html)
            self.assertIn("井卦", html)
            self.assertIn("六爻详释", html)
            self.assertIn("当前解读", html)
            self.assertIn("追问与历史", html)
            self.assertIn("debugPanel", html)
            self.assertIn("调试信息（原始 JSON）", html)
            self.assertIn("formatModeLabel", html)
            self.assertNotIn("`置信度：${intent.confidence", html)

            body = json.dumps(
                {
                    "chart_input": {
                        "calendar_type": "solar",
                        "year": 1978,
                        "month": 4,
                        "day": 5,
                        "hour": 18,
                        "location": "台湾",
                    },
                    "question": "分析事业",
                }
            ).encode("utf-8")
            request = urllib.request.Request(
                f"{base_url}/agent",
                data=body,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(request, timeout=5) as response:
                agent = json.loads(response.read().decode("utf-8"))
            self.assertEqual(agent["chart"]["pillars_text"], "戊午 丙辰 丁酉 己酉")
            self.assertEqual(agent["report"]["question"], "分析事业")
            self.assertEqual(agent["trace"][1]["name"], "intent")
            self.assertEqual(agent["trace"][2]["name"], "chart")
            self.assertIn("interpretation", agent)
        finally:
            server.shutdown()
            thread.join(timeout=5)
            server.server_close()


if __name__ == "__main__":
    unittest.main()
