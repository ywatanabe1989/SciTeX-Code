# Step-by-Step Migration Plan

## Migration Priority Order (Safest First)

### Priority 1: Configuration Files (SAFEST) ✅
- `default_config.yaml` → `config/settings/`
- `*.json` config files → `config/settings/`
- **Risk**: None - just copying, originals remain

### Priority 2: Static Cache Data (SAFE) 
- `doi_cache/` → `cache/doi_cache/` (copy, keep original)
- `semantic_index_test/` → `cache/semantic_index/`
- **Risk**: Very low - cache can be regenerated

### Priority 3: Session Data (MODERATE)
- `user_*/` → `cache/sessions/`
- `openathens_sessions/` → `cache/sessions/openathens/`
- `sso_sessions/` → `cache/sessions/sso/`
- **Risk**: Moderate - affects authentication

### Priority 4: Browser Profiles (MODERATE)
- Consolidate `chrome_profile*` → `profiles/chrome/`
- **Risk**: Moderate - affects browser functionality

### Priority 5: Screenshots (LOW RISK)
- `screenshots/` → `workspace/screenshots/`
- **Risk**: Low - just debugging data

### Priority 6: PDFs (HIGHEST RISK - DO LAST)
- `pdfs/` → `library/storage/` with proper paper IDs
- **Risk**: High - critical user data

## Migration Strategy: Copy First, Link Later

1. **Copy** data to new location
2. **Test** functionality with new location
3. **Create symlink** from old to new (or vice versa)
4. **Verify** everything still works
5. **Only then** consider removing originals (with backup)