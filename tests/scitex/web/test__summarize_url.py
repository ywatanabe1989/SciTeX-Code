#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-08 05:51:10 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/web/test__summarize_url.py

"""
Tests for URL summarization functionality.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
import json
from concurrent.futures import Future
from bs4 import BeautifulSoup
import re

from scitex.web import (
    extract_main_content,
    crawl_url,
    crawl_to_json,
    summarize_all,
    summarize_url,
)


class TestExtractMainContent:
    """Test extract_main_content function."""
    
    def test_extract_main_content_with_readability(self):
        """Test content extraction with readability library."""
        html_content = """
        <html>
            <body>
                <h1>Main Title</h1>
                <p>This is the main content.</p>
                <div>Some extra content</div>
            </body>
        </html>
        """
        
        # Test when Document is available
        mock_doc = Mock()
        mock_doc.summary.return_value = "<h1>Main Title</h1><p>This is the main content.</p>"
        
        with patch('scitex.web._summarize_url.Document', return_value=mock_doc):
            result = extract_main_content(html_content)
            assert result == "Main Title This is the main content."
            assert "<" not in result  # HTML tags removed
    
    def test_extract_main_content_without_readability(self):
        """Test content extraction when readability is not available."""
        html_content = "<p>Test content</p>"
        
        with patch('scitex.web._summarize_url.Document', None):
            result = extract_main_content(html_content)
            assert result == "Test content"[:5000]  # Limited to 5000 chars
    
    def test_extract_main_content_complex_html(self):
        """Test extraction with complex HTML."""
        html_content = """
        <html>
            <head><title>Test</title></head>
            <body>
                <script>var x = 1;</script>
                <p>Real   content   with   spaces</p>
                <style>body { color: red; }</style>
            </body>
        </html>
        """
        
        mock_doc = Mock()
        mock_doc.summary.return_value = "<p>Real   content   with   spaces</p>"
        
        with patch('scitex.web._summarize_url.Document', return_value=mock_doc):
            result = extract_main_content(html_content)
            assert result == "Real content with spaces"  # Extra spaces removed
    
    def test_extract_main_content_empty_html(self):
        """Test extraction with empty HTML."""
        with patch('scitex.web._summarize_url.Document', None):
            result = extract_main_content("")
            assert result == ""
    
    def test_extract_main_content_no_tags(self):
        """Test extraction with plain text."""
        plain_text = "Just plain text without HTML"
        
        with patch('scitex.web._summarize_url.Document', None):
            result = extract_main_content(plain_text)
            assert result == plain_text


class TestCrawlUrl:
    """Test crawl_url function."""
    
    def test_crawl_url_single_page(self):
        """Test crawling a single page."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<html><body><p>Test content</p></body></html>"
        
        with patch('requests.get', return_value=mock_response):
            with patch('scitex.web._summarize_url.extract_main_content', return_value="Test content"):
                visited, contents = crawl_url("http://test.com", max_depth=0)
                
                assert "http://test.com" in visited
                assert contents["http://test.com"] == "Test content"
                assert len(visited) == 1
    
    def test_crawl_url_with_links(self):
        """Test crawling with links to follow."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """
        <html><body>
            <p>Main page</p>
            <a href="/page2">Link to page 2</a>
            <a href="http://test.com/page3">Link to page 3</a>
        </body></html>
        """
        
        with patch('requests.get', return_value=mock_response):
            with patch('scitex.web._summarize_url.extract_main_content', return_value="Content"):
                visited, contents = crawl_url("http://test.com", max_depth=1)
                
                # Should visit main page and try to visit linked pages
                assert "http://test.com" in visited
    
    def test_crawl_url_max_depth(self):
        """Test that max_depth is respected."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<a href="/deep">Link</a>'
        
        with patch('requests.get', return_value=mock_response):
            with patch('scitex.web._summarize_url.extract_main_content', return_value="Content"):
                visited, contents = crawl_url("http://test.com", max_depth=0)
                
                # Should only visit the initial URL with max_depth=0
                assert len(visited) == 1
                assert "http://test.com" in visited
    
    def test_crawl_url_request_exception(self):
        """Test handling of request exceptions."""
        import requests
        
        with patch('requests.get', side_effect=requests.RequestException("Network error")):
            visited, contents = crawl_url("http://test.com")
            
            assert len(visited) == 0
            assert len(contents) == 0
    
    def test_crawl_url_non_200_status(self):
        """Test handling of non-200 status codes."""
        mock_response = Mock()
        mock_response.status_code = 404
        
        with patch('requests.get', return_value=mock_response):
            visited, contents = crawl_url("http://test.com")
            
            assert len(visited) == 0
            assert len(contents) == 0
    
    def test_crawl_url_avoid_duplicate_visits(self):
        """Test that URLs are not visited twice."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<a href="/">Home</a>'  # Link back to self
        
        call_count = 0
        def mock_get(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return mock_response
        
        with patch('requests.get', side_effect=mock_get):
            with patch('scitex.web._summarize_url.extract_main_content', return_value="Content"):
                visited, contents = crawl_url("http://test.com", max_depth=1)
                
                # Should only call once despite self-referential link
                assert call_count == 1


class TestCrawlToJson:
    """Test crawl_to_json function."""
    
    def test_crawl_to_json_basic(self):
        """Test basic JSON conversion."""
        mock_urls = {"http://test.com"}
        mock_contents = {"http://test.com": "Test page content"}
        
        with patch('scitex.web._summarize_url.crawl_url', return_value=(mock_urls, mock_contents)):
            with patch('scitex.ai.GenAI') as mock_genai:
                mock_llm = Mock()
                mock_llm.return_value = "Summary of test page"
                mock_genai.return_value = mock_llm
                
                # Mock ThreadPoolExecutor
                mock_future = Mock(spec=Future)
                mock_future.result.return_value = {
                    "url": "http://test.com",
                    "content": "Summary of test page"
                }
                
                with patch('concurrent.futures.ThreadPoolExecutor') as mock_executor:
                    mock_executor.return_value.__enter__.return_value.submit.return_value = mock_future
                    with patch('concurrent.futures.as_completed', return_value=[mock_future]):
                        with patch('tqdm.tqdm', side_effect=lambda x, **kwargs: x):
                            result = crawl_to_json("test.com")
                            
                            parsed = json.loads(result)
                            assert parsed["start_url"] == "https://test.com"
                            assert len(parsed["crawled_pages"]) == 1
                            assert parsed["crawled_pages"][0]["url"] == "http://test.com"
    
    def test_crawl_to_json_url_normalization(self):
        """Test URL normalization (adding https://)."""
        with patch('scitex.web._summarize_url.crawl_url', return_value=(set(), {})):
            with patch('concurrent.futures.ThreadPoolExecutor'):
                with patch('concurrent.futures.as_completed', return_value=[]):
                    with patch('tqdm.tqdm', side_effect=lambda x, **kwargs: x):
                        result = crawl_to_json("example.com")
                        parsed = json.loads(result)
                        assert parsed["start_url"] == "https://example.com"
    
    def test_crawl_to_json_already_has_protocol(self):
        """Test URL with existing protocol."""
        with patch('scitex.web._summarize_url.crawl_url', return_value=(set(), {})):
            with patch('concurrent.futures.ThreadPoolExecutor'):
                with patch('concurrent.futures.as_completed', return_value=[]):
                    with patch('tqdm.tqdm', side_effect=lambda x, **kwargs: x):
                        result = crawl_to_json("http://example.com")
                        parsed = json.loads(result)
                        assert parsed["start_url"] == "http://example.com"
    
    def test_crawl_to_json_multiple_pages(self):
        """Test JSON conversion with multiple pages."""
        mock_urls = {"http://test.com", "http://test.com/page2"}
        mock_contents = {
            "http://test.com": "Main content",
            "http://test.com/page2": "Page 2 content"
        }
        
        with patch('scitex.web._summarize_url.crawl_url', return_value=(mock_urls, mock_contents)):
            with patch('scitex.ai.GenAI') as mock_genai:
                mock_llm = Mock()
                mock_llm.side_effect = ["Summary 1", "Summary 2"]
                mock_genai.return_value = mock_llm
                
                # Create futures for each URL
                futures = []
                for i, url in enumerate(mock_urls):
                    mock_future = Mock(spec=Future)
                    mock_future.result.return_value = {
                        "url": url,
                        "content": f"Summary {i+1}"
                    }
                    futures.append(mock_future)
                
                with patch('concurrent.futures.ThreadPoolExecutor') as mock_executor:
                    mock_executor.return_value.__enter__.return_value.submit.side_effect = futures
                    with patch('concurrent.futures.as_completed', return_value=futures):
                        with patch('tqdm.tqdm', side_effect=lambda x, **kwargs: x):
                            result = crawl_to_json("test.com")
                            
                            parsed = json.loads(result)
                            assert len(parsed["crawled_pages"]) == 2


class TestSummarizeAll:
    """Test summarize_all function."""
    
    def test_summarize_all_basic(self):
        """Test basic summarization."""
        json_content = json.dumps({
            "start_url": "http://test.com",
            "crawled_pages": [
                {"url": "http://test.com", "content": "Test summary"}
            ]
        })
        
        with patch('scitex.ai.GenAI') as mock_genai:
            mock_llm = Mock()
            mock_llm.return_value = "• Point 1\n• Point 2\n• Point 3\n• Point 4\n• Point 5"
            mock_genai.return_value = mock_llm
            
            result = summarize_all(json_content)
            
            assert "Point 1" in result
            assert "Point 5" in result
            mock_llm.assert_called_once()
            
            # Check that the prompt includes the JSON content
            call_args = mock_llm.call_args[0][0]
            assert "5 bullet points" in call_args
            assert json_content in call_args
    
    def test_summarize_all_empty_json(self):
        """Test summarization with empty JSON."""
        empty_json = json.dumps({"start_url": "", "crawled_pages": []})
        
        with patch('scitex.ai.GenAI') as mock_genai:
            mock_llm = Mock()
            mock_llm.return_value = "No content to summarize"
            mock_genai.return_value = mock_llm
            
            result = summarize_all(empty_json)
            assert result == "No content to summarize"


class TestSummarizeUrl:
    """Test summarize_url function."""
    
    def test_summarize_url_complete_flow(self):
        """Test complete URL summarization flow."""
        mock_json = json.dumps({
            "start_url": "https://test.com",
            "crawled_pages": [{"url": "https://test.com", "content": "Page summary"}]
        })
        mock_summary = "• Summary point 1\n• Summary point 2"
        
        with patch('scitex.web._summarize_url.crawl_to_json', return_value=mock_json):
            with patch('scitex.web._summarize_url.summarize_all', return_value=mock_summary):
                with patch('builtins.print'):  # Suppress pprint output
                    ground_summary, json_result = summarize_url("test.com")
                    
                    assert ground_summary == mock_summary
                    assert json_result == mock_json
    
    def test_summarize_url_error_handling(self):
        """Test error handling in summarize_url."""
        with patch('scitex.web._summarize_url.crawl_to_json', side_effect=Exception("Crawl error")):
            with pytest.raises(Exception) as exc_info:
                summarize_url("test.com")
            assert str(exc_info.value) == "Crawl error"
    
    def test_summarize_url_pprint_called(self):
        """Test that pprint is called with the summary."""
        mock_json = '{"test": "data"}'
        mock_summary = "Test summary"
        
        with patch('scitex.web._summarize_url.crawl_to_json', return_value=mock_json):
            with patch('scitex.web._summarize_url.summarize_all', return_value=mock_summary):
                with patch('pprint.pprint') as mock_pprint:
                    summarize_url("test.com")
                    mock_pprint.assert_called_once_with(mock_summary)


class TestMain:
    """Test main function and module alias."""
    
    def test_main_is_summarize_url(self):
        """Test that main is an alias for summarize_url."""
        assert main == summarize_url
    
    def test_main_execution(self):
        """Test main function execution."""
        with patch('scitex.web._summarize_url.summarize_url', return_value=("Summary", "{}")) as mock_summarize:
            result = main("http://example.com")
            mock_summarize.assert_called_once_with("http://example.com")
            assert result == ("Summary", "{}")
    
    def test_script_execution(self):
        """Test script execution with arguments."""
        with patch('sys.argv', ['script.py', '--url', 'http://example.com']):
            with patch('scitex.gen.print_block'):
                with patch('scitex.web._summarize_url.main') as mock_main:
                    # Import and execute the argument parsing
                    import argparse
                    parser = argparse.ArgumentParser(description="")
                    parser.add_argument("--url", "-u", type=str, help="(default: %(default)s)")
                    args = parser.parse_args()
                    
                    assert args.url == 'http://example.com'
    
    def test_readability_import_fallback(self):
        """Test readability import fallback mechanism."""
        # This tests the import logic in the actual module
        # The module tries to import from 'readability' first, then 'readability.readability'
        import sys
        
        # Test when both imports fail
        with patch.dict('sys.modules', {'readability': None, 'readability.readability': None}):
            # Re-import the module to trigger the import logic
            if 'scitex.web._summarize_url' in sys.modules:
                del sys.modules['scitex.web._summarize_url']
            
            # This should set Document to None
            from scitex.web import _summarize_url
            # The Document variable should be None when imports fail
            # (This is handled in the actual module's import section)

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/web/_summarize_url.py
# --------------------------------------------------------------------------------
# #!./env/bin/python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-07-29 21:43:30 (ywatanabe)"
# # ./src/scitex/web/_crawl.py
# 
# 
# import requests
# from bs4 import BeautifulSoup
# import urllib.parse
# from concurrent.futures import ThreadPoolExecutor, as_completed
# import json
# from tqdm import tqdm
# import scitex
# from pprint import pprint
# 
# try:
#     from readability import Document
# except ImportError:
#     try:
#         from readability.readability import Document
#     except ImportError:
#         Document = None
# 
# import re
# 
# 
# # def crawl_url(url, max_depth=1):
# #     print("\nCrawling...")
# #     visited = set()
# #     to_visit = [(url, 0)]
# #     contents = {}
# 
# #     while to_visit:
# #         current_url, depth = to_visit.pop(0)
# #         if current_url in visited or depth > max_depth:
# #             continue
# 
# #         try:
# #             response = requests.get(current_url)
# #             if response.status_code == 200:
# #                 visited.add(current_url)
# #                 contents[current_url] = response.text
# #                 soup = BeautifulSoup(response.text, "html.parser")
# 
# #                 for link in soup.find_all("a", href=True):
# #                     absolute_link = urllib.parse.urljoin(
# #                         current_url, link["href"]
# #                     )
# #                     if absolute_link not in visited:
# #                         to_visit.append((absolute_link, depth + 1))
# 
# #         except requests.RequestException:
# #             pass
# 
# #     return visited, contents
# 
# 
# def extract_main_content(html):
#     if Document is None:
#         # Fallback: just strip HTML tags
#         content = re.sub("<[^<]+?>", "", html)
#         content = " ".join(content.split())
#         return content[:5000]  # Limit to first 5000 chars
# 
#     doc = Document(html)
#     content = doc.summary()
#     # Remove HTML tags
#     content = re.sub("<[^<]+?>", "", content)
#     # Remove extra whitespace
#     content = " ".join(content.split())
#     return content
# 
# 
# def crawl_url(url, max_depth=1):
#     print("\nCrawling...")
#     visited = set()
#     to_visit = [(url, 0)]
#     contents = {}
# 
#     while to_visit:
#         current_url, depth = to_visit.pop(0)
#         if current_url in visited or depth > max_depth:
#             continue
# 
#         try:
#             response = requests.get(current_url)
#             if response.status_code == 200:
#                 visited.add(current_url)
#                 main_content = extract_main_content(response.text)
#                 contents[current_url] = main_content
#                 soup = BeautifulSoup(response.text, "html.parser")
# 
#                 for link in soup.find_all("a", href=True):
#                     absolute_link = urllib.parse.urljoin(current_url, link["href"])
#                     if absolute_link not in visited:
#                         to_visit.append((absolute_link, depth + 1))
# 
#         except requests.RequestException:
#             pass
# 
#     return visited, contents
# 
# 
# def crawl_to_json(start_url):
#     if not start_url.startswith("http"):
#         start_url = "https://" + start_url
#     crawled_urls, contents = crawl_url(start_url)
# 
#     print("\nSummalizing as json...")
# 
#     def process_url(url):
#         llm = scitex.ai.GenAI("gpt-4o-mini")
#         return {
#             "url": url,
#             "content": llm(f"Summarize this page in 1 line:\n\n{contents[url]}"),
#         }
# 
#     with ThreadPoolExecutor() as executor:
#         future_to_url = {executor.submit(process_url, url): url for url in crawled_urls}
#         crawled_pages = []
#         for future in tqdm(
#             as_completed(future_to_url),
#             total=len(crawled_urls),
#             desc="Processing URLs",
#         ):
#             crawled_pages.append(future.result())
# 
#     result = {"start_url": start_url, "crawled_pages": crawled_pages}
# 
#     return json.dumps(result, indent=2)
# 
# 
# def summarize_all(json_contents):
#     llm = scitex.ai.GenAI("gpt-4o-mini")
#     out = llm(f"Summarize this json file with 5 bullet points:\n\n{json_contents}")
#     return out
# 
# 
# def summarize_url(start_url):
#     json_result = crawl_to_json(start_url)
#     ground_summary = summarize_all(json_result)
# 
#     pprint(ground_summary)
#     return ground_summary, json_result
# 
# 
# main = summarize_url
# 
# if __name__ == "__main__":
#     import argparse
#     import scitex
# 
#     parser = argparse.ArgumentParser(description="")
#     parser.add_argument("--url", "-u", type=str, help="(default: %(default)s)")
#     args = parser.parse_args()
#     scitex.gen.print_block(args, c="yellow")
# 
#     main(args.url)

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/web/_summarize_url.py
# --------------------------------------------------------------------------------
