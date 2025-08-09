#!/usr/bin/env python3
"""Smart retry logic for Scholar PDF downloads.

This module implements intelligent retry strategies with:
- Exponential backoff
- Transient error detection
- Strategy rotation on failure
- Adaptive timeout adjustment
"""

import asyncio
import time
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Type, Union
import logging

from scitex.errors import PDFDownloadError, ScholarError


logger = logging.getLogger(__name__)


# Transient errors that should trigger retry
TRANSIENT_ERROR_CODES = {
    408,  # Request Timeout
    429,  # Too Many Requests
    500,  # Internal Server Error
    502,  # Bad Gateway
    503,  # Service Unavailable
    504,  # Gateway Timeout
    520,  # Cloudflare Unknown Error
    521,  # Cloudflare Web Server Is Down
    522,  # Cloudflare Connection Timed Out
    524,  # Cloudflare A Timeout Occurred
}

TRANSIENT_ERROR_MESSAGES = {
    "timeout",
    "timed out",
    "connection reset",
    "connection refused",
    "temporary failure",
    "service unavailable",
    "rate limit",
    "too many requests",
}


class RetryConfig:
    """Configuration for retry behavior."""
    
    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: float = 0.1,
        timeout_multiplier: float = 1.5,
        strategy_rotation: bool = True,
    ):
        """Initialize retry configuration.
        
        Args:
            max_attempts: Maximum number of retry attempts
            initial_delay: Initial delay between retries (seconds)
            max_delay: Maximum delay between retries (seconds)
            exponential_base: Base for exponential backoff
            jitter: Random jitter factor (0-1)
            timeout_multiplier: Multiply timeout on each retry
            strategy_rotation: Try different download strategies on retry
        """
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.timeout_multiplier = timeout_multiplier
        self.strategy_rotation = strategy_rotation


def is_transient_error(error: Exception) -> bool:
    """Determine if an error is transient and should be retried.
    
    Args:
        error: The exception to check
        
    Returns:
        True if the error is transient
    """
    # Check error type
    if isinstance(error, asyncio.TimeoutError):
        return True
    
    # Check HTTP status codes
    if hasattr(error, 'status') and error.status in TRANSIENT_ERROR_CODES:
        return True
    
    # Check error messages
    error_msg = str(error).lower()
    if any(msg in error_msg for msg in TRANSIENT_ERROR_MESSAGES):
        return True
    
    # Check specific error types
    if isinstance(error, (ConnectionError, TimeoutError)):
        return True
    
    return False


def calculate_delay(
    attempt: int,
    config: RetryConfig
) -> float:
    """Calculate delay before next retry with exponential backoff and jitter.
    
    Args:
        attempt: Current attempt number (0-based)
        config: Retry configuration
        
    Returns:
        Delay in seconds
    """
    # Exponential backoff
    delay = config.initial_delay * (config.exponential_base ** attempt)
    
    # Cap at max delay
    delay = min(delay, config.max_delay)
    
    # Add jitter to prevent thundering herd
    import random
    jitter_amount = delay * config.jitter * (2 * random.random() - 1)
    delay += jitter_amount
    
    return max(0, delay)


def retry_async(
    config: Optional[RetryConfig] = None,
    on_retry: Optional[Callable[[int, Exception], None]] = None,
    retry_exceptions: Optional[Tuple[Type[Exception], ...]] = None,
):
    """Decorator for async functions with smart retry logic.
    
    Args:
        config: Retry configuration
        on_retry: Callback function called on each retry
        retry_exceptions: Specific exceptions to retry on
    """
    if config is None:
        config = RetryConfig()
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            last_error = None
            
            for attempt in range(config.max_attempts):
                try:
                    # Adjust timeout if specified
                    if attempt > 0 and 'timeout' in kwargs:
                        kwargs['timeout'] = int(
                            kwargs['timeout'] * config.timeout_multiplier
                        )
                    
                    # Call the function
                    result = await func(*args, **kwargs)
                    
                    # Success - return result
                    return result
                    
                except Exception as e:
                    last_error = e
                    
                    # Check if we should retry
                    should_retry = False
                    
                    if retry_exceptions:
                        should_retry = isinstance(e, retry_exceptions)
                    else:
                        should_retry = is_transient_error(e)
                    
                    if not should_retry or attempt == config.max_attempts - 1:
                        # Don't retry - re-raise
                        raise
                    
                    # Calculate delay
                    delay = calculate_delay(attempt, config)
                    
                    # Log retry
                    logger.info(
                        f"Retry {attempt + 1}/{config.max_attempts} "
                        f"after {delay:.1f}s for: {type(e).__name__}"
                    )
                    
                    # Call retry callback
                    if on_retry:
                        on_retry(attempt + 1, e)
                    
                    # Wait before retry
                    await asyncio.sleep(delay)
            
            # All attempts failed
            if last_error:
                raise last_error
                
        return wrapper
    return decorator


