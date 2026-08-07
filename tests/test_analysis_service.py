import unittest

from backend.app.services.analysis_service import AnalysisService
from backend.app.services.llm_provider import LLMProvider


class AnalysisServicePromptTests(unittest.TestCase):
    def test_build_prompt_requests_deep_learning_explanation(self):
        service = AnalysisService(LLMProvider())
        prompt = service.build_prompt("Some article content", ["AI", "LLM"])

        self.assertIn("deep understanding", prompt.lower())
        self.assertIn("deep understanding", prompt.lower())
        self.assertIn("trade-offs", prompt.lower())
        self.assertIn("follow-up", prompt.lower())


if __name__ == "__main__":
    unittest.main()
