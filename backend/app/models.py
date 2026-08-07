from sqlalchemy import Column, String, Text, Float, DateTime, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class Article(Base):
    __tablename__ = "articles"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str] = mapped_column(String(128), nullable=False)
    url: Mapped[str] = mapped_column(String(1024), nullable=False)
    published_at: Mapped[DateTime] = mapped_column(DateTime)
    importance_score: Mapped[float] = mapped_column(Float, default=0.0)
    is_curated: Mapped[bool] = mapped_column(Boolean, default=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False, default="")
    plain_english: Mapped[str] = mapped_column(Text, nullable=False, default="")
    concepts: Mapped[str] = mapped_column(Text, nullable=False, default="")
    analysis_payload: Mapped[str] = mapped_column(Text, nullable=False, default="")
    analysis_ready: Mapped[bool] = mapped_column(Boolean, default=False)
