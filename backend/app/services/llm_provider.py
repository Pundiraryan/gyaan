import os
import json
from typing import Dict, Optional
import httpx

class LLMProvider:
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "openai")
        self.api_key = (
            os.getenv("LLM_API_KEY")
            or os.getenv("OPENROUTER_API_KEY")
            or os.getenv("OPENAI_API_KEY")
        )
        self.model = os.getenv("LLM_MODEL", "gpt-4o-mini")
        self.max_tokens = int(os.getenv("LLM_MAX_TOKENS", "1024"))
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
        self.openrouter_base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1").rstrip("/")

    def select_model(self, depth: str) -> str:
        if self.provider == "openrouter":
            mapping = {
                "beginner": "openai/gpt-4o-mini",
                "student": "openai/gpt-4o-mini",
                "engineer": "openai/gpt-4o-mini",
                "expert": "anthropic/claude-sonnet-4",
            }
            return mapping.get(depth, self.model)

        mapping = {
            "beginner": "gpt-3.5-turbo",
            "student": "gpt-3.5-turbo",
            "engineer": "gpt-4o-mini",
            "expert": "gpt-4o-mini",
        }
        return mapping.get(depth, self.model)

    async def generate(self, prompt: str, metadata: Optional[Dict] = None) -> str:
        if self.provider == "ollama":
            url = f"{self.ollama_base_url}/api/chat"
            headers = {"Content-Type": "application/json"}
            body = {
                "model": self.select_model(metadata.get("depth") if metadata else self.model),
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are GYAAN, an expert educational AI assistant. "
                            "Produce clear, structured learning content and return valid JSON when requested."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                "stream": False,
            }
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(url, json=body, headers=headers)
                response.raise_for_status()
                data = response.json()
                message = data.get("message", {})
                return message.get("content", "")

        if not self.api_key:
            return (
                "[LLM API key is not configured. Install a valid LLM_API_KEY, OPENROUTER_API_KEY, or OPENAI_API_KEY to use the AI explanation feature.]"
            )

        if self.provider in ("openai", "openrouter"):
            url = (
                f"{self.openrouter_base_url}/chat/completions"
                if self.provider == "openrouter"
                else "https://api.openai.com/v1/chat/completions"
            )
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            body = {
                "model": self.select_model(metadata.get("depth") if metadata else self.model),
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are GYAAN, an expert educational AI assistant. "
                            "Produce clear, structured learning content and return valid JSON when requested."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                "max_tokens": self.max_tokens,
                "temperature": 0.7,
            }
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(url, json=body, headers=headers)
                response.raise_for_status()
                data = response.json()
                choice = data.get("choices", [{}])[0]
                message = choice.get("message", {})
                return message.get("content", "")

        return (
            "[Unsupported LLM provider. Set LLM_PROVIDER=openai, openrouter, or ollama.]"
        )
