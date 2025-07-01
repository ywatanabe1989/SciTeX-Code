#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-02 00:20:00 (ywatanabe)"
# File: ./tests/scitex/scholar/test_pdf_downloader.py

"""Test PDF downloader functionality."""

import pytest
import tempfile
import os
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from scitex.scholar import PDFDownloader


def test_pdf_downloader_initialization():
    """Test PDFDownloader initialization."""
    with tempfile.TemporaryDirectory() as tmpdir:
        downloader = PDFDownloader(download_dir=tmpdir)
        assert str(downloader.download_dir) == tmpdir
        assert os.path.exists(tmpdir)


def test_pdf_downloader_default_dir():
    """Test PDFDownloader with default directory."""
    downloader = PDFDownloader()
    assert downloader.download_dir is not None
    assert isinstance(downloader.download_dir, Path)


@patch('aiohttp.ClientSession.get')
def test_download_pdf_success(mock_get):
    """Test successful PDF download."""
    # Mock async response
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.read = AsyncMock(return_value=b'%PDF-1.4 mock pdf content')
    mock_get.return_value.__aenter__.return_value = mock_response
    
    with tempfile.TemporaryDirectory() as tmpdir:
        downloader = PDFDownloader(download_dir=tmpdir)
        
        # Test download
        url = "https://example.com/test.pdf"
        filename = "test_paper.pdf"
        
        result = asyncio.run(downloader.download_from_url(url, filename))
        
        # Check file was created
        expected_path = os.path.join(tmpdir, filename)
        assert str(result) == expected_path
        assert os.path.exists(expected_path)
        
        # Check content
        with open(expected_path, 'rb') as f:
            content = f.read()
        assert content == b'%PDF-1.4 mock pdf content'


@patch('aiohttp.ClientSession.get')
def test_download_pdf_failure(mock_get):
    """Test failed PDF download."""
    # Mock failed response
    mock_response = AsyncMock()
    mock_response.status = 404
    mock_get.return_value.__aenter__.return_value = mock_response
    
    with tempfile.TemporaryDirectory() as tmpdir:
        downloader = PDFDownloader(download_dir=tmpdir)
        
        url = "https://example.com/notfound.pdf"
        filename = "test_paper.pdf"
        
        # Should handle failure gracefully
        result = asyncio.run(downloader.download_from_url(url, filename))
        assert result is None
        
        # File should not exist
        expected_path = os.path.join(tmpdir, filename)
        assert not os.path.exists(expected_path)


if __name__ == "__main__":
    pytest.main([__file__])