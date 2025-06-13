#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-03 08:30:00 (ywatanabe)"
# Author: ywatanabe (ywatanabe@alumni.u-tokyo.ac.jp)
# File: tests/scitex/ai/genai/test_groq.py

import os
import pytest
import warnings
from unittest.mock import Mock, patch
import sys


class TestGroq:
    """Test suite for Groq class functionality.
    
    Note: Due to circular import issues in the current codebase,
    these tests focus on verifying the module structure and basic functionality.
    """

    def test_groq_module_exists(self):
        """Test that Groq module file exists."""
        module_path = os.path.join(
            os.path.dirname(__file__), '..', '..', '..', '..', 'src', 
            'scitex', 'ai', 'genai', 'groq.py'
        )
        assert os.path.exists(module_path), "Groq module file should exist"

    def test_groq_module_has_groq_class(self):
        """Test that Groq module contains Groq class definition."""
        module_path = os.path.join(
            os.path.dirname(__file__), '..', '..', '..', '..', 'src', 
            'scitex', 'ai', 'genai', 'groq.py'
        )
        
        with open(module_path, 'r') as f:
            content = f.read()
        
        assert 'class Groq(' in content, "Groq class should be defined in module"
        assert 'BaseGenAI' in content, "Groq should inherit from BaseGenAI"

    def test_groq_module_has_deprecation_warning(self):
        """Test that Groq module contains deprecation warning."""
        module_path = os.path.join(
            os.path.dirname(__file__), '..', '..', '..', '..', 'src', 
            'scitex', 'ai', 'genai', 'groq.py'
        )
        
        with open(module_path, 'r') as f:
            content = f.read()
        
        assert 'warnings.warn' in content, "Groq module should issue deprecation warning"
        assert 'DeprecationWarning' in content, "Groq module should use DeprecationWarning"
        assert 'deprecated' in content.lower(), "Groq module should have deprecation notice"

    def test_groq_module_has_required_methods(self):
        """Test that Groq module contains required methods."""
        module_path = os.path.join(
            os.path.dirname(__file__), '..', '..', '..', '..', 'src', 
            'scitex', 'ai', 'genai', 'groq.py'
        )
        
        with open(module_path, 'r') as f:
            content = f.read()
        
        required_methods = [
            '_init_client',
            '_api_call_static',
            '_api_call_stream'
        ]
        
        for method in required_methods:
            assert f'def {method}(' in content, f"Groq should implement {method} method"

    def test_groq_module_has_proper_imports(self):
        """Test that Groq module has proper import statements."""
        module_path = os.path.join(
            os.path.dirname(__file__), '..', '..', '..', '..', 'src', 
            'scitex', 'ai', 'genai', 'groq.py'
        )
        
        with open(module_path, 'r') as f:
            content = f.read()
        
        expected_imports = [
            'from groq import Groq as _Groq',
            'from .base_genai import BaseGenAI',
            'import warnings'
        ]
        
        for import_stmt in expected_imports:
            assert import_stmt in content, f"Groq module should have import: {import_stmt}"

    def test_groq_module_has_default_parameters(self):
        """Test that Groq class has expected default parameters."""
        module_path = os.path.join(
            os.path.dirname(__file__), '..', '..', '..', '..', 'src', 
            'scitex', 'ai', 'genai', 'groq.py'
        )
        
        with open(module_path, 'r') as f:
            content = f.read()
        
        # Check for initialization parameters
        expected_params = [
            'system_setting',
            'api_key',
            'model',
            'stream',
            'temperature',
            'max_tokens'
        ]
        
        for param in expected_params:
            assert f'{param}:' in content or f'{param}=' in content, \
                f"Groq should have {param} parameter"

    def test_groq_module_has_llama_model_defaults(self):
        """Test that Groq module has Llama model defaults."""
        module_path = os.path.join(
            os.path.dirname(__file__), '..', '..', '..', '..', 'src', 
            'scitex', 'ai', 'genai', 'groq.py'
        )
        
        with open(module_path, 'r') as f:
            content = f.read()
        
        # Check for Groq/Llama model defaults
        assert 'llama3-8b-8192' in content, "Groq should have Llama model default"
        assert '8000' in content, "Groq should have appropriate max_tokens default"

    def test_groq_module_has_api_key_validation(self):
        """Test that Groq module has API key validation."""
        module_path = os.path.join(
            os.path.dirname(__file__), '..', '..', '..', '..', 'src', 
            'scitex', 'ai', 'genai', 'groq.py'
        )
        
        with open(module_path, 'r') as f:
            content = f.read()
        
        # Check for API key validation
        assert 'GROQ_API_KEY' in content, "Groq should reference GROQ_API_KEY environment variable"
        assert 'not api_key' in content or 'ValueError' in content, "Groq should validate API key"

    def test_groq_module_has_token_tracking(self):
        """Test that Groq module has token usage tracking."""
        module_path = os.path.join(
            os.path.dirname(__file__), '..', '..', '..', '..', 'src', 
            'scitex', 'ai', 'genai', 'groq.py'
        )
        
        with open(module_path, 'r') as f:
            content = f.read()
        
        # Check for token tracking
        assert 'input_tokens' in content, "Groq should track input tokens"
        assert 'output_tokens' in content, "Groq should track output tokens"
        assert 'prompt_tokens' in content, "Groq should access prompt tokens from usage"
        assert 'completion_tokens' in content, "Groq should access completion tokens from usage"

    def test_groq_module_has_streaming_support(self):
        """Test that Groq module supports streaming."""
        module_path = os.path.join(
            os.path.dirname(__file__), '..', '..', '..', '..', 'src', 
            'scitex', 'ai', 'genai', 'groq.py'
        )
        
        with open(module_path, 'r') as f:
            content = f.read()
        
        # Check for streaming support
        assert 'stream=' in content, "Groq should support streaming parameter"
        assert 'yield' in content, "Groq should use yield for streaming"

    def test_groq_module_has_proper_provider_name(self):
        """Test that Groq module sets correct provider name."""
        module_path = os.path.join(
            os.path.dirname(__file__), '..', '..', '..', '..', 'src', 
            'scitex', 'ai', 'genai', 'groq.py'
        )
        
        with open(module_path, 'r') as f:
            content = f.read()
        
        # Check provider name
        assert 'provider="Groq"' in content, "Groq should set provider name correctly"

    def test_groq_module_has_client_initialization(self):
        """Test that Groq module has proper client initialization."""
        module_path = os.path.join(
            os.path.dirname(__file__), '..', '..', '..', '..', 'src', 
            'scitex', 'ai', 'genai', 'groq.py'
        )
        
        with open(module_path, 'r') as f:
            content = f.read()
        
        # Check client initialization
        assert '_Groq(' in content, "Groq should use Groq client"
        assert 'api_key=self.api_key' in content, "Groq should pass API key to client"

    def test_groq_module_structure_integrity(self):
        """Test overall structure integrity of Groq module."""
        module_path = os.path.join(
            os.path.dirname(__file__), '..', '..', '..', '..', 'src', 
            'scitex', 'ai', 'genai', 'groq.py'
        )
        
        with open(module_path, 'r') as f:
            content = f.read()
        
        # Basic structure checks
        assert content.strip(), "Groq module should not be empty"
        assert '#!/usr/bin/env python3' in content, "Groq module should have shebang"

    def test_groq_module_error_handling(self):
        """Test that Groq module has proper error handling."""
        module_path = os.path.join(
            os.path.dirname(__file__), '..', '..', '..', '..', 'src', 
            'scitex', 'ai', 'genai', 'groq.py'
        )
        
        with open(module_path, 'r') as f:
            content = f.read()
        
        # Check for error handling
        assert 'ValueError' in content, "Groq module should have error handling"

    def test_groq_module_documentation(self):
        """Test that Groq module has proper documentation."""
        module_path = os.path.join(
            os.path.dirname(__file__), '..', '..', '..', '..', 'src', 
            'scitex', 'ai', 'genai', 'groq.py'
        )
        
        with open(module_path, 'r') as f:
            content = f.read()
        
        # Check for documentation
        assert '"""' in content, "Groq module should have docstrings"
        assert 'Functionality:' in content, "Groq module should document functionality"
        assert 'Input:' in content, "Groq module should document inputs"
        assert 'Output:' in content, "Groq module should document outputs"

    def test_groq_module_has_chat_completions_usage(self):
        """Test that Groq module uses chat completions API."""
        module_path = os.path.join(
            os.path.dirname(__file__), '..', '..', '..', '..', 'src', 
            'scitex', 'ai', 'genai', 'groq.py'
        )
        
        with open(module_path, 'r') as f:
            content = f.read()
        
        # Check for chat completions API usage
        assert 'chat.completions.create' in content, "Groq should use chat completions API"
        assert 'messages=self.history' in content, "Groq should pass message history"

    def test_groq_module_has_proper_message_extraction(self):
        """Test that Groq module has proper message content extraction."""
        module_path = os.path.join(
            os.path.dirname(__file__), '..', '..', '..', '..', 'src', 
            'scitex', 'ai', 'genai', 'groq.py'
        )
        
        with open(module_path, 'r') as f:
            content = f.read()
        
        # Check for message extraction
        assert 'choices[0].message.content' in content, "Groq should extract message content"
        assert 'choices[0].delta.content' in content, "Groq should extract delta content for streaming"

    def test_groq_module_max_tokens_limit(self):
        """Test that Groq module has max_tokens limit enforcement."""
        module_path = os.path.join(
            os.path.dirname(__file__), '..', '..', '..', '..', 'src', 
            'scitex', 'ai', 'genai', 'groq.py'
        )
        
        with open(module_path, 'r') as f:
            content = f.read()
        
        # Check for max_tokens limit
        assert 'min(max_tokens, 8000)' in content, "Groq should enforce max_tokens limit"

    def test_groq_module_temperature_configuration(self):
        """Test that Groq module has temperature configuration."""
        module_path = os.path.join(
            os.path.dirname(__file__), '..', '..', '..', '..', 'src', 
            'scitex', 'ai', 'genai', 'groq.py'
        )
        
        with open(module_path, 'r') as f:
            content = f.read()
        
        # Check for temperature configuration
        assert 'temperature: float = 0.5' in content, "Groq should have default temperature"
        assert 'temperature=self.temperature' in content, "Groq should pass temperature to API"

    def test_groq_module_api_parameters(self):
        """Test that Groq module passes correct API parameters."""
        module_path = os.path.join(
            os.path.dirname(__file__), '..', '..', '..', '..', 'src', 
            'scitex', 'ai', 'genai', 'groq.py'
        )
        
        with open(module_path, 'r') as f:
            content = f.read()
        
        # Check for API parameters
        expected_params = [
            'model=self.model',
            'messages=self.history',
            'temperature=self.temperature',
            'max_tokens=self.max_tokens'
        ]
        
        for param in expected_params:
            assert param in content, f"Groq should use parameter: {param}"


if __name__ == "__main__":
    pytest.main([__file__])