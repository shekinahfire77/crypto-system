"""Main entry point for crypto system."""

import asyncio
import platform
import signal
import sys
from time import time

import structlog
from prometheus_client import start_http_server

from config.settings import get_settings
from monitoring.logger import setup_logging
from monitoring.metrics import MetricsCollector, service_startup_timestamp, service_uptime_seconds
from monitoring.health import HealthChecker
from orchestration.scheduler import get_scheduler
from orchestration.coordinator import DataCoordinator

logger = structlog.get_logger(__name__)


class CryptoSystemService:
    """Main service orchestrator."""

    def __init__(self):
        """Initialize service."""
        self.settings = get_settings()
        self.coordinator = DataCoordinator()
        self.scheduler = get_scheduler()
        self.health_checker = HealthChecker()
        self.is_running = False
        self.start_time = time()

    async def initialize(self) -> None:
        """Initialize service components."""
        await logger.ainfo(
            "service_initializing",
            settings=self.settings.get_masked_settings(),
        )

        # Setup logging
        setup_logging(
            log_level=self.settings.log_level,
            log_file=self.settings.log_file,
        )

        # Start metrics server
        start_http_server(self.settings.metrics_port)
        await logger.ainfo(
            "metrics_server_started",
            port=self.settings.metrics_port,
        )

        # Record startup time
        service_startup_timestamp.set_to_current_time()

        # Initialize coordinator
        await self.coordinator.initialize()

        await logger.ainfo("service_initialized")

    async def setup_jobs(self) -> None:
        """Setup scheduled jobs."""
        await logger.ainfo("setting_up_jobs")

        # Price update job
        if self.settings.enable_coingecko or self.settings.enable_cmc:
            self.scheduler.schedule_price_update(
                self.coordinator.fetch_and_store_prices
            )

        # Metadata update job
        if self.settings.enable_coingecko:
            self.scheduler.schedule_metadata_update(
                self.coordinator.fetch_and_store_metadata
            )

        # Sentiment update job
        if self.settings.enable_sentiment_analysis:
            self.scheduler.schedule_sentiment_update(
                self.coordinator.fetch_and_store_sentiment
            )

        # DEX update job
        if self.settings.enable_cmc_dex:
            self.scheduler.schedule_dex_update(
                self.coordinator.fetch_and_store_dex_data
            )

        # Exchange update job
        if self.settings.enable_coingecko:
            self.scheduler.schedule_exchange_update(
                self.coordinator.fetch_and_store_exchanges
            )

        await logger.ainfo(
            "jobs_setup",
            job_count=len(self.scheduler.get_jobs()),
        )

    async def start(self) -> None:
        """Start the service."""
        if self.is_running:
            return

        await self.initialize()
        await self.setup_jobs()

        await self.scheduler.start()
        self.is_running = True

        await logger.ainfo("service_started")

        # Update uptime metrics periodically
        while self.is_running:
            uptime = time() - self.start_time
            service_uptime_seconds.set(uptime)
            await asyncio.sleep(10)

    async def stop(self) -> None:
        """Stop the service."""
        if not self.is_running:
            return

        await logger.ainfo("service_stopping")

        self.is_running = False
        await self.scheduler.stop()
        await self.coordinator.cleanup()

        await logger.ainfo("service_stopped")

    async def health_check(self) -> dict:
        """Get service health status.

        Returns:
            Health status dictionary
        """
        return self.health_checker.get_health_status()


async def main() -> None:
    """Main entry point."""
    service = CryptoSystemService()

    async def signal_handler(sig: int) -> None:
        """Handle shutdown signals."""
        await logger.ainfo("signal_received", signal=sig)
        await service.stop()
        sys.exit(0)

    # Register signal handlers (Unix/Linux only - not available on Windows)
    if platform.system() != "Windows":
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(
                sig,
                lambda s=sig: asyncio.create_task(signal_handler(s)),
            )
    else:
        await logger.ainfo("signal_handlers_not_available_on_windows")

    try:
        await service.start()
    except KeyboardInterrupt:
        await logger.ainfo("keyboard_interrupt_received")
        await service.stop()
        sys.exit(0)
    except Exception as e:
        await logger.aerror("service_error", error=str(e), exc_info=True)
        await service.stop()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
