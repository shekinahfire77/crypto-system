"""Prometheus metrics collection."""

from prometheus_client import Counter, Gauge, Histogram, Summary
from typing import Dict, Any

# API Request Metrics
api_requests_total = Counter(
    "crypto_api_requests_total",
    "Total API requests",
    ["api_name", "endpoint", "status"],
)

api_request_duration = Histogram(
    "crypto_api_request_duration_seconds",
    "API request duration",
    ["api_name", "endpoint"],
)

api_request_errors = Counter(
    "crypto_api_request_errors_total",
    "Total API request errors",
    ["api_name", "error_type"],
)

api_rate_limit_remaining = Gauge(
    "crypto_api_rate_limit_remaining",
    "Remaining API calls",
    ["api_name"],
)

# Database Metrics
db_operations_total = Counter(
    "crypto_db_operations_total",
    "Total database operations",
    ["operation", "table"],
)

db_operation_duration = Histogram(
    "crypto_db_operation_duration_seconds",
    "Database operation duration",
    ["operation", "table"],
)

db_operation_errors = Counter(
    "crypto_db_operation_errors_total",
    "Total database operation errors",
    ["operation", "table", "error_type"],
)

db_connection_pool_size = Gauge(
    "crypto_db_connection_pool_size",
    "Database connection pool size",
)

db_active_connections = Gauge(
    "crypto_db_active_connections",
    "Active database connections",
)

# Data Processing Metrics
records_processed = Counter(
    "crypto_records_processed_total",
    "Total records processed",
    ["source", "data_type"],
)

processing_errors = Counter(
    "crypto_processing_errors_total",
    "Total processing errors",
    ["source", "error_type"],
)

processing_duration = Histogram(
    "crypto_processing_duration_seconds",
    "Data processing duration",
    ["source", "data_type"],
)

# System Metrics
scheduler_jobs_running = Gauge(
    "crypto_scheduler_jobs_running",
    "Number of running scheduler jobs",
)

scheduler_job_duration = Summary(
    "crypto_scheduler_job_duration_seconds",
    "Scheduler job duration",
    ["job_name"],
)

scheduler_job_errors = Counter(
    "crypto_scheduler_job_errors_total",
    "Scheduler job errors",
    ["job_name", "error_type"],
)

service_startup_timestamp = Gauge(
    "crypto_service_startup_timestamp",
    "Service startup timestamp",
)

service_uptime_seconds = Gauge(
    "crypto_service_uptime_seconds",
    "Service uptime in seconds",
)


class MetricsCollector:
    """Centralized metrics collection."""

    @staticmethod
    def record_api_request(
        api_name: str,
        endpoint: str,
        status: str,
        duration: float,
    ) -> None:
        """Record API request metrics.

        Args:
            api_name: API service name
            endpoint: API endpoint
            status: Request status
            duration: Request duration in seconds
        """
        api_requests_total.labels(
            api_name=api_name,
            endpoint=endpoint,
            status=status,
        ).inc()

        api_request_duration.labels(
            api_name=api_name,
            endpoint=endpoint,
        ).observe(duration)

    @staticmethod
    def record_api_error(
        api_name: str,
        error_type: str,
    ) -> None:
        """Record API error metrics.

        Args:
            api_name: API service name
            error_type: Error type
        """
        api_request_errors.labels(
            api_name=api_name,
            error_type=error_type,
        ).inc()

    @staticmethod
    def set_rate_limit_remaining(
        api_name: str,
        remaining: int,
    ) -> None:
        """Set remaining rate limit.

        Args:
            api_name: API service name
            remaining: Remaining calls
        """
        api_rate_limit_remaining.labels(api_name=api_name).set(remaining)

    @staticmethod
    def record_db_operation(
        operation: str,
        table: str,
        duration: float,
        success: bool = True,
    ) -> None:
        """Record database operation metrics.

        Args:
            operation: Operation type (select, insert, update, delete)
            table: Table name
            duration: Operation duration
            success: Whether operation succeeded
        """
        db_operations_total.labels(operation=operation, table=table).inc()

        if success:
            db_operation_duration.labels(
                operation=operation,
                table=table,
            ).observe(duration)

    @staticmethod
    def record_db_error(
        operation: str,
        table: str,
        error_type: str,
    ) -> None:
        """Record database operation error.

        Args:
            operation: Operation type
            table: Table name
            error_type: Error type
        """
        db_operation_errors.labels(
            operation=operation,
            table=table,
            error_type=error_type,
        ).inc()

    @staticmethod
    def record_records_processed(
        source: str,
        data_type: str,
        count: int,
    ) -> None:
        """Record processed records.

        Args:
            source: Data source
            data_type: Type of data
            count: Number of records
        """
        records_processed.labels(source=source, data_type=data_type).inc(count)

    @staticmethod
    def record_processing_error(
        source: str,
        error_type: str,
    ) -> None:
        """Record processing error.

        Args:
            source: Data source
            error_type: Error type
        """
        processing_errors.labels(source=source, error_type=error_type).inc()

    @staticmethod
    def record_scheduler_job(
        job_name: str,
        duration: float,
        success: bool = True,
    ) -> None:
        """Record scheduler job execution.

        Args:
            job_name: Job name
            duration: Job duration
            success: Whether job succeeded
        """
        if success:
            scheduler_job_duration.labels(job_name=job_name).observe(duration)

    @staticmethod
    def record_scheduler_error(
        job_name: str,
        error_type: str,
    ) -> None:
        """Record scheduler job error.

        Args:
            job_name: Job name
            error_type: Error type
        """
        scheduler_job_errors.labels(job_name=job_name, error_type=error_type).inc()
