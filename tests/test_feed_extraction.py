import asyncio
import unittest

from backend.app.services.news_scraper import FEED_URLS, NewsScraper

SOURCE_FEED_KEYWORDS = {
    "linkedin": "LinkedIn+Engineering",
    "google_news": "news.google.com/rss",
    "hacker_news": "hnrss.org",
    "reddit": "reddit.com",
}


class FeedExtractionTests(unittest.TestCase):
    def _feed_urls_for(self, source: str):
        keyword = SOURCE_FEED_KEYWORDS[source]
        return [url for url in FEED_URLS if keyword in url]

    def _extract_all(self, feed_urls):
        scraper = NewsScraper(feed_urls)

        async def run():
            results = []
            for url in feed_urls:
                try:
                    articles = await scraper.fetch_feed(url)
                    results.append((url, articles))
                except Exception as exc:
                    results.append((url, exc))
            return results

        return asyncio.run(run())

    def _assert_source_extracts_articles(self, source):
        feed_urls = self._feed_urls_for(source)
        self.assertGreater(len(feed_urls), 0, f"no {source} feed URLs configured in FEED_URLS")

        results = self._extract_all(feed_urls)
        total = 0
        details = []
        for url, articles in results:
            if isinstance(articles, Exception):
                details.append(f"{url} -> ERROR: {articles}")
                continue
            valid = [a for a in articles if a.get("title") and a.get("url") and a.get("content")]
            total += len(valid)
            details.append(f"{url} -> {len(valid)} valid articles")

        print(f"\n[{source}] {' | '.join(details)}")
        self.assertGreater(total, 0, f"could not extract any articles from {source} feeds:\n" + "\n".join(details))

    def test_linkedin_articles_extract(self):
        self._assert_source_extracts_articles("linkedin")

    def test_google_news_articles_extract(self):
        self._assert_source_extracts_articles("google_news")

    def test_hacker_news_articles_extract(self):
        self._assert_source_extracts_articles("hacker_news")

    def test_reddit_articles_extract(self):
        self._assert_source_extracts_articles("reddit")


if __name__ == "__main__":
    unittest.main()
