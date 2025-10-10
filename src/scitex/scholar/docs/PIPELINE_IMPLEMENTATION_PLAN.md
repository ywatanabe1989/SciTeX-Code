# Scholar Pipeline Implementation Plan

**Date**: 2025-10-11
**Goal**: Implement storage-first sequential pipeline for paper processing

## Architecture Summary

```
Single Paper: Sequential Stages
├─ Stage 1: Resolve DOI (if title provided)
├─ Stage 2: Load/Create from storage (check metadata)
├─ Stage 3: Find URLs (check → process → save)
├─ Stage 4: Download PDF (check → process → save)
└─ Stage 5: Update symlinks (organize in project)

Multiple Papers: Parallel Papers, Sequential Stages per Paper
├─ Paper 1: [Stage 1 → Stage 2 → Stage 3 → Stage 4 → Stage 5]  ┐
├─ Paper 2: [Stage 1 → Stage 2 → Stage 3 → Stage 4 → Stage 5]  ├─ Parallel (semaphore)
├─ Paper 3: [Stage 1 → Stage 2 → Stage 3 → Stage 4 → Stage 5]  ┘
└─ Paper 4: [waits for slot...]
```

## Storage Structure

```
~/.scitex/scholar/library/
├── MASTER/
│   └── {8-DIGIT-ID}/
│       ├── metadata.json          # Paper.model_dump() format
│       └── *.pdf                  # Downloaded PDFs
└── {project}/
    ├── info/
    │   ├── bibtex/
    │   └── project_metadata.json
    └── PDF-{status}_CC-{citations}_IF-{impact}_{year}_{author}_{journal} → ../MASTER/{ID}
```

---

## Phase 1: Storage Helpers in LibraryManager

**Goal**: Add simple helper methods to check and load paper data from storage

### 1.1: Add `has_metadata(paper_id: str) -> bool`

**File**: `src/scitex/scholar/storage/_LibraryManager.py`

**Implementation**:
```python
def has_metadata(self, paper_id: str) -> bool:
    """Check if metadata.json exists for paper.

    Args:
        paper_id: 8-digit paper ID

    Returns:
        True if metadata.json exists, False otherwise
    """
    metadata_file = self.library_master_dir / paper_id / "metadata.json"
    return metadata_file.exists()
```

**Test**:
```python
# Should return True for existing papers
manager = LibraryManager()
assert manager.has_metadata("2D162FB7") == True
assert manager.has_metadata("XXXXXXXX") == False
```

---

### 1.2: Add `has_urls(paper_id: str) -> bool`

**File**: `src/scitex/scholar/storage/_LibraryManager.py`

**Implementation**:
```python
def has_urls(self, paper_id: str) -> bool:
    """Check if PDF URLs exist in metadata.

    Args:
        paper_id: 8-digit paper ID

    Returns:
        True if metadata has PDF URLs, False otherwise
    """
    if not self.has_metadata(paper_id):
        return False

    metadata_file = self.library_master_dir / paper_id / "metadata.json"
    try:
        with open(metadata_file, 'r') as f:
            data = json.load(f)

        # Check nested structure: metadata.url.pdfs
        urls = data.get("metadata", {}).get("url", {}).get("pdfs", [])
        return len(urls) > 0
    except Exception:
        return False
```

**Test**:
```python
# Check if existing papers have URLs
manager = LibraryManager()
has_urls = manager.has_urls("2D162FB7")
print(f"Paper 2D162FB7 has URLs: {has_urls}")
```

---

### 1.3: Add `has_pdf(paper_id: str) -> bool`

**File**: `src/scitex/scholar/storage/_LibraryManager.py`

**Implementation**:
```python
def has_pdf(self, paper_id: str) -> bool:
    """Check if PDF file exists in storage.

    Args:
        paper_id: 8-digit paper ID

    Returns:
        True if any PDF file exists, False otherwise
    """
    paper_dir = self.library_master_dir / paper_id
    if not paper_dir.exists():
        return False

    # Check for any PDF files
    pdf_files = list(paper_dir.glob("*.pdf"))
    return len(pdf_files) > 0
```

