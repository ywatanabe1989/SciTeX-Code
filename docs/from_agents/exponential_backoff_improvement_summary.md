# Exponential Backoff Improvement Summary

**Date**: 2025-08-01  
**Issue**: Semantic Scholar DOI resolver had 10-second initial retry delay
**Solution**: Improved exponential backoff settings

## Changes Made

### Semantic Scholar Source (`_SemanticScholarSource.py`)
**Before**:
```python
wait_exponential(multiplier=2, min=10, max=120)
# Sequence: 10s, 20s, 40s, 80s, 120s
# Total for 5 attempts: 270 seconds (4.5 minutes)
```

**After**:
```python
wait_exponential(multiplier=1.5, min=2, max=60)
# Sequence: 2s, 3s, 4.5s, 6.8s, 10.1s, 15.2s, 22.8s, 34.2s, 51.3s, 60s
# Total for 5 attempts: 25.6 seconds (vs 270s before!)
```

## Current Exponential Backoff Settings

| Source | Multiplier | Min | Max | First 5 Retries | Total Wait |
|--------|------------|-----|-----|-----------------|------------|
| CrossRef | 1 | 2s | 30s | 2, 2, 2, 2, 2s | 10s |
| PubMed | 1 | 2s | 30s | 2, 2, 2, 2, 2s | 10s |
| OpenAlex | 1 | 2s | 30s | 2, 2, 2, 2, 2s | 10s |
| Semantic Scholar | 1.5 | 2s | 60s | 2, 3, 4.5, 6.8, 10.1s | 26.4s |

## Benefits

1. **Faster Recovery**: Initial retry after just 2 seconds instead of 10
2. **Progressive Backoff**: Gradually increases wait time to respect rate limits
3. **Reasonable Caps**: Maximum 60 seconds prevents excessive waiting
4. **10x Faster**: Total wait time reduced from 270s to ~26s for 5 retries

## Implementation Details

The exponential backoff formula:
```
wait_time = min(min_delay * (multiplier ^ attempt), max_delay)
```

Where:
- `min_delay`: Starting delay (2 seconds)
- `multiplier`: Growth factor (1.5 for gradual increase)
- `attempt`: Retry attempt number (0, 1, 2, ...)
- `max_delay`: Maximum delay cap (60 seconds)

## Recommendations

1. **General APIs**: Use `multiplier=1, min=1-2, max=30`
2. **Rate-Limited APIs**: Use `multiplier=1.5, min=2, max=60`
3. **Strict APIs**: Use `multiplier=2, min=3, max=120`

The improved settings balance:
- Quick recovery from transient errors
- Respect for API rate limits
- Reasonable total wait times
- Progressive backoff to prevent API hammering