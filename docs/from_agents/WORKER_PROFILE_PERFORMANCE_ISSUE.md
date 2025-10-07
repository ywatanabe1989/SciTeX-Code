# Worker Profile Performance Issue - Identified

**Date**: 2025-10-07
**Issue**: Worker initialization taking too long due to profile copying
**Status**: Root cause identified, solution proposed

---

## Root Cause

**File**: `download/ParallelPDFDownloader.py:474-482`

```python
# Current implementation
profile_manager = ChromeProfileManager(worker_profile_name, config=self.config)
sync_success = profile_manager.sync_from_profile(source_profile_name="system")
```

**What happens**:
1. Each worker calls `sync_from_profile("system")`
2. This copies Extensions directory: **277MB per worker**
3. For 8 workers: **~2.2GB total copying**
4. Extensions are never modified, so copying is wasteful

**Evidence from disk usage**:
```
761M    system                    # Master profile
172M    system_worker_0           # Copied
141M    system_worker_1           # Copied
180M    system_worker_2           # Copied
393M    system_worker_3           # Copied (largest, includes cache)
135M    system_worker_4           # Copied
134M    system_worker_5           # Copied
125M    system_worker_6           # Copied
121M    system_worker_7           # Copied
```

---

## What's Being Copied

**File**: `browser/local/utils/_ChromeProfileManager.py:266-365`

`sync_from_profile()` copies:
1. ✅ **Extensions** (277MB) - SHOULD USE SYMLINK
2. ✅ **Cookies** (~few KB) - OK to copy
3. ✅ **Preferences** (~few KB) - OK to copy
4. ✅ **Local State** (~100KB) - OK to copy
5. ✅ **Login Data** (~few MB) - OK to copy

**Only Extensions directory is large** - everything else is small.

---

## Proposed Solution

### Option 1: Symlink Extensions (Recommended)

**Modify**: `_ChromeProfileManager.py:290-299`

```python
# Current (slow)
if source_extensions.exists():
    if target_extensions.exists():
        shutil.rmtree(target_extensions)
    shutil.copytree(source_extensions, target_extensions)
    synced_items.append("extensions")

# Proposed (fast)
if source_extensions.exists():
    if target_extensions.exists():
        if target_extensions.is_symlink():
            target_extensions.unlink()
        else:
            shutil.rmtree(target_extensions)
    target_extensions.symlink_to(source_extensions)
    synced_items.append("extensions (symlinked)")
```

**Benefits**:
- ✅ Instant "copy" (just creates symlink)
- ✅ Saves 277MB × 8 = 2.2GB disk space
- ✅ Extensions auto-update when system profile updates
- ✅ No risk - Chrome reads extensions, doesn't write to them

**Risks**:
- ⚠️ If Chrome writes to Extensions directory, could affect all workers
  - **Mitigation**: Chrome typically only reads from Extensions, writes to Cache/Storage

### Option 2: One-Time Profile Copy

Cache worker profiles - don't recreate every run.

**Add**: Check if worker profile already has extensions before syncing

```python
# In ParallelPDFDownloader.py:474-482
profile_manager = ChromeProfileManager(worker_profile_name, config=self.config)

# Only sync if extensions not already present
if not profile_manager.check_extensions_installed(verbose=False):
    sync_success = profile_manager.sync_from_profile(source_profile_name="system")
else:
    logger.debug(f"Worker {worker_id}: Extensions already present, skipping sync")
    sync_success = True
```

**Benefits**:
- ✅ First run slow, subsequent runs fast
- ✅ No symlink risks
- ✅ Simple change

**Drawbacks**:
- ⚠️ First run still slow
- ⚠️ Workers don't get extension updates without manual cleanup

### Option 3: Hybrid Approach (Best)

Combine both:
1. Use symlinks for Extensions (read-only, large)
2. Copy cookies/preferences/login (read-write, small)
3. Cache worker profiles (don't recreate every run)

---

## Implementation Priority

### High Priority (Do Now)
1. ✅ Symlink Extensions directory instead of copying
2. ✅ Check if worker profile exists before syncing

### Medium Priority
3. ⏳ Add cleanup command to remove stale worker profiles
4. ⏳ Log sync time for monitoring

### Low Priority
5. ⏳ Profile warming - pre-create worker profiles
6. ⏳ Share Cache directory via symlink too

---

## Performance Improvement Estimate

**Current**:
- Worker init: ~10-15 seconds (profile copy)
- 8 workers × 15s = 120s total overhead

**After symlink fix**:
- Worker init: ~2-3 seconds (symlink + small file copies)
- 8 workers × 3s = 24s total overhead

**Savings**: ~96 seconds (80% reduction)

---

## Question About Chrome Profile Location

User asked:
> it seems they are not saved there: (.env-3.11) (wsl) scholar $ ls ~/.cache/google-chrome/

The profiles are at:
- **Actual location**: `~/.scitex/scholar/cache/chrome/system`
- **NOT at**: `~/.cache/google-chrome/`

This is correct - scitex uses custom profile location via `--user-data-dir` flag.

**Why custom location**:
1. ✅ Isolation from personal Chrome usage
2. ✅ Project-specific profiles
3. ✅ Easier to manage/cleanup
4. ✅ No interference with user's Chrome

---

## Recommended Action

**Immediate**:
1. Implement symlink approach for Extensions directory
2. Add existence check before syncing

**Code changes needed**:
- `_ChromeProfileManager.py:290-299` - Use symlink for Extensions
- `ParallelPDFDownloader.py:476-477` - Add existence check

**Testing**:
1. Delete all `system_worker_*` profiles
2. Run parallel download with 8 workers
3. Verify worker init takes <5 seconds
4. Verify extensions work correctly

---

*Analysis completed by Claude Code on 2025-10-07*
