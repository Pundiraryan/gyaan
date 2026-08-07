import asyncio
import hashlib
import re
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional

import feedparser
import httpx

from ..crud import upsert_articles

FEED_URLS = [
    # Engineering blogs
    "https://engineering.linkedin.com/rss",
    "https://feeds.feedburner.com/TechCrunch/",
    "https://www.wired.com/feed/rss",
    "https://www.theverge.com/rss/index.xml",
    "https://engineering.googleblog.com/atom.xml",
    "https://engineering.fb.com/rss",
    "https://aws.amazon.com/blogs/engineering/feed/rss/",
    # Research papers / academic feeds
    "https://export.arxiv.org/rss/cs.AI",
    "https://export.arxiv.org/rss/cs.LG",
    "https://export.arxiv.org/rss/cs.CR",
    # Startup / financial news
    "https://feeds.feedburner.com/venturebeat",
    "https://www.cnbc.com/id/10001147/device/rss/rss.html",
    "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml",
    "https://feeds.a.dj.com/rss/RSSMarketsMain.xml",
    # Technical discussions and community
    "https://hnrss.org/frontpage",
    "https://www.reddit.com/r/technology/.rss",
    "https://www.reddit.com/r/programming/.rss",
    "https://www.reddit.com/r/MachineLearning/.rss",
    # X/Twitter and LinkedIn adjacent feeds via public aggregators
    "https://nitter.net/search/rss?q=technology",
    "https://nitter.net/search/rss?q=programming",
    # Google News RSS feeds. Prefer RSS over scraping Google News pages directly.
    "https://news.google.com/rss/headlines/section/topic/TECHNOLOGY?hl=en-IN&gl=IN&ceid=IN:en",
    "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=en-IN&gl=IN&ceid=IN:en",
    "https://news.google.com/rss/headlines/section/topic/SCIENCE?hl=en-IN&gl=IN&ceid=IN:en",
    "https://news.google.com/rss/search?q=artificial+intelligence+when:1d&hl=en-IN&gl=IN&ceid=IN:en",
    "https://news.google.com/rss/search?q=startups+technology+when:1d&hl=en-IN&gl=IN&ceid=IN:en",
    "https://news.google.com/rss/search?q=cybersecurity+when:1d&hl=en-IN&gl=IN&ceid=IN:en",
]

SOURCE_PRIORITY = {
    "TechCrunch": 0.95,
    "The Verge": 0.93,
    "Wired": 0.92,
    "LinkedIn": 0.91,
    "Google AI Blog": 0.90,
    "arXiv": 0.88,
    "Hacker News": 0.89,
    "Reddit": 0.86,
    "CNBC": 0.85,
    "Wall Street Journal": 0.84,
    "Feedburner": 0.83,
    "VentureBeat": 0.87,
    "Google News": 0.90,
}


def clean_html(value: str) -> str:
    if not value:
        return ""
    text = re.sub(r"<[^>]+>", "", value)
    return re.sub(r"\s+", " ", text).strip()


def build_article_id(url: str, title: str) -> str:
    source = url or title
    return hashlib.sha256(source.encode("utf-8")).hexdigest()[:32]


def build_concepts(entry: Dict[str, Any], title: str) -> str:
    tags = []
    if entry.get("tags"):
        tags = [tag.get("term", "").strip() for tag in entry.get("tags", []) if tag.get("term")]
    if tags:
        return ",".join(dict.fromkeys(tags))

    words = [word.lower() for word in re.findall(r"[A-Za-z]{4,}", title)]
    unique_words = []
    for word in words:
        if word not in unique_words and word not in ["https", "http", "feed"]:
            unique_words.append(word)
        if len(unique_words) >= 8:
            break
    return ",".join(unique_words)


def build_importance_score(source: str, published_at: Optional[datetime]) -> float:
    score = 0.70
    if source in SOURCE_PRIORITY:
        score = SOURCE_PRIORITY[source]
    elif source.startswith("Google News"):
        score = SOURCE_PRIORITY["Google News"]
    if published_at:
        age_hours = (datetime.utcnow() - published_at).total_seconds() / 3600
        recency_bonus = max(0.0, 0.15 - min(age_hours / 48.0, 0.15))
        score += recency_bonus
    return min(max(score, 0.55), 0.99)


def parse_published_at(entry: Dict[str, Any]) -> Optional[datetime]:
    parsed = entry.get("published_parsed") or entry.get("updated_parsed")
    if parsed:
        return datetime(*parsed[:6])
    return None


class NewsScraper:
    def __init__(self, feed_urls: Optional[Iterable[str]] = None):
        self.feed_urls = list(feed_urls) if feed_urls else FEED_URLS

    async def fetch_feed(self, feed_url: str) -> List[Dict[str, Any]]:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(feed_url)
            response.raise_for_status()
            feed = await asyncio.to_thread(feedparser.parse, response.text)

        if getattr(feed, "bozo", False):
            return []

        source = clean_html(feed.feed.get("title", "News Feed"))
        articles: List[Dict[str, Any]] = []

        for entry in feed.entries[:20]:
            link = entry.get("link") or entry.get("id") or ""
            title = clean_html(entry.get("title", "Untitled"))
            summary = clean_html(entry.get("summary", entry.get("description", "")))
            content_blocks = entry.get("content") or []
            content = ""
            if content_blocks:
                content = clean_html(content_blocks[0].get("value", ""))
            content = content or summary or title
            published_at = parse_published_at(entry)
            concepts = build_concepts(entry, title)
            article_id = build_article_id(link, title)
            importance_score = build_importance_score(source, published_at)

            articles.append(
                {
                    "id": article_id,
                    "title": title,
                    "content": content,
                    "summary": summary or content[:250],
                    "plain_english": summary or content[:250],
                    "source": source,
                    "url": link,
                    "published_at": published_at,
                    "importance_score": importance_score,
                    "is_curated": False,
                    "concepts": concepts,
                }
            )

        return articles

    async def scrape_to_db(self, session) -> int:
        tasks = [self.fetch_feed(url) for url in self.feed_urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        articles: List[Dict[str, Any]] = []
        for result in results:
            if isinstance(result, Exception):
                continue
            articles.extend(result)

        if not articles:
            return 0

        return await upsert_articles(session, articles)


async def scrape_latest_articles(session) -> int:
    scraper = NewsScraper()
    return await scraper.scrape_to_db(session)
