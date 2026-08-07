import json
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from .models import Article

SAMPLE_ARTICLES = [
    {
        "id": "insight-01",
        "title": "Open-source LLMs unlock faster experimentation for AI research",
        "snippet": "A new wave of community-driven models is making advanced AI research more accessible.",
        "content": "Open-source large language models are accelerating research by reducing costs, enabling customization, and empowering developers to experiment with new architectures without vendor lock-in.",
        "source": "Engineering Blog",
        "url": "https://example.com/opensource-llm-research",
        "published_at": datetime(2026, 6, 30, 8, 0),
        "importance_score": 0.98,
        "is_curated": True,
        "summary": "Community-built LLMs are lowering the barrier to research and speeding up innovation.",
        "plain_english": "These models are open for everyone to use and modify, which means more people can try new AI ideas quickly.",
        "concepts": "LLMs,Open-source,Experimentation,Model fine-tuning,Community research"
    },
    {
        "id": "insight-02",
        "title": "Why Retrieval-Augmented Generation is the future of enterprise knowledge work",
        "snippet": "RAG combines retrieval with generation to make AI answers grounded and up to date.",
        "content": "Retrieval-Augmented Generation improves AI outputs by pulling in real documents and data during generation, helping teams keep answers accurate and context-rich.",
        "source": "Tech News",
        "url": "https://example.com/rag-enterprise-future",
        "published_at": datetime(2026, 6, 30, 9, 15),
        "importance_score": 0.94,
        "is_curated": True,
        "summary": "RAG is becoming essential for companies that need AI to answer questions using real business data.",
        "plain_english": "Instead of guessing, the AI looks up information from your documents first, then answers more reliably.",
        "concepts": "RAG,Retrieval,Vector search,Knowledge grounding,Enterprise AI"
    },
    {
        "id": "insight-03",
        "title": "Startup ecosystem shifts toward developer-first fintech products",
        "snippet": "New fintech startups are building tools that let engineers build financial products faster.",
        "content": "A rising wave of developer-first finance platforms gives engineering teams APIs and composable building blocks to create banking experiences without deep financial domain knowledge.",
        "source": "Startup Digest",
        "url": "https://example.com/dev-first-fintech",
        "published_at": datetime(2026, 6, 30, 10, 45),
        "importance_score": 0.91,
        "is_curated": True,
        "summary": "Fintech is moving from consumer apps to programmable APIs for builders.",
        "plain_english": "Rather than building payment systems from scratch, engineers can use ready-made tools to add finance features quickly.",
        "concepts": "Fintech,APIs,Embedded finance,Developer platforms,Composability"
    },
    {
        "id": "insight-04",
        "title": "New research shows multimodal AI is improving reasoning across vision and text",
        "snippet": "The latest multimodal systems are better at connecting images, video, and words to solve complex tasks.",
        "content": "Researchers are combining visual and language models to build systems that can understand charts, diagrams, and real-world scenes while reasoning about them in natural language.",
        "source": "Research Blog",
        "url": "https://example.com/multimodal-reasoning",
        "published_at": datetime(2026, 6, 30, 12, 0),
        "importance_score": 0.93,
        "is_curated": True,
        "summary": "Multimodal AI is becoming stronger at reasoning by linking visual signals with text.",
        "plain_english": "AI is getting better at understanding pictures and words together, so it can explain what it sees and why it matters.",
        "concepts": "Multimodal AI,Vision-language,Reasoning,Embeddings,Transformers"
    },
    {
        "id": "insight-05",
        "title": "Why learning prerequisite concepts is the most reliable path to mastery",
        "snippet": "Strong understanding comes from clear foundations, not memorizing surface details.",
        "content": "Mastery requires identifying the smallest building blocks of a topic, learning them deeply, and connecting them into a coherent mental model.",
        "source": "Learning Science",
        "url": "https://example.com/prerequisite-learning",
        "published_at": datetime(2026, 6, 30, 13, 30),
        "importance_score": 0.89,
        "is_curated": True,
        "summary": "The best learning path is built on prerequisites and recursive understanding.",
        "plain_english": "To really understand something, start with the basics and make sure the foundations are strong.",
        "concepts": "Learning science,Prerequisites,Concept mapping,Deep understanding,First principles"
    }
]

async def list_daily_insights(session: AsyncSession) -> list[Article]:
    result = await session.execute(
        select(Article)
        .where(Article.analysis_ready.is_(True))
        .order_by(Article.importance_score.desc(), Article.is_curated.desc(), Article.published_at.desc())
        .limit(10)
    )
    return result.scalars().all()

async def get_article_by_id(session: AsyncSession, article_id: str) -> Article | None:
    result = await session.execute(select(Article).where(Article.id == article_id))
    return result.scalar_one_or_none()

async def ensure_seed_data(session: AsyncSession) -> None:
    count_result = await session.execute(select(func.count(Article.id)))
    article_count = count_result.scalar_one()
    if article_count > 0:
        return

    for record in SAMPLE_ARTICLES:
        article = Article(
            id=record['id'],
            title=record['title'],
            content=record['content'],
            source=record['source'],
            url=record['url'],
            published_at=record['published_at'],
            importance_score=record['importance_score'],
            is_curated=record['is_curated'],
            summary=record['summary'],
            plain_english=record['plain_english'],
            concepts=record['concepts'],
            analysis_payload=json.dumps({
                'one_sentence_summary': record['summary'],
                'plain_english': record['plain_english'],
                'what_happened': 'A concise preview of the article is already available for the app.',
                'why_it_matters': 'This seeded analysis shows how the detail experience will look.',
                'historical_context': 'The article context is prepared for rapid onboarding.',
                'career_relevance': 'This preview highlights how learners can connect the topic to practice.',
                'expert_perspectives': [
                    'Researcher: the core idea is grounded and explainable.',
                    'Engineer: the implementation story is clear and actionable.',
                    'Founder: the signal is strong for product and business relevance.',
                ],
                'contrarian_perspective': 'A balanced critique is included to encourage deeper thinking.',
                'future_predictions': ['The topic will continue to matter across product and engineering teams.'],
                'knowledge_graph': ['Core concept relationships are shown in the detail view.'],
                'follow_up_questions': ['What should I learn next about this field?'],
            }),
            analysis_ready=True,
        )
        session.add(article)
    await session.commit()

async def upsert_articles(session: AsyncSession, articles: list[dict]) -> int:
    created_or_updated = 0

    for record in articles:
        article = await session.get(Article, record["id"])
        if article is None:
            article = Article(
                id=record["id"],
                title=record["title"],
                content=record["content"],
                source=record["source"],
                url=record["url"],
                published_at=record.get("published_at"),
                importance_score=record.get("importance_score", 0.0),
                is_curated=record.get("is_curated", False),
                summary=record.get("summary", ""),
                plain_english=record.get("plain_english", ""),
                concepts=record.get("concepts", ""),
            )
            session.add(article)
            created_or_updated += 1
        else:
            updated = False
            for field in [
                "title",
                "content",
                "source",
                "url",
                "published_at",
                "importance_score",
                "is_curated",
                "summary",
                "plain_english",
                "concepts",
            ]:
                new_value = record.get(field)
                if new_value is not None and getattr(article, field) != new_value:
                    setattr(article, field, new_value)
                    updated = True
            if updated:
                created_or_updated += 1

    await session.commit()
    return created_or_updated
