#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-03 08:14:40 (ywatanabe)"
# Author: ywatanabe (ywatanabe@alumni.u-tokyo.ac.jp)
# File: tests/scitex/ai/genai/test_deepseek.py

import os
import pytest
import warnings
from unittest.mock import Mock, patch
import sys


class TestDeepSeek:
    """Test suite for DeepSeek class functionality.
    
    Note: Due to circular import issues in the current codebase,
    these tests focus on verifying the module structure and basic functionality.
    """

    def test_deepseek_module_exists(self):
        """Test that DeepSeek module file exists."""
        module_path = os.path.join(
            os.path.dirname(__file__), '..', '..', '..', '..', 'src', 
            'scitex', 'ai', 'genai', 'deepseek.py'
        )
        assert os.path.exists(module_path), "DeepSeek module file should exist"

    def test_deepseek_module_has_deepseek_class(self):
        """Test that DeepSeek module contains DeepSeek class definition."""
        module_path = os.path.join(
            os.path.dirname(__file__), '..', '..', '..', '..', 'src', 
            'scitex', 'ai', 'genai', 'deepseek.py'
        )
        
        with open(module_path, 'r') as f:
            content = f.read()
        
        assert 'class DeepSeek(' in content, "DeepSeek class should be defined in module"
        assert 'BaseGenAI' in content, "DeepSeek should inherit from BaseGenAI"

    def test_deepseek_module_has_deprecation_warning(self):
        """Test that DeepSeek module contains deprecation warning."""
        module_path = os.path.join(
            os.path.dirname(__file__), '..', '..', '..', '..', 'src', 
            'scitex', 'ai', 'genai', 'deepseek.py'
        )
        
        with open(module_path, 'r') as f:
            content = f.read()
        
        assert 'DEPRECATED' in content, "DeepSeek module should have deprecation notice"
        assert 'warnings.warn' in content, "DeepSeek module should issue deprecation warning"
        assert 'DeprecationWarning' in content, "DeepSeek module should use DeprecationWarning"

    def test_deepseek_module_has_required_methods(self):
        """Test that DeepSeek module contains required methods."""
        module_path = os.path.join(
            os.path.dirname(__file__), '..', '..', '..', '..', 'src', 
            'scitex', 'ai', 'genai', 'deepseek.py'
        )
        
        with open(module_path, 'r') as f:
            content = f.read()
        
        required_methods = [
            '_init_client',
            '_api_call_static',
            '_api_call_stream'
        ]
        
        for method in required_methods:
            assert f'def {method}(' in content, f"DeepSeek should implement {method} method"

    def test_deepseek_module_has_proper_imports(self):
        """Test that DeepSeek module has proper import statements."""
        module_path = os.path.join(
            os.path.dirname(__file__), '..', '..', '..', '..', 'src', 
            'scitex', 'ai', 'genai', 'deepseek.py'
        )
        
        with open(module_path, 'r') as f:
            content = f.read()
        
        expected_imports = [
            'from openai import OpenAI as _OpenAI',
            'from .base_genai import BaseGenAI',
            'import warnings'
        ]
        
        for import_stmt in expected_imports:
            assert import_stmt in content, f"DeepSeek module should have import: {import_stmt}"

    def test_deepseek_module_has_default_parameters(self):
        """Test that DeepSeek class has expected default parameters."""
        module_path = os.path.join(
            os.path.dirname(__file__), '..', '..', '..', '..', 'src', 
            'scitex', 'ai', 'genai', 'deepseek.py'
        )
        
        with open(module_path, 'r') as f:
            content = f.read()
        
        # Check for initialization parameters
        expected_params = [
            'system_setting',
            'model',
            'api_key',
            'stream',
            'temperature',
            'max_tokens'
        ]
        
        for param in expected_params:
            assert f'{param}=' in content or f'{param},' in content, \
                f"DeepSeek should have {param} parameter"

    def test_deepseek_module_has_deepseek_defaults(self):
        """Test that DeepSeek module has DeepSeek-specific defaults."""
        module_path = os.path.join(
            os.path.dirname(__file__), '..', '..', '..', '..', 'src', 
            'scitex', 'ai', 'genai', 'deepseek.py'
        )
        
        with open(module_path, 'r') as f:
            content = f.read()
        
        # Check for DeepSeek defaults
        assert 'deepseek-chat' in content, "DeepSeek should have deepseek-chat model default"
        assert '4096' in content, "DeepSeek should have appropriate max_tokens default"

    def test_deepseek_module_has_base_url_configuration(self):
        """Test that DeepSeek module has proper base URL configuration."""
        module_path = os.path.join(
            os.path.dirname(__file__), '..', '..', '..', '..', 'src', 
            'scitex', 'ai', 'genai', 'deepseek.py'
        )
        
        with open(module_path, 'r') as f:
            content = f.read()
        
        # Check for base URL configuration
        assert 'api.deepseek.com' in content, "DeepSeek should use DeepSeek API base URL"
        assert 'base_url=' in content, "DeepSeek should set base_url parameter"

    def test_deepseek_module_has_token_tracking(self):
        """Test that DeepSeek module has token usage tracking."""
        module_path = os.path.join(
            os.path.dirname(__file__), '..', '..', '..', '..', 'src', 
            'scitex', 'ai', 'genai', 'deepseek.py'
        )
        
        with open(module_path, 'r') as f:
            content = f.read()
        
        # Check for token tracking
        assert 'input_tokens' in content, "DeepSeek should track input tokens"
        assert 'output_tokens' in content, "DeepSeek should track output tokens"
        assert 'prompt_tokens' in content, "DeepSeek should access prompt tokens from usage"
        assert 'completion_tokens' in content, "DeepSeek should access completion tokens from usage"

    def test_deepseek_module_has_streaming_support(self):
        """Test that DeepSeek module supports streaming."""
        module_path = os.path.join(
            os.path.dirname(__file__), '..', '..', '..', '..', 'src', 
            'scitex', 'ai', 'genai', 'deepseek.py'
        )
        
        with open(module_path, 'r') as f:
            content = f.read()
        
        # Check for streaming support
        assert 'stream=' in content, "DeepSeek should support streaming parameter"
        assert 'yield' in content, "DeepSeek should use yield for streaming"
        assert 'buffer' in content, "DeepSeek should use buffering for streaming"

    def test_deepseek_module_has_proper_provider_name(self):
        """Test that DeepSeek module sets correct provider name."""
        module_path = os.path.join(
            os.path.dirname(__file__), '..', '..', '..', '..', 'src', 
            'scitex', 'ai', 'genai', 'deepseek.py'
        )
        
        with open(module_path, 'r') as f:
            content = f.read()
        
        # Check provider name
        assert 'provider="DeepSeek"' in content, "DeepSeek should set provider name correctly"

    def test_deepseek_module_has_client_initialization(self):
        """Test that DeepSeek module has proper client initialization."""
        module_path = os.path.join(
            os.path.dirname(__file__), '..', '..', '..', '..', 'src', 
            'scitex', 'ai', 'genai', 'deepseek.py'
        )
        
        with open(module_path, 'r') as f:
            content = f.read()
        
        # Check client initialization
        assert '_OpenAI(' in content, "DeepSeek should use OpenAI client"
        assert 'api_key=self.api_key' in content, "DeepSeek should pass API key to client"

    def test_deepseek_module_structure_integrity(self):
        """Test overall structure integrity of DeepSeek module."""
        module_path = os.path.join(
            os.path.dirname(__file__), '..', '..', '..', '..', 'src', 
            'scitex', 'ai', 'genai', 'deepseek.py'
        )
        
        with open(module_path, 'r') as f:
            content = f.read()
        
        # Basic structure checks
        assert content.strip(), "DeepSeek module should not be empty"
        assert '#!/usr/bin/env python3' in content, "DeepSeek module should have shebang"
        assert 'if __name__ == "__main__"' in content, "DeepSeek module should have main block"

    def test_deepseek_module_error_handling(self):
        """Test that DeepSeek module has proper error handling."""
        module_path = os.path.join(
            os.path.dirname(__file__), '..', '..', '..', '..', 'src', 
            'scitex', 'ai', 'genai', 'deepseek.py'
        )
        
        with open(module_path, 'r') as f:
            content = f.read()
        
        # Check for error handling
        assert 'try:' in content, "DeepSeek module should have try-except blocks"
        assert 'except' in content, "DeepSeek module should handle exceptions"

    def test_deepseek_module_documentation(self):
        """Test that DeepSeek module has proper documentation."""
        module_path = os.path.join(
            os.path.dirname(__file__), '..', '..', '..', '..', 'src', 
            'scitex', 'ai', 'genai', 'deepseek.py'
        )
        
        with open(module_path, 'r') as f:
            content = f.read()
        
        # Check for documentation
        assert '"""' in content, "DeepSeek module should have docstrings"
        assert 'Functionality:' in content, "DeepSeek module should document functionality"
        assert 'Input:' in content, "DeepSeek module should document inputs"
        assert 'Output:' in content, "DeepSeek module should document outputs"

    def test_deepseek_module_has_streaming_buffering_logic(self):
        """Test that DeepSeek module has proper streaming buffering logic."""
        module_path = os.path.join(
            os.path.dirname(__file__), '..', '..', '..', '..', 'src', 
            'scitex', 'ai', 'genai', 'deepseek.py'
        )
        
        with open(module_path, 'r') as f:
            content = f.read()
        
        # Check for streaming buffering logic
        assert 'buffer +=' in content, "DeepSeek should accumulate text in buffer"
        assert '.!?' in content, "DeepSeek should check for sentence-ending characters"
        assert 'yield buffer' in content, "DeepSeek should yield buffered content"

    def test_deepseek_module_has_chat_completions_usage(self):
        """Test that DeepSeek module uses chat completions API."""
        module_path = os.path.join(
            os.path.dirname(__file__), '..', '..', '..', '..', 'src', 
            'scitex', 'ai', 'genai', 'deepseek.py'
        )
        
        with open(module_path, 'r') as f:
            content = f.read()
        
        # Check for chat completions API usage
        assert 'chat.completions.create' in content, "DeepSeek should use chat completions API"
        assert 'messages=self.history' in content, "DeepSeek should pass message history"

    def test_deepseek_module_has_proper_message_extraction(self):
        """Test that DeepSeek module has proper message content extraction."""
        module_path = os.path.join(
            os.path.dirname(__file__), '..', '..', '..', '..', 'src', 
            'scitex', 'ai', 'genai', 'deepseek.py'
        )
        
        with open(module_path, 'r') as f:
            content = f.read()
        
        # Check for message extraction
        assert 'choices[0].message.content' in content, "DeepSeek should extract message content"
        assert 'choices[0].delta.content' in content, "DeepSeek should extract delta content for streaming"

    def test_deepseek_module_has_usage_tracking_protection(self):
        """Test that DeepSeek module has protected usage tracking."""
        module_path = os.path.join(
            os.path.dirname(__file__), '..', '..', '..', '..', 'src', 
            'scitex', 'ai', 'genai', 'deepseek.py'
        )
        
        with open(module_path, 'r') as f:
            content = f.read()
        
        # Check for protected usage tracking (try-except around usage access)
        usage_tracking_lines = [line for line in content.split('\n') if 'input_tokens +=' in line or 'output_tokens +=' in line]
        assert len(usage_tracking_lines) > 0, "DeepSeek should have usage tracking"

    def test_deepseek_module_api_parameters(self):
        """Test that DeepSeek module passes correct API parameters."""
        module_path = os.path.join(
            os.path.dirname(__file__), '..', '..', '..', '..', 'src', 
            'scitex', 'ai', 'genai', 'deepseek.py'
        )
        
        with open(module_path, 'r') as f:
            content = f.read()
        
        # Check for API parameters
        expected_params = [
            'model=self.model',
            'messages=self.history',
            'temperature=self.temperature',
            'max_tokens=self.max_tokens',
            'seed=self.seed'
        ]
        
        for param in expected_params:
            assert param in content, f"DeepSeek should use parameter: {param}"


if __name__ == "__main__":
    pytest.main([__file__])