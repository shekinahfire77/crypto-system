"""APScheduler orchestration and job scheduling."""

import asyncio
from datetime import datetime
from typing import Optional

import structlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from config.settings import get_settings

logger = structlog.get_logger(__name__)


class SchedulerManager:
    """Manages APScheduler instance and job scheduling."""

    def __init__(self):
        """Initialize scheduler manager."""
        self.scheduler = AsyncIOScheduler()
        self.settings = get_settings()
        self.is_running = False

    async def start(self) -> None:
        """Start the scheduler."""
        if not self.is_running:
            self.scheduler.start()
            self.is_running = True
            await logger.ainfo("scheduler_started")

    async def stop(self) -> None:
        """Stop the scheduler."""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            await logger.ainfo("scheduler_stopped")

    def schedule_price_update(
        self,
        job_func,
        job_id: str = "price_update",
    ) -> None:
        """Schedule price update job.

        Args:
            job_func: Async function to execute
            job_id: Job identifier
        """
        self.scheduler.add_job(
            job_func,
            trigger=IntervalTrigger(seconds=self.settings.price_update_interval),
            id=job_id,
            name="Price Update",
            misfire_grace_time=10,
            coalesce=True,
            max_instances=1,
        )

    def schedule_metadata_update(
        self,
        job_func,
        job_id: str = "metadata_update",
    ) -> None:
        """Schedule metadata update job.

        Args:
            job_func: Async function to execute
            job_id: Job identifier
        """
        self.scheduler.add_job(
            job_func,
            trigger=IntervalTrigger(seconds=self.settings.metadata_update_interval),
            id=job_id,
            name="Metadata Update",
            misfire_grace_time=60,
            coalesce=True,
            max_instances=1,
        )

    def schedule_sentiment_update(
        self,
        job_func,
        job_id: str = "sentiment_update",
    ) -> None:
        """Schedule sentiment update job.

        Args:
            job_func: Async function to execute
            job_id: Job identifier
        """
        self.scheduler.add_job(
            job_func,
            trigger=IntervalTrigger(seconds=self.settings.sentiment_update_interval),
            id=job_id,
            name="Sentiment Update",
            misfire_grace_time=30,
            coalesce=True,
            max_instances=1,
        )

    def schedule_dex_update(
        self,
        job_func,
        job_id: str = "dex_update",
    ) -> None:
        """Schedule DEX update job.

        Args:
            job_func: Async function to execute
            job_id: Job identifier
        """
        self.scheduler.add_job(
            job_func,
            trigger=IntervalTrigger(seconds=self.settings.dex_update_interval),
            id=job_id,
            name="DEX Update",
            misfire_grace_time=30,
            coalesce=True,
            max_instances=1,
        )

    def schedule_exchange_update(
        self,
        job_func,
        job_id: str = "exchange_update",
    ) -> None:
        """Schedule exchange update job.

        Args:
            job_func: Async function to execute
            job_id: Job identifier
        """
        self.scheduler.add_job(
            job_func,
            trigger=IntervalTrigger(seconds=self.settings.exchange_update_interval),
            id=job_id,
            name="Exchange Update",
            misfire_grace_time=60,
            coalesce=True,
            max_instances=1,
        )

    def get_jobs(self) -> list:
        """Get all scheduled jobs.

        Returns:
            List of scheduled jobs
        """
        return self.scheduler.get_jobs()

    def remove_job(self, job_id: str) -> None:
        """Remove a scheduled job.

        Args:
            job_id: Job identifier
        """
        self.scheduler.remove_job(job_id)


# Global scheduler instance
_scheduler: Optional[SchedulerManager] = None


def get_scheduler() -> SchedulerManager:
    """Get or create scheduler instance.

    Returns:
        SchedulerManager instance
    """
    global _scheduler
    if _scheduler is None:
        _scheduler = SchedulerManager()
    return _scheduler
