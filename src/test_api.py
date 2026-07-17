"""Functional smoke tests for Friday API Service."""
import os
import sys
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient

from friday import api as api_module
from friday.api import app


class FridayApiSmokeTests(unittest.TestCase):
    def setUp(self):
        api_module.state.pending_confirm.clear()
        api_module.state.events.clear()
        api_module.state.history = [{"role": "system", "content": "test system"}]

    def test_app_loads_and_status_returns_200(self):
        client = TestClient(app)
        response = client.get("/api/status")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["status"], "ok")
        self.assertEqual(body["service"], "friday-api")
        self.assertIn("confirm_required", body["event_types"])

    def test_chat_keeps_gated_tool_pending_until_confirmed(self):
        client = TestClient(app)
        llm_message = {
            "content": "ได้ค่ะ",
            "tool_calls": [
                {"function": {"name": "open_app", "arguments": {"name": "notepad"}}}
            ],
        }
        execute = Mock(return_value="เปิด notepad ให้แล้วค่ะ")

        with patch.object(api_module.core, "ask_ollama", return_value=llm_message), patch.dict(
            api_module.core.CONFIRM_GATED["open_app"], {"execute": execute}
        ):
            response = client.post("/api/chat", json={"message": "เปิด notepad"})
            self.assertEqual(response.status_code, 200)
            body = response.json()
            self.assertEqual(body["pending_confirmation"]["tool_name"], "open_app")
            execute.assert_not_called()

            confirmation_id = body["pending_confirmation"]["confirmation_id"]
            confirm_response = client.post(
                "/api/tool/confirm",
                json={"confirmation_id": confirmation_id, "confirm": True},
            )
            self.assertEqual(confirm_response.status_code, 200)
            self.assertTrue(confirm_response.json()["executed"])
            execute.assert_called_once_with("notepad")


if __name__ == "__main__":
    unittest.main()
