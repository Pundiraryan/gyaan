from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import os

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    sqlite_path = os.path.join(os.path.dirname(__file__), "..", "gyaan_dev.db")
    sqlite_path = os.path.abspath(sqlite_path)
    DATABASE_URL = f"sqlite+aiosqlite:///{sqlite_path}"

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=False, future=True, connect_args=connect_args)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def ensure_dev_schema() -> None:
    if not DATABASE_URL.startswith("sqlite"):
        return

    async with engine.begin() as conn:
        columns_result = await conn.execute(text("PRAGMA table_info(articles)"))
        existing_columns = {row[1] for row in columns_result.fetchall()}

        if "analysis_payload" not in existing_columns:
            await conn.execute(text("ALTER TABLE articles ADD COLUMN analysis_payload TEXT NOT NULL DEFAULT ''"))
        if "analysis_ready" not in existing_columns:
            await conn.execute(text("ALTER TABLE articles ADD COLUMN analysis_ready BOOLEAN NOT NULL DEFAULT 0"))
