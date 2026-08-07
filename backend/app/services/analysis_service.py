import json
from typing import Any, List

from .llm_provider import LLMProvider


class AnalysisService:
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider

    def build_prompt(self, content: str, concepts: List[str]) -> str:
        return (
            "You are GYAAN, an elite educational AI tutor and analyst. "
            "Your mission is to help a learner understand the article deeply, clearly, and practically. "
            "Think like a master teacher, not a summarizer. "
            "Return valid JSON only. Do not include markdown, headers, or commentary outside the JSON object.\n\n"
            "Article content:\n"
            f"{content}\n\n"
            "Concept tags:\n"
            f"{', '.join(concepts)}\n\n"
            "Instructions:\n"
            "- Write a one-sentence summary that captures the real core idea and why it matters.\n"
            "- Translate the article into plain English that a motivated learner can understand without losing precision.\n"
            "- Explain what happened with depth: the actors, mechanism, sequence, stakes, and important details.\n"
            "- Explain why it matters by connecting it to larger trends, consequences, systems, or real-world impact.\n"
            "- Provide historical context so the learner understands how this topic evolved and why it is relevant now.\n"
            "- Explain career relevance for students, engineers, researchers, founders, and product builders.\n"
            "- Offer expert perspectives from multiple angles such as researcher, engineer, founder, and critic.\n"
            "- Include a contrarian perspective that highlights trade-offs, risks, blind spots, and limitations.\n"
            "- Provide future predictions that are grounded, cautious, and evidence-oriented rather than hype-driven.\n"
            "- Create a concise knowledge graph with the key concepts and relationships that help the learner build a mental model.\n"
            "- Include follow-up questions that guide the learner toward deeper understanding.\n"
            "- Prioritize deep understanding, causal reasoning, practical takeaways, and learning value over surface-level summaries.\n"
            "- If information is incomplete, make the best evidence-based inference and clearly avoid overclaiming.\n\n"
            "Return keys: one_sentence_summary, plain_english, what_happened, why_it_matters, historical_context, career_relevance, expert_perspectives, contrarian_perspective, future_predictions, knowledge_graph, follow_up_questions.\n"
            "All scalar fields must be strings. expert_perspectives, future_predictions, knowledge_graph, and follow_up_questions must be arrays of strings."
        )

    def _stringify(self, value: Any, fallback: str) -> str:
        if value is None:
            return fallback
        if isinstance(value, str):
            return value
        if isinstance(value, list):
            return "\n".join(self._stringify(item, "") for item in value if item is not None).strip() or fallback
        if isinstance(value, dict):
            parts = []
            for key, item in value.items():
                text = self._stringify(item, "")
                parts.append(f"{key}: {text}" if text else str(key))
            return "\n".join(parts).strip() or fallback
        return str(value)

    def _string_list(self, value: Any, fallback: List[str]) -> List[str]:
        if value is None:
            return fallback
        if isinstance(value, list):
            items = [self._stringify(item, "").strip() for item in value]
            return [item for item in items if item] or fallback
        if isinstance(value, dict):
            items = []
            for key, item in value.items():
                text = self._stringify(item, "").strip()
                items.append(f"{key}: {text}" if text else str(key))
            return items or fallback
        if isinstance(value, str):
            return [value] if value.strip() else fallback
        return [str(value)]

    def normalize_analysis(self, analysis: dict, content: str) -> dict:
        return {
            "one_sentence_summary": self._stringify(
                analysis.get("one_sentence_summary"),
                content[:200],
            ),
            "plain_english": self._stringify(analysis.get("plain_english"), content),
            "what_happened": self._stringify(
                analysis.get("what_happened"),
                "The main event will be explained here.",
            ),
            "why_it_matters": self._stringify(
                analysis.get("why_it_matters"),
                "The impact and importance will be explained here.",
            ),
            "historical_context": self._stringify(
                analysis.get("historical_context"),
                "Historical context will be added here.",
            ),
            "career_relevance": self._stringify(
                analysis.get("career_relevance"),
                "Career implications will be included here.",
            ),
            "expert_perspectives": self._string_list(
                analysis.get("expert_perspectives"),
                [
                    "Researcher: perspective pending.",
                    "Engineer: perspective pending.",
                    "Founder: perspective pending.",
                ],
            ),
            "contrarian_perspective": self._stringify(
                analysis.get("contrarian_perspective"),
                "A contrarian perspective will be included here.",
            ),
            "future_predictions": self._string_list(
                analysis.get("future_predictions"),
                ["Future predictions will be included here."],
            ),
            "knowledge_graph": self._string_list(
                analysis.get("knowledge_graph"),
                ["Knowledge graph generation pending."],
            ),
            "follow_up_questions": self._string_list(
                analysis.get("follow_up_questions"),
                ["What should I learn next about this topic?"],
            ),
        }

    async def generate_deep_analysis(self, content: str, concepts: List[str]) -> dict:
        if not self.llm_provider.api_key:
            return {
                "one_sentence_summary": "This article will be analyzed by the AI once an API key is configured.",
                "plain_english": content,
                "what_happened": "A summary of the main event or development will appear here.",
                "why_it_matters": "The impact and importance will be explained when AI is available.",
                "historical_context": "Relevant history would be added here.",
                "career_relevance": "Career implications will be included when the model is enabled.",
                "expert_perspectives": [
                    "Researcher: not available without the model.",
                    "Engineer: not available without the model.",
                    "Founder: not available without the model.",
                ],
                "contrarian_perspective": "A contrarian perspective will be provided by the AI.",
                "future_predictions": ["Prediction 1 pending AI analysis."],
                "knowledge_graph": ["Pending AI knowledge graph generation."],
                "follow_up_questions": ["What should I learn next about this topic?"],
            }

        prompt = self.build_prompt(content, concepts)
        raw_output = await self.llm_provider.generate(prompt, metadata={"depth": "engineer"})

        try:
            parsed = json.loads(raw_output)
            return self.normalize_analysis(parsed, content)
        except json.JSONDecodeError:
            return self.normalize_analysis({
                "one_sentence_summary": content[:200],
                "plain_english": content,
                "what_happened": "The AI returned content that could not be parsed as JSON.",
                "why_it_matters": "This section is reserved for impact analysis.",
                "historical_context": "This section is reserved for historical timeline context.",
                "career_relevance": "This section is reserved for career relevance.",
                "expert_perspectives": [
                    "Researcher perspective not implemented yet.",
                    "Engineer perspective not implemented yet.",
                    "Founder perspective not implemented yet.",
                ],
                "contrarian_perspective": "This section is reserved for contrarian critique.",
                "future_predictions": [
                    "Future prediction 1 not implemented yet.",
                    "Future prediction 2 not implemented yet.",
                ],
                "knowledge_graph": ["Knowledge graph node placeholder"],
                "follow_up_questions": ["What should I learn next about this topic?"],
            }, content)
