import unittest

from backend.app.services.news_scraper import FEED_URLS, NewsScraper, build_importance_score


class NewsScraperTests(unittest.TestCase):
    def test_google_news_rss_feeds_are_configured(self):
        google_news_urls = [url for url in FEED_URLS if "news.google.com/rss" in url]

        self.assertGreaterEqual(len(google_news_urls), 3)
        self.assertTrue(all("hl=en-IN" in url and "gl=IN" in url for url in google_news_urls))

    def test_google_news_source_titles_get_priority_score(self):
        score = build_importance_score("Google News - Technology", None)

        self.assertEqual(score, 0.90)

    def test_scraper_accepts_custom_feed_urls(self):
        scraper = NewsScraper(["https://example.com/feed.xml"])

        self.assertEqual(scraper.feed_urls, ["https://example.com/feed.xml"])


if __name__ == "__main__":
    unittest.main()
