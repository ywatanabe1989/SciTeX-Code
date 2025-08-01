#!/usr/bin/env python3
"""Demonstration of improved exponential backoff settings for DOI resolvers."""

# Current settings in different sources:

# CrossRef (good):
# wait_exponential(multiplier=1, min=2, max=30)
# - Starts at 2 seconds
# - Multiplies by 1 each retry (2, 4, 8, 16, 30)
# - Caps at 30 seconds

# Semantic Scholar (too conservative):
# wait_exponential(multiplier=2, min=10, max=120)
# - Starts at 10 seconds (too high!)
# - Multiplies by 2 each retry (10, 20, 40, 80, 120)
# - Caps at 120 seconds

# RECOMMENDED improved settings:

# For general API calls (fast recovery):
GENERAL_BACKOFF = {
    "multiplier": 1,
    "min": 1,      # Start at 1 second
    "max": 30      # Cap at 30 seconds
}
# Sequence: 1, 2, 4, 8, 16, 30, 30, ...

# For rate-limited APIs (gradual recovery):
RATE_LIMITED_BACKOFF = {
    "multiplier": 1.5,
    "min": 2,      # Start at 2 seconds
    "max": 60      # Cap at 60 seconds
}
# Sequence: 2, 3, 4.5, 6.75, 10.1, 15.2, 22.8, 34.2, 51.3, 60, ...

# For aggressive rate limits (e.g., 429 errors):
AGGRESSIVE_BACKOFF = {
    "multiplier": 2,
    "min": 3,      # Start at 3 seconds
    "max": 120     # Cap at 120 seconds
}
# Sequence: 3, 6, 12, 24, 48, 96, 120, ...

# Example implementation:
example_code = '''
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
    before_sleep
)
import logging

logger = logging.getLogger(__name__)

def log_retry_attempt(retry_state):
    """Log retry attempts with wait time."""
    wait_time = retry_state.next_action.sleep
    attempt = retry_state.attempt_number
    logger.info(f"Retry attempt {attempt}, waiting {wait_time:.1f} seconds...")

# For normal API calls
@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=1, max=30),
    retry=retry_if_exception_type(requests.RequestException),
    before_sleep=log_retry_attempt
)
def fetch_with_normal_backoff(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

# For rate-limited APIs
@retry(
    stop=stop_after_attempt(7),
    wait=wait_exponential(multiplier=1.5, min=2, max=60),
    retry=retry_if_exception(is_rate_limited),
    before_sleep=log_retry_attempt
)
def fetch_with_rate_limit_backoff(url):
    response = requests.get(url)
    if response.status_code == 429:
        raise RateLimitError("API rate limit exceeded")
    response.raise_for_status()
    return response.json()
'''

print("Improved Exponential Backoff Settings")
print("="*50)
print("\n1. General API calls (fast recovery):")
print(f"   wait_exponential(**{GENERAL_BACKOFF})")
print("   Sequence: 1s, 2s, 4s, 8s, 16s, 30s (cap)")

print("\n2. Rate-limited APIs (gradual recovery):")
print(f"   wait_exponential(**{RATE_LIMITED_BACKOFF})")
print("   Sequence: 2s, 3s, 4.5s, 6.8s, 10.1s, 15.2s, ...")

print("\n3. Aggressive rate limits (slow recovery):")
print(f"   wait_exponential(**{AGGRESSIVE_BACKOFF})")
print("   Sequence: 3s, 6s, 12s, 24s, 48s, 96s, 120s (cap)")

print("\n" + "="*50)
print("Benefits:")
print("- Faster initial retries (1-3s instead of 10s)")
print("- Gradual backoff prevents hammering APIs")
print("- Reasonable caps prevent excessive waiting")
print("- Configurable based on API strictness")

# Calculate total wait times
import math

def calculate_wait_sequence(multiplier, min_val, max_val, attempts=7):
    """Calculate the wait sequence for exponential backoff."""
    waits = []
    for i in range(attempts):
        wait = min(min_val * (multiplier ** i), max_val)
        waits.append(wait)
    return waits

print("\n" + "="*50)
print("Wait time comparison for 7 attempts:")
print("-"*50)

scenarios = [
    ("Current Semantic Scholar", 2, 10, 120),
    ("Improved General", 1, 1, 30),
    ("Improved Rate-Limited", 1.5, 2, 60),
]

for name, mult, min_v, max_v in scenarios:
    waits = calculate_wait_sequence(mult, min_v, max_v)
    total = sum(waits)
    print(f"\n{name}:")
    print(f"  Waits: {[f'{w:.1f}s' for w in waits]}")
    print(f"  Total wait time: {total:.1f} seconds ({total/60:.1f} minutes)")