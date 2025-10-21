"""Base API service class with rate limiting and error handling."""

import asyncio
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import aiohttp
import structlog
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

logger = structlog.get_logger(__name__)


class RateLimiter:
    """Token bucket rate limiter for API calls."""

    def __init__(self, calls_per_minute: int):
        """Initialize rate limiter.

        Args:
            calls_per_minute: Maximum calls allowed per minute
        """
        self.calls_per_minute = calls_per_minute
        self.tokens = calls_per_minute
        self.last_update = time.time()
        self.lock = asyncio.Lock()

    async def acquire(self) -> None:
        """Acquire a token, waiting if necessary."""
        async with self.lock:
            now = time.time()
            time_passed = now - self.last_update
            self.tokens = min(
                self.calls_per_minute,
                self.tokens + (time_passed * self.calls_per_minute / 60),
            )
            self.last_update = now

            if self.tokens < 1:
                wait_time = (1 - self.tokens) * 60 / self.calls_per_minute
                await logger.ainfo(
                    "rate_limit_wait",
                    wait_seconds=round(wait_time, 2),
                )
                await asyncio.sleep(wait_time)
                self.tokens = 0
            else:
                self.tokens -= 1


class BaseAPIService(ABC):
    """Base class for API services with rate limiting and retry logic."""

    def __init__(
        self,
        api_key: str,
        base_url: str,
        rate_limit: int,
        max_retries: int = 3,
        backoff_factor: float = 2.0,
    ):
        """Initialize API service.

        Args:
            api_key: API authentication key
            base_url: Base URL for API endpoints
            rate_limit: Maximum calls per minute
            max_retries: Maximum number of retry attempts
            backoff_factor: Exponential backoff factor
        """
        self.api_key = api_key
        self.base_url = base_url
        self.rate_limiter = RateLimiter(rate_limit)
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.session: Optional[aiohttp.ClientSession] = None
        self.logger = structlog.get_logger(__name__)

    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()

    @abstractmethod
    def get_headers(self) -> Dict[str, str]:
        """Get API-specific headers.

        Returns:
            Dictionary of HTTP headers
        """
        pass

    @retry(
        retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def make_request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        method: str = "GET",
    ) -> Dict[str, Any]:
        """Make rate-limited API request with retry logic.

        Args:
            endpoint: API endpoint path
            params: Query parameters
            method: HTTP method

        Returns:
            JSON response as dictionary

        Raises:
            aiohttp.ClientError: If request fails after retries
            ValueError: If response is not valid JSON
        """
        await self.rate_limiter.acquire()

        url = f"{self.base_url}/{endpoint}"
        headers = self.get_headers()

        try:
            async with self.session.request(
                method, url, headers=headers, params=params, timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                # Handle rate limit responses
                if response.status == 429:
                    retry_after = int(response.headers.get("Retry-After", 60))
                    await self.logger.awarning(
                        "api_rate_limited",
                        endpoint=endpoint,
                        retry_after=retry_after,
                    )
                    await asyncio.sleep(retry_after)
                    return await self.make_request(endpoint, params, method)

                response.raise_for_status()

                try:
                    data = await response.json()
                except ValueError as e:
                    await self.logger.aerror(
                        "invalid_json_response",
                        endpoint=endpoint,
                        status=response.status,
                        error=str(e),
                    )
                    raise

                await self.logger.ainfo(
                    "api_request_success",
                    endpoint=endpoint,
                    status=response.status,
                )

                return data

        except aiohttp.ClientError as e:
            await self.logger.aerror(
                "api_request_failed",
                endpoint=endpoint,
                error=str(e),
            )
            raise

    async def batch_request(
        self,
        endpoints: list[str],
        params_list: Optional[list[Optional[Dict[str, Any]]]] = None,
    ) -> list[Dict[str, Any]]:
        """Make multiple requests concurrently.

        Args:
            endpoints: List of endpoint paths
            params_list: List of parameter dictionaries

        Returns:
            List of responses
        """
        if params_list is None:
            params_list = [None] * len(endpoints)

        tasks = [
            self.make_request(endpoint, params)
            for endpoint, params in zip(endpoints, params_list)
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Log any exceptions
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                await self.logger.aerror(
                    "batch_request_error",
                    endpoint=endpoints[i],
                    error=str(result),
                )

        return [r for r in results if not isinstance(r, Exception)]
