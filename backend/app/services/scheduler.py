import json
import os
from typing import Optional

import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select

from ..database import async_session
from ..models import Article
from .analysis_service import AnalysisService
from .llm_provider import LLMProvider
from .news_scraper import scrape_latest_articles

_scheduler: Optional[AsyncIOScheduler] = None
_DIGEST_LIMIT = int(os.getenv("DAILY_DIGEST_LIMIT", "5"))


async def send_digest_notification(processed_count: int) -> bool:
    webhook_url = os.getenv("DIGEST_WEBHOOK_URL")
    if not webhook_url:
        print("[scheduler] no DIGEST_WEBHOOK_URL configured; skipping notification")
        return False

    payload = {
        "title": "GYAAN daily digest ready",
        "body": f"{processed_count} articles were analyzed and are ready to view.",
        "type": "daily_digest_ready",
        "processed_articles": processed_count,
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(webhook_url, json=payload)
            response.raise_for_status()
        print(f"[scheduler] sent digest notification to {webhook_url}")
        return True
    except Exception as exc:
        print(f"[scheduler] failed to send digest notification: {exc}")
        return False


def start_daily_scrape_scheduler() -> AsyncIOScheduler:
    global _scheduler
    if _scheduler is not None:
        if _scheduler.running:
            return _scheduler
        _scheduler.shutdown(wait=False)

    cron_expression = os.getenv("DAILY_SCRAPE_CRON", "30 18 * * *")
    _scheduler = AsyncIOScheduler(timezone="Asia/Kolkata")
    _scheduler.add_job(
        run_daily_scrape,
        trigger=CronTrigger.from_crontab(cron_expression, timezone="Asia/Kolkata"),
        id="daily-scrape",
        replace_existing=True,
        misfire_grace_time=300,
    )
    _scheduler.start()
    return _scheduler


async def process_daily_digest(scraped_count: int) -> int:
    analysis_service = AnalysisService(LLMProvider())
    processed_count = 0

    async with async_session() as session:
        stmt = (
            select(Article)
            .where(Article.analysis_ready.is_(False))
            .order_by(Article.published_at.desc(), Article.importance_score.desc())
            .limit(_DIGEST_LIMIT)
        )
        result = await session.execute(stmt)
        articles = result.scalars().all()

        for article in articles:
            try:
                concepts = [concept.strip() for concept in article.concepts.split(",") if concept.strip()]
                analysis = await analysis_service.generate_deep_analysis(article.content, concepts)
                article.summary = analysis.get("one_sentence_summary", article.summary)
                article.plain_english = analysis.get("plain_english", article.plain_english)
                article.analysis_payload = json.dumps(analysis)
                article.analysis_ready = True
                article.is_curated = True
                processed_count += 1
            except Exception as exc:
                print(f"[scheduler] failed to analyze article {article.id}: {exc}")

        await session.commit()

    print(f"[scheduler] analyzed {processed_count} new articles (scraped={scraped_count})")
    if processed_count > 0:
        await send_digest_notification(processed_count)
    return processed_count


async def run_daily_scrape() -> None:
    try:
        async with async_session() as session:
            count = await scrape_latest_articles(session)
            print(f"[scheduler] scraped {count} latest articles")

        await process_daily_digest(count)
    except Exception as exc:
        print(f"[scheduler] failed to scrape latest articles: {exc}")
