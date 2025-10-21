"""Health check endpoint."""

import asyncio
from datetime import datetime
from typing import Dict, Any, Optional

import aiohttp
import structlog

from config.settings import get_settings

logger = structlog.get_logger(__name__)


class HealthStatus:
    """Health status enumeration."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class HealthChecker:
    """Service health checker."""

    def __init__(self):
        """Initialize health checker."""
        from datetime import timezone
        now = datetime.now(timezone.utc)
        self.start_time = now
        self.last_check = now
        self.status = HealthStatus.HEALTHY
        self.errors: Dict[str, Any] = {}

    def check_database_connection(self) -> bool:
        """Check database connectivity.

        Returns:
            True if database is accessible
        """
        try:
            from database.connection import get_db_session

            session = get_db_session()
            session.execute("SELECT 1")
            session.close()
            return True
        except Exception as e:
            self.errors["database"] = str(e)
            return False

    async def check_api_connectivity(self) -> Dict[str, bool]:
        """Check API connectivity.

        Returns:
            Dictionary of API status
        """
        settings = get_settings()
        status = {}
        
        # Check CoinGecko
        if settings.enable_coingecko:
            status["coingecko"] = await self._check_coingecko(settings)
        else:
            status["coingecko"] = None  # Disabled
        
        # Check CoinMarketCap
        if settings.enable_cmc:
            status["cmc"] = await self._check_cmc(settings)
        else:
            status["cmc"] = None  # Disabled
        
        # Check CMC DEX
        if settings.enable_cmc_dex:
            status["cmc_dex"] = await self._check_cmc_dex(settings)
        else:
            status["cmc_dex"] = None  # Disabled

        return status

    async def _check_coingecko(self, settings) -> bool:
        """Check CoinGecko API health.
        
        Args:
            settings: Application settings
            
        Returns:
            True if API is reachable and responding
        """
        try:
            async with aiohttp.ClientSession() as session:
                # Lightweight ping endpoint
                url = f"{settings.coingecko_base_url}/ping"
                headers = {}
                if settings.coingecko_api_key:
                    headers["x-cg-pro-api-key"] = settings.coingecko_api_key
                
                async with session.get(
                    url, 
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    return response.status == 200
        except Exception as e:
            self.errors["coingecko"] = str(e)
            await logger.awarning("coingecko_health_check_failed", error=str(e))
            return False

    async def _check_cmc(self, settings) -> bool:
        """Check CoinMarketCap API health.
        
        Args:
            settings: Application settings
            
        Returns:
            True if API is reachable and responding
        """
        try:
            async with aiohttp.ClientSession() as session:
                # Lightweight info endpoint
                url = f"{settings.cmc_base_url}/v1/key/info"
                headers = {"X-CMC_PRO_API_KEY": settings.cmc_api_key}
                
                async with session.get(
                    url,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    return response.status == 200
        except Exception as e:
            self.errors["cmc"] = str(e)
            await logger.awarning("cmc_health_check_failed", error=str(e))
            return False

    async def _check_cmc_dex(self, settings) -> bool:
        """Check CoinMarketCap DEX API health.
        
        Args:
            settings: Application settings
            
        Returns:
            True if API is reachable and responding
        """
        try:
            async with aiohttp.ClientSession() as session:
                # Use same key info endpoint as CMC
                url = f"{settings.cmc_dex_base_url}/v1/key/info"
                headers = {"X-CMC_PRO_API_KEY": settings.cmc_dex_api_key}
                
                async with session.get(
                    url,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    return response.status == 200
        except Exception as e:
            self.errors["cmc_dex"] = str(e)
            await logger.awarning("cmc_dex_health_check_failed", error=str(e))
            return False

    async def get_health_status(self) -> Dict[str, Any]:
        """Get current health status.

        Returns:
            Health status dictionary
        """
        db_ok = self.check_database_connection()
        api_status = await self.check_api_connectivity()

        all_apis_ok = all(v is True for v in api_status.values() if v is not None)

        if not db_ok:
            overall_status = HealthStatus.UNHEALTHY
        elif not all_apis_ok:
            overall_status = HealthStatus.DEGRADED
        else:
            overall_status = HealthStatus.HEALTHY

        from datetime import timezone
        now = datetime.now(timezone.utc)
        uptime = (now - self.start_time).total_seconds()

        return {
            "status": overall_status,
            "timestamp": now.isoformat(),
            "uptime_seconds": uptime,
            "database": {
                "status": "ok" if db_ok else "error",
                "error": self.errors.get("database"),
            },
            "apis": api_status,
            "errors": self.errors if self.errors else None,
        }
