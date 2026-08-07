from pydantic import BaseModel
from typing import List, Optional

class ArticleSummary(BaseModel):
    id: str
    title: str
    snippet: str
    source: str
    published_at: Optional[str]
    importance_score: float

class DailyInsightResponse(BaseModel):
    date: str
    insights: List[ArticleSummary]

class ArticleDetailResponse(BaseModel):
    id: str
    title: str
    source: str
    url: str
    published_at: Optional[str]
    summary: str
    plain_english: str
    content: str
    concepts: List[str]
    what_happened: str
    why_it_matters: str
    historical_context: str
    career_relevance: str
    expert_perspectives: List[str]
    contrarian_perspective: str
    future_predictions: List[str]
    knowledge_graph: List[str]
    follow_up_questions: List[str]

class ExplainRequest(BaseModel):
    query: str
    depth: str = "student"

class ExplainResponse(BaseModel):
    query: str
    depth: str
    explanation: str
    key_concepts: List[str]
    suggested_followups: List[str]
