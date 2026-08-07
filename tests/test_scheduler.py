import asyncio
import unittest
from unittest.mock import AsyncMock, patch

from backend.app.services import scheduler
from backend.app.services.scheduler import start_daily_scrape_scheduler


class DailyScrapeSchedulerTests(unittest.TestCase):
    def test_start_daily_scrape_scheduler_registers_job_once(self):
        with patch("backend.app.services.scheduler.AsyncIOScheduler") as scheduler_cls:
            scheduler_instance = scheduler_cls.return_value
            scheduler_instance.running = False

            start_daily_scrape_scheduler()

            scheduler_instance.add_job.assert_called_once()
            scheduler_instance.start.assert_called_once()

    def test_run_daily_scrape_triggers_digest_pipeline(self):
        with patch("backend.app.services.scheduler.scrape_latest_articles", new_callable=AsyncMock) as scrape_mock, patch(
            "backend.app.services.scheduler.process_daily_digest", new_callable=AsyncMock
        ) as digest_mock:
            scrape_mock.return_value = 3

            asyncio.run(scheduler.run_daily_scrape())

            scrape_mock.assert_awaited_once()
            digest_mock.assert_awaited_once_with(3)


if __name__ == "__main__":
    unittest.main()
