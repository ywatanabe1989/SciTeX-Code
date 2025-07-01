# Scholar Module Test Coverage Improvement Plan

**Date**: 2025-07-02  
**Current Coverage**: 18% (4/22 modules tested)  
**Target Coverage**: 80%+ 

## Priority 1: Critical Integration Tests (Week 1)

### 1. test_semantic_scholar_client.py
```python
# Test API client functionality
- test_search_papers_basic()
- test_search_with_pagination()
- test_rate_limiting()
- test_error_handling()
- test_paper_info_retrieval()
```

### 2. test_paper_acquisition.py
```python
# Test main acquisition interface
- test_search_multiple_sources()
- test_ai_enhancement()
- test_full_literature_review()
- test_download_papers_pdfs()
- test_source_fallback()
```

### 3. test_journal_metrics.py
```python
# Test impact factor functionality
- test_lookup_journal_metrics()
- test_fuzzy_matching()
- test_custom_database()
- test_enhance_bibliography()
```

### 4. test_vector_search_engine.py
```python
# Test semantic search
- test_build_index()
- test_search_similarity()
- test_persistence()
- test_update_index()
```

## Priority 2: Core Functionality Tests (Week 2)

### 5. test_paper_enrichment.py
```python
# Test enrichment service
- test_enrich_single_paper()
- test_enrich_batch()
- test_async_enrichment()
- test_pdf_download_integration()
```

### 6. test_local_search.py
```python
# Test local file search
- test_index_directory()
- test_search_papers()
- test_file_watching()
- test_cache_management()
```

### 7. test_scientific_pdf_parser.py
```python
# Test PDF parsing
- test_extract_metadata()
- test_parse_sections()
- test_extract_references()
- test_handle_corrupted_pdf()
```

### 8. test_text_processor.py
```python
# Test text processing
- test_clean_text()
- test_extract_keywords()
- test_sentence_segmentation()
- test_unicode_handling()
```

## Priority 3: Advanced Features (Week 3)

### 9. test_literature_review_workflow.py
```python
# Test AI-powered workflows
- test_generate_search_queries()
- test_filter_papers()
- test_generate_summary()
- test_find_knowledge_gaps()
```

### 10. test_mcp_server.py & test_mcp_vector_server.py
```python
# Test MCP functionality
- test_server_initialization()
- test_tool_registration()
- test_search_operations()
- test_concurrent_requests()
```

### 11. test_document_indexer.py
```python
# Test document indexing
- test_index_papers()
- test_update_index()
- test_search_index()
- test_index_persistence()
```

## Test Implementation Guidelines

### 1. Use Mocking for External APIs
```python
@patch('aiohttp.ClientSession')
async def test_semantic_scholar_api(mock_session):
    # Mock API responses
    pass
```

### 2. Create Test Fixtures
```python
@pytest.fixture
def sample_paper():
    return Paper(
        title="Test Paper",
        authors=["Test Author"],
        # ...
    )
```

### 3. Test Both Success and Failure Cases
```python
async def test_api_error_handling():
    # Test 429 rate limit
    # Test 500 server error
    # Test network timeout
```

### 4. Integration Tests
```python
async def test_full_workflow():
    # Search → Enrich → Download → Index
```

## Success Metrics

- [ ] 80%+ module coverage
- [ ] All critical paths tested
- [ ] Mock all external dependencies
- [ ] < 30s total test runtime
- [ ] CI/CD integration ready

## Next Steps

1. Start with Priority 1 tests (most critical)
2. Use existing test patterns from test_paper.py
3. Add GitHub Actions for automated testing
4. Document any discovered bugs

With these tests implemented, the scholar module will be production-ready with confidence in all features.