#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-24 14:25:00 (ywatanabe)"
# File: tests/scitex/scholar/conftest.py
# ----------------------------------------

"""
Shared test fixtures and utilities for Scholar module tests.

Provides common mock configurations and helpers.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock
from scitex.scholar import ScholarConfig


def create_mock_scholar_config(tmp_path):
    """
    Create a complete mock ScholarConfig with all required attributes.
    
    This helper ensures all tests use consistent mock configurations
    and prevents AttributeError for missing mock attributes.
    
    Args:
        tmp_path: pytest tmp_path fixture for temporary directories
        
    Returns:
        Mock object with all ScholarConfig attributes
    """
    mock_config = Mock(spec=ScholarConfig)
    
    # Core paths
    mock_config.workspace_dir = tmp_path
    mock_config.pdf_dir = str(tmp_path / "pdfs")
    
    # API Keys
    mock_config.semantic_scholar_api_key = None
    mock_config.crossref_api_key = None
    
    # Email addresses
    mock_config.pubmed_email = "test@example.com"
    mock_config.crossref_email = "test@example.com"
    
    # Feature toggles
    mock_config.enable_auto_enrich = True
    mock_config.use_impact_factor_package = False
    mock_config.enable_auto_download = False
    mock_config.acknowledge_scihub_ethical_usage = True
    
    # Search configuration
    mock_config.default_search_sources = ["pubmed", "arxiv"]
    mock_config.default_search_limit = 20
    
    # PDF management
    mock_config.enable_pdf_extraction = True
    
    # Performance settings
    mock_config.max_parallel_requests = 3
    mock_config.request_timeout = 30
    mock_config.cache_size = 1000
    mock_config.google_scholar_timeout = 10
    
    # Advanced settings
    mock_config.verify_ssl = True
    mock_config.debug_mode = False
    
    # OpenAthens authentication
    mock_config.openathens_enabled = False
    mock_config.openathens_org_id = None
    mock_config.openathens_idp_url = None
    mock_config.openathens_email = None
    mock_config.openathens_username = None
    mock_config.openathens_password = None
    mock_config.openathens_institution_name = None
    
    # Lean Library settings
    mock_config.use_lean_library = True
    mock_config.lean_library_browser_profile = None
    
    # HTTP settings
    mock_config.user_agent = "SciTeX-Scholar/1.0"
    
    return mock_config


@pytest.fixture
def mock_scholar_config(tmp_path):
    """
    Pytest fixture for creating mock ScholarConfig.
    
    Usage in tests:
        def test_something(mock_scholar_config):
            config = mock_scholar_config
            # Use config in test...
    """
    return create_mock_scholar_config(tmp_path)


# Additional shared fixtures can be added here

# EOF