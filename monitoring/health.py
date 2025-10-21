"""Health check endpoint."""

from datetime import datetime
from typing import Dict, Any

import structlog

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
        self.start_time = datetime.utcnow()
        self.last_check = datetime.utcnow()
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

    def check_api_connectivity(self) -> Dict[str, bool]:
        """Check API connectivity.

        Returns:
            Dictionary of API status
        """
        status = {
            "coingecko": True,
            "cmc": True,
            "cmc_dex": True,
        }
        # TODO: Implement actual health checks for each API

        return status

    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status.

        Returns:
            Health status dictionary
        """
        db_ok = self.check_database_connection()
        api_status = self.check_api_connectivity()

        all_apis_ok = all(api_status.values())

        if not db_ok:
            overall_status = HealthStatus.UNHEALTHY
        elif not all_apis_ok:
            overall_status = HealthStatus.DEGRADED
        else:
            overall_status = HealthStatus.HEALTHY

        uptime = (datetime.utcnow() - self.start_time).total_seconds()

        return {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": uptime,
            "database": {
                "status": "ok" if db_ok else "error",
                "error": self.errors.get("database"),
            },
            "apis": api_status,
            "errors": self.errors if self.errors else None,
        }