class StrategyRotator:
    """Rotate through different download strategies on retry."""
    
    def __init__(self, strategies: List[str]):
        """Initialize with list of strategy names."""
        self.strategies = strategies
        self.current_index = 0
        self.failed_strategies: Set[str] = set()
    
    def get_next_strategy(self, failed_strategy: Optional[str] = None) -> Optional[str]:
        """Get next strategy to try.
        
        Args:
            failed_strategy: Strategy that just failed
            
        Returns:
            Next strategy name or None if all failed
        """
        if failed_strategy:
            self.failed_strategies.add(failed_strategy)
        
        # Find next strategy that hasn't failed
        for _ in range(len(self.strategies)):
            strategy = self.strategies[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.strategies)
            
            if strategy not in self.failed_strategies:
                return strategy
        
        # All strategies failed
        return None
    
    def reset(self):
        """Reset for new download attempt."""
        self.current_index = 0
        self.failed_strategies.clear()


class RetryManager:
    """Manage retry logic for PDF downloads."""
    
    def __init__(self, config: Optional[RetryConfig] = None):
        """Initialize retry manager."""
        self.config = config or RetryConfig()
        self.download_attempts: Dict[str, int] = {}
        self.strategy_rotators: Dict[str, StrategyRotator] = {}
    
    async def download_with_retry(
        self,
        identifier: str,
        download_func: Callable,
        strategies: Optional[List[str]] = None,
        **kwargs
    ) -> Tuple[Optional[Any], Dict[str, Any]]:
        """Download with smart retry logic.
        
        Args:
            identifier: DOI or URL
            download_func: Async download function
            strategies: List of strategy names to rotate through
            **kwargs: Arguments for download function
            
        Returns:
            Tuple of (result, metadata)
        """
        # Initialize strategy rotator if needed
        if strategies and self.config.strategy_rotation:
            if identifier not in self.strategy_rotators:
                self.strategy_rotators[identifier] = StrategyRotator(strategies)
            rotator = self.strategy_rotators[identifier]
        else:
            rotator = None
        
        # Track attempts
        self.download_attempts[identifier] = 0
        
        metadata = {
            'attempts': 0,
            'strategies_tried': [],
            'errors': [],
            'total_time': 0,
        }
        
        start_time = time.time()
        last_error = None
        
        for attempt in range(self.config.max_attempts):
            self.download_attempts[identifier] = attempt + 1
            metadata['attempts'] = attempt + 1
            
            try:
                # Get strategy for this attempt
                if rotator:
                    strategy = rotator.get_next_strategy()
                    if strategy is None:
                        # All strategies failed
                        break
                    kwargs['preferred_strategy'] = strategy
                    metadata['strategies_tried'].append(strategy)
                
                # Adjust timeout
                if attempt > 0 and 'timeout' in kwargs:
                    kwargs['timeout'] = int(
                        kwargs['timeout'] * self.config.timeout_multiplier
                    )
                
                # Attempt download
                result = await download_func(identifier, **kwargs)
                
                # Success
                metadata['total_time'] = time.time() - start_time
                return result, metadata
                
            except Exception as e:
                last_error = e
                metadata['errors'].append({
                    'attempt': attempt + 1,
                    'error': str(e),
                    'type': type(e).__name__,
                    'transient': is_transient_error(e),
                })
                
                # Check if we should retry
                if not is_transient_error(e) or attempt == self.config.max_attempts - 1:
                    break
                
                # Mark strategy as failed if using rotation
                if rotator and 'preferred_strategy' in kwargs:
                    rotator.failed_strategies.add(kwargs['preferred_strategy'])
                
                # Calculate delay
                delay = calculate_delay(attempt, self.config)
                
                logger.info(
                    f"Retry {attempt + 1}/{self.config.max_attempts} "
                    f"for {identifier} after {delay:.1f}s"
                )
                
                # Wait before retry
                await asyncio.sleep(delay)
        
        # All attempts failed
        metadata['total_time'] = time.time() - start_time
        
        if last_error:
            raise PDFDownloadError(
                f"Failed after {metadata['attempts']} attempts: {last_error}",
                identifier=identifier,
                metadata=metadata
            )
        
        return None, metadata