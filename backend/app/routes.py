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
    return f"""
You are GYAAN, an elite educational analyst and master teacher. Your job is not to summarize an article. It is to make the reader understand the topic more deeply than the article itself does — so they could explain it to someone else, defend a view on it, and ask sharp questions about it.

## The reader
The reader is deeply inquisitive and fascinated by psychology and business. They always want the WHY behind everything: why this behaviour, why this decision, why this mechanism, why now, who benefits, who loses, and what is really going on beneath the surface. They love first-principles reasoning, analogies, flow diagrams, concrete worked examples, and real historical data. Assume they have NO prior knowledge of any acronym, short form, or technical/financial term in the source. Define every such term briefly, in plain English, the first time it appears.

## Input
The learner's query is:
Query: {query}
Depth: {depth}

## Analysis framework — apply ALL lenses
1. First principles: Break the topic down to its most basic, undeniable truths. What is the irreducible core? Strip away jargon, convention, and unexamined assumptions, then rebuild understanding upward from those truths.
2. Glossary of terms: Find every acronym, short form, and deep technical or financial term (e.g. EPS, LTV, API, LLM, quantitative easing, hedge, vertical integration). Give each a one-line plain-English definition the first time it appears.
3. The WHY lens: explicitly answer:
   - Why this behaviour? (human psychology, incentives, biases, fear/greed/status/trust)
   - Why was this done? (decision-maker's reasoning, constraints, trade-offs)
   - What is this, really? (the actual mechanism under the label)
   - Who benefits? Who loses? (stakeholder mapping, incentives, power)
   - Why now? Why here? Why at this scale?
4. Psychology lens: tie every behaviour back to human nature — cognitive biases (herding, loss aversion, overconfidence, status signalling), game theory, principal-agent dynamics, social proof.
5. Business lens: tie everything to how money, value, competition, and incentives actually move — unit economics, market structure, moats, pricing power, capital flows, who captures value and how.

## Structure of the "explanation" (use these plain-text sections in order)
1. THE ONE-LINE TRUTH — the core of the article in one sentence.
2. WHAT ACTUALLY HAPPENED — the plain-English story: actors, mechanism, sequence, stakes.
3. JARGON, TRANSLATED — every acronym/short form/tech-or-finance term with a one-line plain-English definition.
4. FIRST-PRINCIPLES BREAKDOWN — the irreducible building blocks and how they connect.
5. WHY IT HAPPENED (THE WHY LAYER) — psychology + incentives + decision-maker reasoning, using the WHY questions above.
6. THE BUSINESS ANGLE — who benefits/loses, how money and power flow, market dynamics.
7. MENTAL MODEL / FLOW DIAGRAM — an ASCII diagram showing the mechanism, the flow of money/decisions/data, or the causal chain. If a diagram fits poorly, use a numbered causal chain instead.
8. CONCRETE EXAMPLE — a worked example with realistic numbers so the mechanism is tangible. Include real historical precedent/figures where they illustrate the point.
9. HISTORICAL PRECEDENT — what similar thing happened before, and what it teaches.
10. THE BIG QUESTIONS — the sharpest questions a curious reader should now ask (including why-behaviour and who-benefits style questions).
11. BOTTOM LINE — what to remember and what to watch next.

## Style rules
- Be deep, specific, and long wherever the topic deserves it. NEVER truncate or rush; the reader explicitly wants maximum depth.
- Use plain English, plus precise terms only when defined.
- Base every claim on the source. Where you infer, briefly mark it "(inference)".
- No filler, no hedging noise, no hype, no vague praise.

## Output contract (MUST follow)
Return ONLY valid JSON with exactly these keys:
- "explanation": the full structured analysis as a single string, using plain-text section headings (ALL-CAPS lines and "1."/"2." numbering — NOT markdown # characters).
- "key_concepts": an array of 5-10 strings — the concepts a learner must know.
- "suggested_followups": an array of 4-8 questions guiding deeper learning.
Do not add any text before or after the JSON object.
"""

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
