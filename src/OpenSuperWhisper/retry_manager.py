"""
Retry Manager Module
Manages retry logic for failed chunk processing
"""

import threading
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any

from . import logger


class RetryStrategy(Enum):
    """Retry strategies for different error types"""

    IMMEDIATE = "immediate"  # Retry immediately
    EXPONENTIAL = "exponential"  # Exponential backoff
    FIXED_DELAY = "fixed_delay"  # Fixed delay between retries
    NO_RETRY = "no_retry"  # Don't retry


@dataclass
class RetryConfig:
    """Configuration for retry behavior"""

    max_retries: int = 1  # Maximum number of retries (as per requirements)
    base_delay: float = 5.0  # Base delay in seconds
    max_delay: float = 60.0  # Maximum delay in seconds
    strategy: RetryStrategy = RetryStrategy.FIXED_DELAY


class RetryManager:
    """Manages retry operations for failed chunks"""

    # Error type to retry configuration mapping
    ERROR_RETRY_CONFIG = {
        "Network timeout": RetryConfig(max_retries=1, base_delay=0.0, strategy=RetryStrategy.IMMEDIATE),
        "Connection timed out": RetryConfig(max_retries=1, base_delay=0.0, strategy=RetryStrategy.IMMEDIATE),
        "Rate limit": RetryConfig(max_retries=1, base_delay=60.0, strategy=RetryStrategy.FIXED_DELAY),
        "API rate limit": RetryConfig(max_retries=1, base_delay=60.0, strategy=RetryStrategy.FIXED_DELAY),
        "Network error": RetryConfig(max_retries=1, base_delay=5.0, strategy=RetryStrategy.FIXED_DELAY),
        "Authentication": RetryConfig(max_retries=0, strategy=RetryStrategy.NO_RETRY),
        "API key": RetryConfig(max_retries=0, strategy=RetryStrategy.NO_RETRY),
        "default": RetryConfig(max_retries=1, base_delay=10.0, strategy=RetryStrategy.FIXED_DELAY),
    }

    def __init__(self) -> None:
        """Initialize retry manager"""
        self.retry_queue: list[tuple[int, float]] = []  # (chunk_id, retry_time)
        self.retry_counts: dict[int, int] = {}  # chunk_id -> retry count
        self.retry_lock = threading.Lock()
        self.is_active = True

        logger.logger.info("RetryManager initialized")

    def should_retry(self, chunk_id: int, error: str) -> bool:
        """
        Determine if a chunk should be retried based on error type

        Args:
            chunk_id: Chunk identifier
            error: Error message

        Returns:
            True if should retry, False otherwise
        """
        # Get current retry count
        current_retries = self.retry_counts.get(chunk_id, 0)

        # Get retry configuration for error type
        config = self._get_retry_config(error)

        # Check if retries exhausted
        if current_retries >= config.max_retries:
            logger.logger.info(f"Chunk {chunk_id} exceeded max retries ({config.max_retries})")
            return False

        # Check retry strategy
        if config.strategy == RetryStrategy.NO_RETRY:
            logger.logger.info(f"Chunk {chunk_id} error '{error}' is non-retryable")
            return False

        return True

    def schedule_retry(self, chunk_id: int, error: str) -> float | None:
        """
        Schedule a chunk for retry

        Args:
            chunk_id: Chunk identifier
            error: Error message

        Returns:
            Retry time if scheduled, None otherwise
        """
        if not self.should_retry(chunk_id, error):
            return None

        config = self._get_retry_config(error)
        current_retries = self.retry_counts.get(chunk_id, 0)

        # Calculate delay
        delay = self._calculate_delay(config, current_retries)
        retry_time = time.time() + delay

        # Add to retry queue
        with self.retry_lock:
            self.retry_queue.append((chunk_id, retry_time))
            self.retry_counts[chunk_id] = current_retries + 1

        logger.logger.info(
            f"Scheduled chunk {chunk_id} for retry in {delay:.1f}s "
            f"(attempt {current_retries + 1}/{config.max_retries})"
        )

        return retry_time

    def get_ready_retries(self) -> list[int]:
        """
        Get list of chunks ready for retry

        Returns:
            List of chunk IDs ready for retry
        """
        if not self.is_active:
            return []

        current_time = time.time()
        ready_chunks = []

        with self.retry_lock:
            # Find chunks ready for retry
            remaining_queue = []
            for chunk_id, retry_time in self.retry_queue:
                if retry_time <= current_time:
                    ready_chunks.append(chunk_id)
                else:
                    remaining_queue.append((chunk_id, retry_time))

            self.retry_queue = remaining_queue

        if ready_chunks:
            logger.logger.info(f"Chunks ready for retry: {ready_chunks}")

        return ready_chunks

    def cancel_all_retries(self) -> None:
        """Cancel all pending retries"""
        with self.retry_lock:
            cancelled_count = len(self.retry_queue)
            self.retry_queue.clear()
            self.retry_counts.clear()
            self.is_active = False

        if cancelled_count > 0:
            logger.logger.info(f"Cancelled {cancelled_count} pending retries")

    def remove_chunk(self, chunk_id: int) -> None:
        """Remove a chunk from retry queue (e.g., if successful)"""
        with self.retry_lock:
            self.retry_queue = [(cid, rt) for cid, rt in self.retry_queue if cid != chunk_id]
            if chunk_id in self.retry_counts:
                del self.retry_counts[chunk_id]

    def _get_retry_config(self, error: str) -> RetryConfig:
        """Get retry configuration based on error message"""
        error_lower = error.lower()

        # Check each error pattern
        for pattern, config in self.ERROR_RETRY_CONFIG.items():
            if pattern.lower() in error_lower:
                return config

        # Return default config
        return self.ERROR_RETRY_CONFIG["default"]

    def _calculate_delay(self, config: RetryConfig, retry_count: int) -> float:
        """Calculate retry delay based on strategy"""
        if config.strategy == RetryStrategy.IMMEDIATE:
            return 0.0

        elif config.strategy == RetryStrategy.FIXED_DELAY:
            return config.base_delay

        elif config.strategy == RetryStrategy.EXPONENTIAL:
            # Exponential backoff: base_delay * 2^retry_count
            delay = config.base_delay * (2**retry_count)
            return float(min(delay, config.max_delay))

        return config.base_delay

    def get_retry_status(self) -> dict[str, Any]:
        """Get current retry queue status"""
        with self.retry_lock:
            return {
                "pending_retries": len(self.retry_queue),
                "retry_counts": dict(self.retry_counts),
                "is_active": self.is_active,
                "queue": [(cid, rt - time.time()) for cid, rt in self.retry_queue],
            }
