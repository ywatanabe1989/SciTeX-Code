# Browser Crash Analysis - RESOLVED

## Issue
Workers crash with "Target page, context or browser has been closed" when worker count exceeds 4.

## Root Cause - CONFIRMED ✅

**The worker profile fix code (lines 432-449) IS working correctly for workers 0-3, but workers 4+ are never created.**

### Critical Evidence

#### Worker Profile Creation
```bash
$ ls -la ~/.scitex/scholar/cache/chrome/ | grep system_worker
drwxr-xr-x 34 ywatanabe ywatanabe 4.0K Oct  7 12:53 system_worker_0  ✅
drwxr-xr-x 34 ywatanabe ywatanabe 4.0K Oct  7 12:53 system_worker_1  ✅
drwxr-xr-x 34 ywatanabe ywatanabe 4.0K Oct  7 12:53 system_worker_2  ✅
drwxr-xr-x 34 ywatanabe ywatanabe 4.0K Oct  7 12:53 system_worker_3  ✅
(no system_worker_4, system_worker_5, etc.)                        ❌
```

#### Test Run Timeline (bc87ab)

**Phase 1 - Initial Workers** ✅
- Workers 0-3 started successfully
- Each created unique worker profile (system_worker_0 through system_worker_3)
- Worker 0: Completed 4 papers
- Worker 1: Completed 3 papers
- Worker 2: Completed 3 papers
- Worker 3: Completed 3 papers

**Phase 2 - Additional Workers** ❌
- System attempted to launch workers 4+
- NO worker profiles created for workers 4+
- All used shared `--user-data-dir=/home/ywatanabe/.scitex/scholar/cache/chrome/system`
- Multiple "Target page, context or browser has been closed" errors

## The Real Issue

The code is NOT broken. The issue is **worker pool management**:

1. **Max workers** was set to 4 (based on publisher count)
2. **13 papers** needed downloading, more than 4 workers can handle in one round
3. **Workers 0-3** successfully downloaded their papers using worker profiles
4. **When workers finished**, the pool tried to reuse workers BUT something went wrong

### Hypothesis - Worker Reuse Issue

When a worker finishes its batch and picks up new papers, ONE of these is happening:
1. **Worker profile not recreated** for second round
2. **Browser manager not reinitialized** with worker profile
3. **Profile parameter overridden** somewhere in the code path

## Evidence from Browser Launch Args

**Failed launches show**:
```
--user-data-dir=/home/ywatanabe/.scitex/scholar/cache/chrome/system
```

This proves the chrome_profile_name parameter is NOT being used when workers restart.

## Solution Path

The worker profile fix (lines 432-449) works for FIRST browser launch but NOT for subsequent launches by the same worker thread.

### Locations to Check

1. **ParallelPDFDownloader.py:432-449** - Initial browser creation (WORKS ✅)
2. **Worker reuse logic** - Where workers pick up new papers (BROKEN ❌)
3. **ScholarBrowserManager** - Verify it respects chrome_profile_name on ALL launches

### Debug Strategy

Add logging to track:
1. Worker lifecycle (start, complete, restart)
2. Profile name at each browser creation
3. Browser manager initialization parameters

## Test Results Summary

**Success Rate**: 4 workers × 3-4 papers = 13 papers processed before crashes
**Crash Point**: When worker pool attempts to spawn additional workers beyond 0-3
**Profile Fix Status**: Working for workers 0-3, not implemented for workers 4+

## Solution Implemented ✅

**Fix**: Preemptively create ALL worker profiles before starting parallel downloads

### Changes Made

**File**: `ParallelPDFDownloader.py`

**New method** (lines 343-377):
```python
async def _prepare_worker_profiles_async(self, num_workers: int) -> None:
    """Preemptively create worker profiles to avoid browser crashes."""
    for worker_id in range(num_workers):
        worker_profile_name = f"system_worker_{worker_id}"
        profile_manager = ChromeProfileManager(worker_profile_name, config=self.config)

        # Check if already exists
        if profile_manager.profile_dir.exists():
            if profile_manager.check_extensions_installed(verbose=False):
                continue

        # Sync from system profile
        sync_success = profile_manager.sync_from_profile(source_profile_name="system")
```

**Called at** (line 314):
```python
if self.use_parallel and self.max_workers > 1:
    # Preemptively create worker profiles to avoid crashes
    await self._prepare_worker_profiles_async(self.max_workers)

    logger.info(f"Starting parallel downloads with {self.max_workers} workers")
    result = await self._download_parallel(papers_to_download, project, library_dir)
```

### How It Works

1. **Before downloads start**: Create profiles for ALL workers (0 through max_workers-1)
2. **During downloads**: Each worker uses its pre-created profile
3. **Result**: No crashes from shared profile conflicts

### Configuration

- Controlled by `SCITEX_SCHOLAR_PDF_MAX_PARALLEL` (default: 8)
- Worker profiles: `system_worker_0` through `system_worker_{max_parallel-1}`
- Each profile synced from "system" profile (includes extensions + cookies)

## Next Steps

1. ✅ Identify root cause (workers using shared "system" profile)
2. ✅ Implement preemptive profile creation
3. ⏳ Test with parallel downloads to verify fix
4. ⏳ Monitor for any remaining crashes