**Test**:
```python
# Check PDF existence
manager = LibraryManager()
has_pdf = manager.has_pdf("2D162FB7")
print(f"Paper 2D162FB7 has PDF: {has_pdf}")
```

---

### 1.4: Add `load_paper_from_id(paper_id: str) -> Optional[Paper]`

**File**: `src/scitex/scholar/storage/_LibraryManager.py`

**Implementation**:
```python
def load_paper_from_id(self, paper_id: str) -> Optional["Paper"]:
    """Load Paper object from storage by ID.

    Args:
        paper_id: 8-digit paper ID

    Returns:
        Paper object if found, None otherwise
    """
    from scitex.scholar.core.Paper import Paper

    metadata_file = self.library_master_dir / paper_id / "metadata.json"

    if not metadata_file.exists():
        return None

    try:
        with open(metadata_file, 'r') as f:
            data = json.load(f)

        # Use Paper.from_dict() which handles Pydantic validation
        paper = Paper.from_dict(data)
        return paper

    except Exception as e:
        logger.error(f"Failed to load paper {paper_id}: {e}")
        return None
```

**Test**:
```python
# Load existing paper
manager = LibraryManager()
paper = manager.load_paper_from_id("2D162FB7")
if paper:
    print(f"Loaded: {paper.metadata.basic.title}")
    print(f"DOI: {paper.metadata.id.doi}")
```

---

### 1.5: Add `save_paper_incremental(paper_id: str, paper: Paper)`

**File**: `src/scitex/scholar/storage/_LibraryManager.py`

**Implementation**:
```python
def save_paper_incremental(self, paper_id: str, paper: "Paper") -> None:
    """Save Paper object to storage (incremental update).

    This saves the complete Paper object to metadata.json,
    preserving existing data and updating with new fields.

    Args:
        paper_id: 8-digit paper ID
        paper: Paper object to save
    """
    storage_path = self.library_master_dir / paper_id
    storage_path.mkdir(parents=True, exist_ok=True)

    metadata_file = storage_path / "metadata.json"

    # Load existing metadata if it exists
    existing_data = {}
    if metadata_file.exists():
        try:
            with open(metadata_file, 'r') as f:
                existing_data = json.load(f)
        except Exception:
            pass

    # Get new data from Paper object
    new_data = paper.model_dump()

    # Merge: new data takes precedence for non-None values
    # (This preserves existing data while updating with new info)
    merged_data = self._merge_metadata(existing_data, new_data)

    # Update timestamps
    if "container" not in merged_data:
        merged_data["container"] = {}
    merged_data["container"]["updated_at"] = datetime.now().isoformat()

    # Save to file
    with open(metadata_file, 'w') as f:
        json.dump(merged_data, f, indent=2, ensure_ascii=False)

    logger.debug(f"Saved paper {paper_id} to storage")

def _merge_metadata(self, existing: Dict, new: Dict) -> Dict:
    """Recursively merge metadata dicts, preferring new non-None values."""
    result = existing.copy()

    for key, new_value in new.items():
        if key not in result:
            result[key] = new_value
        elif new_value is None:
            # Keep existing value if new is None
            pass
        elif isinstance(new_value, dict) and isinstance(result[key], dict):
            # Recursively merge nested dicts
            result[key] = self._merge_metadata(result[key], new_value)
        elif isinstance(new_value, list) and len(new_value) > 0:
            # Update lists if new list is not empty
            result[key] = new_value
        elif new_value:
            # Update with new non-empty value
            result[key] = new_value

    return result
```

**Test**:
```python
# Update paper metadata incrementally
from scitex.scholar.core.Paper import Paper

manager = LibraryManager()
paper = manager.load_paper_from_id("2D162FB7")

# Add URL
paper.metadata.url.pdfs.append({
    "url": "https://example.com/test.pdf",
    "source": "test"
})

# Save back
manager.save_paper_incremental("2D162FB7", paper)

# Verify
reloaded = manager.load_paper_from_id("2D162FB7")
assert len(reloaded.metadata.url.pdfs) > 0
```

---

### 1.6: Test Phase 1 Helpers

