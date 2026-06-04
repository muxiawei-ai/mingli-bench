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
            self.assertIn("followUpForm", html)
            self.assertIn("继续追问", html)
            self.assertIn("解读边界", html)

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
