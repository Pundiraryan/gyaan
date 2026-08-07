import asyncio
import os
import unittest
from unittest.mock import patch

from backend.app.services.llm_provider import LLMProvider


class LLMProviderTests(unittest.TestCase):
    def test_openrouter_provider_uses_openrouter_chat_endpoint(self):
        with patch.dict(
            os.environ,
            {
                "LLM_PROVIDER": "openrouter",
                "OPENROUTER_API_KEY": "test-openrouter-key",
                "LLM_MODEL": "openai/gpt-4o-mini",
            },
            clear=False,
        ):
            provider = LLMProvider()

            class FakeResponse:
                def raise_for_status(self):
                    return None

                def json(self):
                    return {"choices": [{"message": {"content": "openrouter-response"}}]}

            class FakeAsyncClient:
                async def __aenter__(self):
                    return self

                async def __aexit__(self, exc_type, exc, tb):
                    return False

                async def post(self, url, json, headers):
                    self.last_url = url
                    self.last_json = json
                    self.last_headers = headers
                    return FakeResponse()

            client = FakeAsyncClient()
            with patch("backend.app.services.llm_provider.httpx.AsyncClient", return_value=client):
                result = asyncio.run(provider.generate("Hello", {"depth": "engineer"}))

            self.assertEqual(result, "openrouter-response")
            self.assertEqual(client.last_url, "https://openrouter.ai/api/v1/chat/completions")
            self.assertEqual(client.last_headers["Authorization"], "Bearer test-openrouter-key")
            self.assertEqual(client.last_json["model"], "openai/gpt-4o-mini")

    def test_openrouter_expert_depth_uses_stronger_model(self):
        with patch.dict(
            os.environ,
            {
                "LLM_PROVIDER": "openrouter",
                "OPENROUTER_API_KEY": "test-openrouter-key",
            },
            clear=False,
        ):
            provider = LLMProvider()

        self.assertEqual(provider.select_model("expert"), "anthropic/claude-sonnet-4")

    def test_ollama_provider_uses_local_chat_endpoint(self):
        with patch.dict(
            os.environ,
            {
                "LLM_PROVIDER": "ollama",
                "OLLAMA_BASE_URL": "http://localhost:11434",
                "LLM_MODEL": "qwen2.5:3b",
            },
            clear=False,
        ):
            provider = LLMProvider()

            class FakeResponse:
                def raise_for_status(self):
                    return None

                def json(self):
                    return {"message": {"content": "local-response"}}

            class FakeAsyncClient:
                async def __aenter__(self):
                    return self

                async def __aexit__(self, exc_type, exc, tb):
                    return False

                async def post(self, url, json, headers):
                    self.last_url = url
                    self.last_json = json
                    self.last_headers = headers
                    return FakeResponse()

            client = FakeAsyncClient()
            with patch("backend.app.services.llm_provider.httpx.AsyncClient", return_value=client):
                result = asyncio.run(provider.generate("Hello"))

            self.assertEqual(result, "local-response")
            self.assertEqual(client.last_url, "http://localhost:11434/api/chat")
            self.assertEqual(client.last_json["model"], "qwen2.5:3b")


if __name__ == "__main__":
    unittest.main()
