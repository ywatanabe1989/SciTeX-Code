# SciTeX-Scholar Tests

This directory contains comprehensive test suites for all SciTeX-Scholar modules, mirroring the source structure.

## Test Structure

```
tests/
├── scitex_scholar/
│   ├── test_document_indexer.py      # Tests for document indexing functionality
│   ├── test_latex_parser.py          # Tests for LaTeX parsing (in parent tests/)
│   ├── test_literature_review_workflow.py  # Tests for literature review workflow
│   ├── test_mcp_server.py           # Tests for MCP server
│   ├── test_mcp_vector_server.py    # Tests for vector MCP server
│   ├── test_paper_acquisition.py    # Tests for paper acquisition
│   ├── test_scientific_pdf_parser.py # Tests for PDF parsing
│   ├── test_search_engine.py        # Tests for search engine (in parent tests/)
│   ├── test_text_processor.py       # Tests for text processing (in parent tests/)
│   └── test_vector_search_engine.py # Tests for vector search
├── test_latex_parser.py             # LaTeX parser tests
├── test_package_import.py           # Package import tests
├── test_search_engine.py            # Search engine tests
└── test_text_processor.py           # Text processor tests
```

## Running Tests

To run all tests:
```bash
# Using pytest directly
python -m pytest tests/ -v

# Using the test runner script
./run_tests.sh

# Run specific test file
python -m pytest tests/scitex_scholar/test_vector_search_engine.py -v

# Run with coverage
python -m pytest tests/ --cov=scitex_scholar --cov-report=html
```

## Test Categories

### Unit Tests
- Individual component testing with mocked dependencies
- Fast execution, isolated functionality
- Examples: `test_latex_parser.py`, `test_text_processor.py`

### Integration Tests
- Testing component interactions
- Workflow testing
- Examples: `test_literature_review_workflow.py`, `test_mcp_server.py`

### Mock Usage
All tests use extensive mocking to:
- Avoid external API calls
- Simulate file system operations
- Control test data precisely
- Ensure fast, reliable test execution

## Test Patterns

Each test module follows these patterns:

1. **Setup and Teardown**
   ```python
   def setUp(self):
       """Initialize test fixtures."""
       self.component = Component()
   ```

2. **Descriptive Test Names**
   ```python
   def test_search_papers_with_filters_returns_filtered_results(self):
   ```

3. **Arrange-Act-Assert**
   ```python
   # Arrange
   mock_data = create_test_data()
   
   # Act
   result = component.process(mock_data)
   
   # Assert
   self.assertEqual(result.status, 'success')
   ```

4. **Mock External Dependencies**
   ```python
   @patch('scitex_scholar.module.external_service')
   def test_with_mock(self, mock_service):
       mock_service.return_value = expected_data
   ```

## Coverage Goals

- Minimum 80% code coverage
- 100% coverage for critical paths
- All error conditions tested
- Edge cases covered

## Dependencies

Required for running tests:
- unittest (built-in)
- unittest.mock (built-in)
- pytest (optional, for advanced features)
- pytest-cov (optional, for coverage reports)