"""Data processing pipeline."""

import asyncio
import time
from typing import Callable, Optional

import structlog

from monitoring.metrics import MetricsCollector

logger = structlog.get_logger(__name__)


class DataPipeline:
    """Data processing pipeline with error handling and metrics."""

    def __init__(self, name: str):
        """Initialize pipeline.

        Args:
            name: Pipeline name
        """
        self.name = name
        self.stages: list[tuple[str, Callable]] = []

    def add_stage(
        self,
        stage_name: str,
        handler: Callable,
    ) -> "DataPipeline":
        """Add a processing stage.

        Args:
            stage_name: Stage name
            handler: Async handler function

        Returns:
            Self for chaining
        """
        self.stages.append((stage_name, handler))
        return self

    async def execute(self, data: dict | list) -> Optional[dict | list]:
        """Execute the pipeline.

        Args:
            data: Input data

        Returns:
            Processed data or None if pipeline fails
        """
        await logger.ainfo("pipeline_started", pipeline=self.name)
        
        start_time = time.time()
        current_data = data

        for stage_name, handler in self.stages:
            try:
                await logger.ainfo("executing_stage", stage=stage_name)
                stage_start = time.time()
                
                current_data = await handler(current_data)
                
                stage_duration = time.time() - stage_start
                await logger.ainfo(
                    "stage_completed",
                    stage=stage_name,
                    duration=round(stage_duration, 2),
                )

            except Exception as e:
                await logger.aerror(
                    "stage_failed",
                    stage=stage_name,
                    error=str(e),
                    pipeline=self.name,
                )
                MetricsCollector.record_processing_error(
                    source=self.name,
                    error_type=str(type(e).__name__),
                )
                return None

        total_duration = time.time() - start_time
        await logger.ainfo(
            "pipeline_completed",
            pipeline=self.name,
            duration=round(total_duration, 2),
        )

        return current_data
