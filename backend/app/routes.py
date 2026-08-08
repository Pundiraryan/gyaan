import json
from datetime import datetime
from fastapi import APIRouter, HTTPException
from sqlalchemy import func, select
from .models import Article
from .schemas import (
    DailyInsightResponse,
    ExplainRequest,
    ExplainResponse,
    ArticleSummary,
    ArticleDetailResponse,
)
from .database import async_session
from .crud import list_daily_insights, get_article_by_id
from .services.analysis_service import AnalysisService
from .services.llm_provider import LLMProvider
from .services.news_scraper import scrape_latest_articles
from .services.scheduler import process_daily_digest

router = APIRouter()
llm_provider = LLMProvider()
analysis_service = AnalysisService(llm_provider)

def build_explain_prompt(query: str, depth: str) -> str:
    return (
        "You are GYAAN, an educational AI analyst. "
        "Answer the following request with a clear, expert-friendly explanation. "
        "Return valid JSON only, with keys: explanation, key_concepts, suggested_followups. "
        "Do not include any markdown formatting.\n\n"
        f"Query: {query}\n"
        f"Depth: {depth}\n\n"
        "Instructions:\n"
        "- Provide a concise layered explanation for the topic.\n"
        "- Include the most important concepts a learner should know.\n"
        "- Generate follow-up questions that guide deeper understanding.\n"
        "- Keep the answer in plain English and avoid vague filler.\n"
    )

@router.get("/daily-insights", response_model=DailyInsightResponse)
async def get_daily_insights():
    async with async_session() as session:
        insights = await list_daily_insights(session)
    return DailyInsightResponse(
        date=datetime.utcnow().date().isoformat(),
        insights=[
            ArticleSummary(
                id=insight.id,
                title=insight.title,
                snippet=insight.content[:120] if insight.content else "",
                source=insight.source,
                published_at=insight.published_at.isoformat() if insight.published_at else None,
                importance_score=insight.importance_score,
            )
            for insight in insights
        ],
    )

@router.post("/scrape")
async def scrape_articles():
    async with async_session() as session:
        count = await scrape_latest_articles(session)
    processed = await process_daily_digest(count)
    return {"scraped_articles": count, "processed_articles": processed}


@router.get("/daily-digest/status")
async def get_daily_digest_status():
    async with async_session() as session:
        result = await session.execute(select(func.count(Article.id)).where(Article.analysis_ready.is_(True)))
        analyzed_articles = result.scalar_one() or 0

    return {
        "digest_ready": analyzed_articles > 0,
        "analyzed_articles": int(analyzed_articles),
        "message": "Daily digest is ready to view in the app.",
    }


@router.post("/daily-digest/run")
async def run_daily_digest_now():
    processed = await process_daily_digest(0)
    return {"processed_articles": processed}


@router.get("/article/{article_id}", response_model=ArticleDetailResponse)
async def get_article(article_id: str):
    async with async_session() as session:
        article = await get_article_by_id(session, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")

    analysis = {}
    if article.analysis_payload:
        try:
            analysis = json.loads(article.analysis_payload)
        except json.JSONDecodeError:
            analysis = {}

    if not analysis:
        analysis = await analysis_service.generate_deep_analysis(
            article.content,
            [concept.strip() for concept in article.concepts.split(",") if concept.strip()],
        )
    analysis = analysis_service.normalize_analysis(analysis, article.content)

    if not article.analysis_payload and analysis:
        async with async_session() as session:
            db_article = await session.get(Article, article.id)
            if db_article is not None:
                db_article.analysis_payload = json.dumps(analysis)
                db_article.analysis_ready = True
                db_article.summary = analysis.get("one_sentence_summary", db_article.summary)
                db_article.plain_english = analysis.get("plain_english", db_article.plain_english)
                await session.commit()

    return ArticleDetailResponse(
        id=article.id,
        title=article.title,
        source=article.source,
        url=article.url,
        published_at=article.published_at.isoformat() if article.published_at else None,
        summary=analysis.get("one_sentence_summary", article.summary),
        plain_english=analysis.get("plain_english", article.plain_english),
        content=article.content,
        concepts=[concept.strip() for concept in article.concepts.split(",") if concept.strip()],
        what_happened=analysis.get("what_happened", "This section is reserved for deep analysis."),
        why_it_matters=analysis.get("why_it_matters", "This section is reserved for impact analysis."),
        historical_context=analysis.get("historical_context", "This section is reserved for historical timeline context."),
        career_relevance=analysis.get("career_relevance", "This section is reserved for career relevance."),
        expert_perspectives=analysis.get(
            "expert_perspectives",
            [
                "Researcher perspective not implemented yet.",
                "Engineer perspective not implemented yet.",
                "Founder perspective not implemented yet.",
            ],
        ),
        contrarian_perspective=analysis.get("contrarian_perspective", "This section is reserved for contrarian critique."),
        future_predictions=analysis.get(
            "future_predictions",
            [
                "Future prediction 1 not implemented yet.",
                "Future prediction 2 not implemented yet.",
            ],
        ),
        knowledge_graph=analysis.get("knowledge_graph", ["Knowledge graph node placeholder"]),
        follow_up_questions=analysis.get("follow_up_questions", ["What should I learn next about this topic?"]),
    )

@router.post("/explain", response_model=ExplainResponse)
async def explain_topic(request: ExplainRequest):
    prompt = build_explain_prompt(request.query, request.depth)
    try:
        raw_output = await llm_provider.generate(prompt, metadata={"depth": request.depth})
    except Exception as exc:
        raw_output = (
            f"LLM request failed: {exc}. "
            "Please try again later or configure an LLM provider."
        )

    try:
        parsed = json.loads(raw_output)
        return ExplainResponse(
            query=request.query,
            depth=request.depth,
            explanation=parsed.get("explanation", raw_output),
            key_concepts=parsed.get("key_concepts", []),
            suggested_followups=parsed.get("suggested_followups", []),
        )
    except json.JSONDecodeError:
        return ExplainResponse(
            query=request.query,
            depth=request.depth,
            explanation=raw_output,
            key_concepts=["Foundations", "Concepts", "Application"],
            suggested_followups=[
                "Why is this important?",
                "What are the core components?",
                "How do I learn this step-by-step?",
            ],
        )
