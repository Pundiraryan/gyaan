import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from .routes import router
from .database import engine, async_session, ensure_dev_schema
from .models import Base
from .crud import ensure_seed_data
from .services.news_scraper import scrape_latest_articles
from .services.scheduler import process_daily_digest, start_daily_scrape_scheduler

app = FastAPI(title="GYAAN API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await ensure_dev_schema()

    async with async_session() as session:
        await ensure_seed_data(session)
        if os.getenv("ENABLE_STARTUP_SCRAPE", "true").lower() in ("1", "true", "yes"):
            try:
                count = await scrape_latest_articles(session)
                print(f"[startup] scraped {count} latest articles")
                await process_daily_digest(count)
            except Exception as exc:
                print(f"[startup] failed to scrape latest articles: {exc}")

    start_daily_scrape_scheduler()