**File**: `.dev/test_phase1_storage_helpers.py`

```python
#!/usr/bin/env python3
"""Test Phase 1 storage helpers with existing neurovista data."""

from scitex.scholar.storage import LibraryManager
from scitex.scholar.core.Paper import Paper

def test_phase1_helpers():
    """Test all Phase 1 storage helper methods."""

    manager = LibraryManager()

    # Test with existing paper
    test_id = "2D162FB7"

    # Test 1: has_metadata
    print(f"\n1. Testing has_metadata('{test_id}')...")
    has_meta = manager.has_metadata(test_id)
    print(f"   Result: {has_meta}")
    assert has_meta == True, "Should have metadata"

    # Test 2: has_urls
    print(f"\n2. Testing has_urls('{test_id}')...")
    has_urls = manager.has_urls(test_id)
    print(f"   Result: {has_urls}")

    # Test 3: has_pdf
    print(f"\n3. Testing has_pdf('{test_id}')...")
    has_pdf = manager.has_pdf(test_id)
    print(f"   Result: {has_pdf}")

    # Test 4: load_paper_from_id
    print(f"\n4. Testing load_paper_from_id('{test_id}')...")
    paper = manager.load_paper_from_id(test_id)
    assert paper is not None, "Should load paper"
    print(f"   Title: {paper.metadata.basic.title[:50]}...")
    print(f"   DOI: {paper.metadata.id.doi}")
    print(f"   URLs: {len(paper.metadata.url.pdfs)}")

    # Test 5: save_paper_incremental
    print(f"\n5. Testing save_paper_incremental('{test_id}')...")
    # Add test URL
    test_url = {"url": "https://test.com/test.pdf", "source": "test"}
    if test_url not in paper.metadata.url.pdfs:
        paper.metadata.url.pdfs.append(test_url)

    manager.save_paper_incremental(test_id, paper)

    # Verify save
    reloaded = manager.load_paper_from_id(test_id)
    assert any(u.get("url") == test_url["url"] for u in reloaded.metadata.url.pdfs)
    print(f"   Saved and reloaded successfully")

    print("\n✅ All Phase 1 tests passed!")

if __name__ == "__main__":
    test_phase1_helpers()
```

**Run test**:
```bash
cd /home/ywatanabe/proj/scitex_repo
python .dev/test_phase1_storage_helpers.py
```

---

## Phase 2: Single Paper Pipeline in Scholar

**Goal**: Implement `process_paper()` method with sequential stages

**File**: `src/scitex/scholar/core/Scholar.py`

**Implementation**: See detailed design in architecture summary

**Key Features**:
- Input: `title` OR `doi`
- Sequential stages with storage checks
- Idempotent (can run multiple times safely)
- Clear progress logging

---

## Phase 3: Parallel Papers Pipeline in Scholar

**Goal**: Implement `process_papers()` method for Papers collection

**File**: `src/scitex/scholar/core/Scholar.py`

**Implementation**: Uses semaphore for controlled parallelism

**Key Features**:
- Input: `Papers` collection or `List[str]`
- Parallel papers with `max_concurrent` control
- Each paper runs through complete sequential pipeline
- Progress tracking for all papers

---

## Progress Tracking

- [x] Architecture designed
- [x] Storage structure analyzed
- [ ] Phase 1.1: has_metadata
- [ ] Phase 1.2: has_urls
- [ ] Phase 1.3: has_pdf
- [ ] Phase 1.4: load_paper_from_id
- [ ] Phase 1.5: save_paper_incremental
- [ ] Phase 1.6: Test Phase 1
- [ ] Phase 2: process_paper
- [ ] Phase 3: process_papers

---

## Notes

- Start with Phase 1 only
- Test each helper method individually
- Use existing neurovista data for testing
- Don't refactor LibraryManager yet (too risky)
- Focus on adding, not changing existing code

---

## Next Steps

After completing Phase 1:
1. Review Phase 1 implementation
2. Test with real data
3. Get user approval
4. Move to Phase 2

**Current Focus**: Phase 1.1 - Implement `has_metadata()`
