import unittest
from types import SimpleNamespace

from mingli_bench.models.message_utils import (
    describe_chat_response,
    extract_chat_message_text,
)


class MessageUtilsTests(unittest.TestCase):
    def test_extracts_string_content(self):
        message = SimpleNamespace(content="  hello  ")
        self.assertEqual(extract_chat_message_text(message), "hello")

    def test_extracts_list_content_parts(self):
        message = SimpleNamespace(
            content=[
                {"type": "text", "text": "first"},
                SimpleNamespace(text="second"),
            ]
        )
        self.assertEqual(extract_chat_message_text(message), "first\nsecond")

    def test_falls_back_to_reasoning_when_content_is_empty(self):
        message = SimpleNamespace(content=None, reasoning="reasoned answer")
        self.assertEqual(extract_chat_message_text(message), "reasoned answer")

    def test_describes_empty_response_without_text(self):
        response = SimpleNamespace(
            choices=[
                SimpleNamespace(
                    finish_reason="length",
                    message=SimpleNamespace(content=None, reasoning_details=[{"x": 1}]),
                )
            ]
        )
        description = describe_chat_response(response)
        self.assertIn("finish_reason='length'", description)
        self.assertIn("content_type=NoneType", description)
        self.assertIn("has_reasoning_details=True", description)


if __name__ == "__main__":
    unittest.main()
