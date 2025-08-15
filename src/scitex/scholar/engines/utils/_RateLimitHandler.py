#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-11 05:25:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/metadata/doi/utils/_RateLimitHandler.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/metadata/doi/utils/_RateLimitHandler.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Centralized rate limit detection and management for DOI resolution.

This module provides intelligent rate limit handling with exponential backoff,
engine rotation, and automatic resume capabilities.
"""

import asyncio
import json
import time
from collections import deque
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

import requests

from scitex import logging
from scitex.scholar.config import ScholarConfig

logger = logging.getLogger(__name__)


class RateLimitType(Enum):
    """Types of rate limit scenarios."""

    HTTP_429 = "http_429"
    API_QUOTA_EXCEEDED = "api_quota_exceeded"
    CONNECTION_TIMEOUT = "connection_timeout"
    SERVER_ERROR = "server_error"
    UNKNOWN = "unknown"


@dataclass
class RateLimitInfo:
    """Information about a rate limit encounter."""

    engine: str
    limit_type: RateLimitType
    wait_time: float
    retry_after: Optional[int] = None
    error_message: Optional[str] = None
    timestamp: float = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


@dataclass
class EngineState:
    """Track the state of an individual API engine."""

    name: str
    is_rate_limited: bool = False
    rate_limit_until: float = 0.0
    consecutive_failures: int = 0
    last_success: float = 0.0
    total_requests: int = 0
    successful_requests: int = 0
    base_delay: float = 0.1
    current_delay: float = 0.1
    max_delay: float = 900.0  # 15 minutes
    adaptive_delay: float = 0.1  # Adaptive delay based on success rates
    rate_limited_count: int = 0  # Count of rate limiting incidents

    @property
    def success_rate(self) -> float:
        """Calculate success rate for this engine."""
        if self.total_requests == 0:
            return 0.0
        return self.successful_requests / self.total_requests

    @property
    def is_available(self) -> bool:
        """Check if engine is available (not rate limited)."""
        if not self.is_rate_limited:
            return True
        return time.time() >= self.rate_limit_until


class RateLimitHandler:
    """Centralized rate limit detection and backoff management."""

    # Common rate limit detection patterns
    RATE_LIMIT_PATTERNS = {
        "crossref": {
            "http_codes": [429, 503],
            "error_messages": [
                "rate limit",
                "too many requests",
                "quota exceeded",
            ],
            "headers": ["retry-after", "x-ratelimit-remaining"],
        },
        "pubmed": {
            "http_codes": [429, 414, 503],
            "error_messages": ["rate limit", "too many requests", "overload"],
            "headers": ["retry-after"],
        },
        "semantic_scholar": {
            "http_codes": [429, 503],
            "error_messages": ["rate limit", "too many requests"],
            "headers": ["retry-after", "x-ratelimit-remaining"],
        },
        "openalex": {
            "http_codes": [429, 503],
            "error_messages": ["rate limit", "too many requests"],
            "headers": ["retry-after"],
        },
        "arxiv": {
            "http_codes": [429, 503],
            "error_messages": ["rate limit", "too many requests"],
            "headers": ["retry-after"],
        },
    }

    def __init__(
        self,
        config: Optional[ScholarConfig] = None,
        # default_delay: Optional[float] = None,
        # enable_adaptive_delay: Optinoal[bool] = None,
        # max_retries: Optional[bool] = None,
    ):
        # def __init__(self, state_file: Optional[Path] = None):
        """Initialize rate limit handler.

        Args:
            state_file: Path to save/load engine states
        """
        self.config = config or ScholarConfig()
        self.state_file = (
            self.config.get_workspace_dir() / "logs" / "rate_limit_state.json"
        )
        self.engine_states: Dict[str, EngineState] = {}
        self.global_backoff = 0.0
        self.last_request_time = 0.0
        self.rate_limit_history: List[RateLimitInfo] = []

        # Adaptive rate limiting tracking
        self.recent_rates = deque(
            maxlen=50
        )  # Track recent success/failure rates
        self.global_adaptive_delay = 0.1  # Global adaptive delay

        # Load existing state if available
        self._load_state()

    def _load_state(self):
        """Load engine states from file."""
        if not self.state_file or not self.state_file.exists():
            return

        try:
            with open(self.state_file, "r") as f:
                data = json.load(f)

            for engine_data in data.get("engines", []):
                engine_state = EngineState(**engine_data)
                self.engine_states[engine_state.name] = engine_state

            self.global_backoff = data.get("global_backoff", 0.0)
            self.global_adaptive_delay = data.get("global_adaptive_delay", 0.1)

            # Clean expired rate limits
            current_time = time.time()
            for state in self.engine_states.values():
                if state.rate_limit_until < current_time:
                    state.is_rate_limited = False
                    state.rate_limit_until = 0.0

            logger.info(
                f"Loaded rate limit states for {len(self.engine_states)} engines"
            )

        except Exception as e:
            logger.warning(f"Failed to load rate limit state: {e}")

    def _save_state(self):
        """Save engine states to file."""
        if not self.state_file:
            return

        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)

            data = {
                "engines": [
                    asdict(state) for state in self.engine_states.values()
                ],
                "global_backoff": self.global_backoff,
                "global_adaptive_delay": self.global_adaptive_delay,
                "last_updated": datetime.now().isoformat(),
            }

            with open(self.state_file, "w") as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            logger.error(f"Failed to save rate limit state: {e}")

    def get_engine_state(self, engine: str) -> EngineState:
        """Get or create engine state."""
        if engine not in self.engine_states:
            self.engine_states[engine] = EngineState(name=engine)
        return self.engine_states[engine]

    def detect_rate_limit(
        self,
        engine: str,
        response: Optional[requests.Response] = None,
        exception: Optional[Exception] = None,
    ) -> Optional[RateLimitInfo]:
        """Detect if a response or exception indicates a rate limit.

        Args:
            engine: API engine name
            response: HTTP response object
            exception: Exception that occurred

        Returns:
            RateLimitInfo if rate limit detected, None otherwise
        """
        patterns = self.RATE_LIMIT_PATTERNS.get(engine.lower(), {})

        # Check HTTP response for rate limits
        if response is not None:
            # Check status codes
            if response.status_code in patterns.get("http_codes", []):
                retry_after = self._extract_retry_after(response)
                wait_time = retry_after or self._calculate_backoff_time(engine)

                return RateLimitInfo(
                    engine=engine,
                    limit_type=RateLimitType.HTTP_429,
                    wait_time=wait_time,
                    retry_after=retry_after,
                    error_message=f"HTTP {response.status_code}",
                )

            # Check for rate limit indicators in response text
            response_text = (
                response.text.lower() if hasattr(response, "text") else ""
            )
            for error_msg in patterns.get("error_messages", []):
                if error_msg in response_text:
                    wait_time = self._calculate_backoff_time(engine)
                    return RateLimitInfo(
                        engine=engine,
                        limit_type=RateLimitType.API_QUOTA_EXCEEDED,
                        wait_time=wait_time,
                        error_message=error_msg,
                    )

        # Check exceptions for rate limit indicators
        if exception is not None:
            error_str = str(exception).lower()

            # Check for timeout errors (might indicate rate limiting)
            if any(
                keyword in error_str
                for keyword in ["timeout", "connection", "read timeout"]
            ):
                wait_time = self._calculate_backoff_time(
                    engine, base_multiplier=2.0
                )
                return RateLimitInfo(
                    engine=engine,
                    limit_type=RateLimitType.CONNECTION_TIMEOUT,
                    wait_time=wait_time,
                    error_message=str(exception),
                )

            # Check for rate limit messages in exception
            for error_msg in patterns.get("error_messages", []):
                if error_msg in error_str:
                    wait_time = self._calculate_backoff_time(engine)
                    return RateLimitInfo(
                        engine=engine,
                        limit_type=RateLimitType.API_QUOTA_EXCEEDED,
                        wait_time=wait_time,
                        error_message=str(exception),
                    )

        return None

    def _extract_retry_after(
        self, response: requests.Response
    ) -> Optional[int]:
        """Extract retry-after header value."""
        retry_after_header = response.headers.get(
            "Retry-After"
        ) or response.headers.get("retry-after")
        if retry_after_header:
            try:
                return int(retry_after_header)
            except ValueError:
                # Might be HTTP date format, ignore for now
                pass
        return None

    def _calculate_backoff_time(
        self, engine: str, base_multiplier: float = 1.0
    ) -> float:
        """Calculate exponential backoff time for a engine."""
        state = self.get_engine_state(engine)

        # Start with base delay
        base_delay = state.base_delay * base_multiplier

        # Apply exponential backoff based on consecutive failures
        backoff_multiplier = min(
            2**state.consecutive_failures, 64
        )  # Cap at 64x
        calculated_delay = base_delay * backoff_multiplier

        # Add jitter to prevent thundering herd
        import random

        jitter = random.uniform(0.8, 1.2)
        final_delay = min(calculated_delay * jitter, state.max_delay)

        return final_delay

    def record_rate_limit(self, rate_limit_info: RateLimitInfo):
        """Record a rate limit encounter and update engine state."""
        engine = rate_limit_info.engine
        state = self.get_engine_state(engine)

        # Update engine state
        state.is_rate_limited = True
        state.rate_limit_until = time.time() + rate_limit_info.wait_time
        state.consecutive_failures += 1
        state.current_delay = rate_limit_info.wait_time
        state.total_requests += 1
        state.rate_limited_count += (
            1  # Track rate limiting incidents for adaptive logic
        )

        # Add to history
        self.rate_limit_history.append(rate_limit_info)

        # Keep only recent history (last 100 entries)
        if len(self.rate_limit_history) > 100:
            self.rate_limit_history = self.rate_limit_history[-100:]

        # Update global backoff if multiple engines are rate limited
        active_rate_limits = sum(
            1 for s in self.engine_states.values() if s.is_rate_limited
        )
        if active_rate_limits >= 2:
            self.global_backoff = max(
                self.global_backoff, rate_limit_info.wait_time * 0.5
            )

        logger.warning(
            f"Rate limit detected for {engine}: {rate_limit_info.limit_type.value} "
            f"(wait {rate_limit_info.wait_time:.1f}s)"
        )

        self._save_state()

    def record_success(self, engine: str):
        """Record a successful request for a engine."""
        state = self.get_engine_state(engine)

        # Update success metrics
        state.successful_requests += 1
        state.total_requests += 1
        state.last_success = time.time()

        # Reset failure tracking on success
        if state.consecutive_failures > 0:
            state.consecutive_failures = max(0, state.consecutive_failures - 1)
            state.current_delay = max(
                state.base_delay, state.current_delay * 0.8
            )

        # Clear rate limit if expired
        if state.is_rate_limited and time.time() >= state.rate_limit_until:
            state.is_rate_limited = False
            state.rate_limit_until = 0.0
            logger.info(f"Rate limit cleared for {engine}")

        self._save_state()

    def record_failure(
        self, engine: str, exception: Optional[Exception] = None
    ):
        """Record a failed request for a engine."""
        state = self.get_engine_state(engine)
        state.total_requests += 1

        # Don't increment failures if it's already rate limited
        if not state.is_rate_limited:
            state.consecutive_failures += 1

        self._save_state()

    def get_available_engines(self, engines: List[str]) -> List[str]:
        """Get list of currently available (non-rate-limited) engines."""
        available = []

        for engine in engines:
            state = self.get_engine_state(engine)
            if state.is_available:
                available.append(engine)

        # Sort by success rate and recent performance
        def sort_key(engine: str) -> tuple:
            state = self.get_engine_state(engine)
            # Primary: success rate, Secondary: recency of last success
            return (-state.success_rate, -state.last_success)

        available.sort(key=sort_key)
        return available

    def get_next_available_time(self, engines: List[str]) -> float:
        """Get the earliest time when any engine will be available."""
        earliest_time = float("inf")
        current_time = time.time()

        for engine in engines:
            state = self.get_engine_state(engine)
            if state.is_rate_limited:
                earliest_time = min(earliest_time, state.rate_limit_until)
            else:
                return current_time  # At least one engine is available now

        return earliest_time if earliest_time != float("inf") else current_time

    def should_use_global_backoff(self) -> bool:
        """Check if global backoff should be applied."""
        if self.global_backoff <= 0:
            return False

        # Apply global backoff if multiple engines are rate limited
        rate_limited_count = sum(
            1 for s in self.engine_states.values() if s.is_rate_limited
        )
        return rate_limited_count >= 2

    def get_wait_time_for_engine(self, engine: str) -> float:
        """Get wait time before next request to a specific engine."""
        state = self.get_engine_state(engine)

        if not state.is_rate_limited:
            # Apply adaptive delay for politeness and performance optimization
            elapsed_since_last = time.time() - self.last_request_time

            # Get adaptive delay for this engine
            adaptive_delay = self.get_adaptive_delay(engine)
            min_delay = max(state.base_delay, adaptive_delay)

            if elapsed_since_last < min_delay:
                return min_delay - elapsed_since_last
            return 0.0

        return max(0.0, state.rate_limit_until - time.time())

    async def wait_with_countdown_async(
        self, wait_time: float, engine: str = "API"
    ):
        """Wait for specified time with countdown display."""
        if wait_time <= 0:
            return

        logger.info(f"Rate limited - waiting {wait_time:.1f}s for {engine}")

        # Show countdown for waits longer than 10 seconds
        if wait_time > 10:
            start_time = time.time()
            while True:
                elapsed = time.time() - start_time
                remaining = wait_time - elapsed

                if remaining <= 0:
                    break

                # Format remaining time
                if remaining >= 3600:
                    time_str = f"{remaining/3600:.1f}h"
                elif remaining >= 60:
                    time_str = f"{remaining/60:.1f}m"
                else:
                    time_str = f"{remaining:.0f}s"

                print(
                    f"\rWaiting for {engine}: {time_str} remaining...",
                    end="",
                    flush=True,
                )

                # Update every second for long waits, more frequently for short ones
                update_interval = min(1.0, remaining / 10)
                await asyncio.sleep(update_interval)

            print()  # New line after countdown
        else:
            await asyncio.sleep(wait_time)

        self.last_request_time = time.time()

    def get_statistics(self) -> Dict[str, any]:
        """Get rate limiting statistics."""
        stats = {
            "total_engines": len(self.engine_states),
            "rate_limited_engines": sum(
                1 for s in self.engine_states.values() if s.is_rate_limited
            ),
            "global_backoff_active": self.should_use_global_backoff(),
            "global_adaptive_delay": self.global_adaptive_delay,
            "recent_success_rate": self.calculate_recent_success_rate(),
            "recent_requests_tracked": len(self.recent_rates),
            "engines": {},
        }

        for name, state in self.engine_states.items():
            stats["engines"][name] = {
                "success_rate": state.success_rate,
                "total_requests": state.total_requests,
                "consecutive_failures": state.consecutive_failures,
                "is_rate_limited": state.is_rate_limited,
                "rate_limit_until": state.rate_limit_until,
                "current_delay": state.current_delay,
                "adaptive_delay": state.adaptive_delay,
                "rate_limited_count": state.rate_limited_count,
            }

        # Recent rate limit history
        recent_limits = [
            {
                "engine": rl.engine,
                "type": rl.limit_type.value,
                "wait_time": rl.wait_time,
                "timestamp": rl.timestamp,
            }
            for rl in self.rate_limit_history[-10:]  # Last 10 rate limits
        ]
        stats["recent_rate_limits"] = recent_limits

        return stats

    def calculate_recent_success_rate(self) -> float:
        """Calculate success rate from recent attempts."""
        if not self.recent_rates:
            return 0.5  # Default to neutral success rate

        successes = sum(1 for success in self.recent_rates if success)
        return successes / len(self.recent_rates)

    def get_adaptive_delay(self, engine: Optional[str] = None) -> float:
        """Get adaptive delay based on recent success/failure patterns.

        Args:
            engine: Specific engine to get delay for, or None for global

        Returns:
            Adaptive delay in seconds
        """
        if engine:
            state = self.get_engine_state(engine)

            # Increase delay if engine has been rate limited frequently
            if state.rate_limited_count > 5:
                state.adaptive_delay = min(2.0, state.adaptive_delay * 1.5)
                logger.debug(
                    f"Increased adaptive delay for {engine}: {state.adaptive_delay:.3f}s"
                )

            # Decrease delay if engine is performing well
            elif state.total_requests > 10 and state.success_rate > 0.8:
                recent_success_rate = self.calculate_recent_success_rate()
                if recent_success_rate > 0.8:
                    state.adaptive_delay = max(
                        0.05, state.adaptive_delay * 0.9
                    )
                    logger.debug(
                        f"Decreased adaptive delay for {engine}: {state.adaptive_delay:.3f}s"
                    )

            return state.adaptive_delay
        else:
            # Global adaptive delay logic
            recent_success_rate = self.calculate_recent_success_rate()
            total_rate_limited = sum(
                state.rate_limited_count
                for state in self.engine_states.values()
            )

            # Increase global delay if getting rate limited frequently
            if total_rate_limited > 5:
                self.global_adaptive_delay = min(
                    2.0, self.global_adaptive_delay * 1.5
                )
                logger.debug(
                    f"Increased global adaptive delay: {self.global_adaptive_delay:.3f}s"
                )

            # Decrease global delay if success rate is high
            elif recent_success_rate > 0.8 and len(self.recent_rates) > 10:
                self.global_adaptive_delay = max(
                    0.05, self.global_adaptive_delay * 0.9
                )
                logger.debug(
                    f"Decreased global adaptive delay: {self.global_adaptive_delay:.3f}s"
                )

            return self.global_adaptive_delay

    def record_request_outcome(self, engine: str, success: bool):
        """Record the outcome of a request for adaptive rate limiting.

        Args:
            engine: The engine that made the request
            success: Whether the request was successful
        """
        # Add to recent rates for global tracking
        self.recent_rates.append(success)

        # Update engine-specific stats
        # state = self.get_engine_state(engine)
        if success:
            self.record_success(engine)
        else:
            # Don't double-count failures if already recorded
            pass


if __name__ == "__main__":

    async def test_rate_limit_handler_async():
        """Test the rate limit handler functionality."""
        print("=" * 60)
        print("RateLimitHandler Test")
        print("=" * 60)

        # Create handler with temporary state file
        state_file = Path("/tmp/test_rate_limit_state.json")
        handler = RateLimitHandler(state_file=state_file)

        print("✅ Handler initialized")

        # Test rate limit detection
        print("\n1. Testing rate limit detection:")

        # Simulate HTTP 429 response
        class MockResponse:
            def __init__(self, status_code, headers=None, text=""):
                self.status_code = status_code
                self.headers = headers or {}
                self.text = text

        response_429 = MockResponse(429, {"Retry-After": "60"})
        rate_limit = handler.detect_rate_limit(
            "crossref", response=response_429
        )

        if rate_limit:
            print(
                f"   ✅ Detected rate limit: {rate_limit.limit_type.value} (wait {rate_limit.wait_time}s)"
            )
            handler.record_rate_limit(rate_limit)
        else:
            print("   ❌ Failed to detect rate limit")

        # Test engine availability
        print("\n2. Testing engine availability:")
        available_engines = handler.get_available_engines(
            ["crossref", "pubmed", "semantic_scholar"]
        )
        print(f"   Available engines: {available_engines}")

        rate_limited_engines = [
            s
            for s in ["crossref", "pubmed", "semantic_scholar"]
            if not handler.get_engine_state(s).is_available
        ]
        print(f"   Rate limited engines: {rate_limited_engines}")

        # Test wait time calculation
        print("\n3. Testing wait time calculation:")
        wait_time = handler.get_wait_time_for_engine("crossref")
        print(f"   Wait time for crossref: {wait_time:.1f}s")

        # Test success recording
        print("\n4. Testing success recording:")
        handler.record_success("pubmed")
        pubmed_state = handler.get_engine_state("pubmed")
        print(f"   PubMed success rate: {pubmed_state.success_rate:.2f}")

        # Test countdown (short duration for demo)
        print("\n5. Testing countdown display:")
        await handler.wait_with_countdown_async(3.0, "test")

        # Show statistics
        print("\n6. Statistics:")
        stats = handler.get_statistics()
        print(f"   Total engines: {stats['total_engines']}")
        print(f"   Rate limited: {stats['rate_limited_engines']}")
        print(f"   Global backoff: {stats['global_backoff_active']}")

        # Show engine details
        for engine, details in stats["engines"].items():
            print(
                f"   {engine}: success_rate={details['success_rate']:.2f}, "
                f"rate_limited={details['is_rate_limited']}"
            )

        print("\n✅ RateLimitHandler test completed!")

        # Cleanup
        if state_file.exists():
            state_file.unlink()

    asyncio.run(test_rate_limit_handler_async())

# python -m scitex.scholar.doi._RateLimitHandler

# EOF
