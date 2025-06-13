# Provider Implementation Migration Guide

## Overview
This guide is for developers migrating provider implementations from BaseGenAI to the new component-based architecture.

## Migration Status

### ✅ Completed Providers
- **OpenAI** - `openai_provider.py` 
- **Anthropic** - `anthropic_provider.py`
- **Mock** - `mock_provider.py` (reference implementation)

### 🔄 Pending Providers
- **Google** - needs migration from `google.py` → `google_provider.py`
- **DeepSeek** - needs migration from `deepseek.py` → `deepseek_provider.py`
- **Groq** - needs migration from `groq.py` → `groq_provider.py`
- **Llama** - needs migration from `llama.py` → `llama_provider.py`
- **Perplexity** - needs migration from `perplexity.py` → `perplexity_provider.py`

## Step-by-Step Migration Process

### 1. Analyze the Old Provider

First, understand what the old provider does:
```python
# Check the old provider file (e.g., groq.py)
# Identify:
# - Supported models
# - Default model
# - API client initialization
# - Message formatting specifics
# - Streaming support
# - Special features
```

### 2. Create New Provider File

Create `{provider}_provider.py` with this template:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-25 12:00:00"
# Author: Yusuke Watanabe (ywatanabe@alumni.u-tokyo.ac.jp)
# scitex/src/scitex/ai/genai/{provider}_provider.py

"""
{Provider} provider implementation for GenAI.
"""

from typing import List, Dict, Any, Optional, Generator
import logging

from .base_provider import BaseProvider, CompletionResponse, Provider
from .provider_factory import register_provider

logger = logging.getLogger(__name__)


class {Provider}Provider(BaseProvider):
    """
    {Provider} provider implementation.
    
    Supports {list of supported models}.
    """
    
    SUPPORTED_MODELS = [
        # Copy from old provider
    ]
    
    DEFAULT_MODEL = "{default-model-name}"
    
    def __init__(self, config):
        """Initialize {Provider} provider."""
        self.config = config
        self.api_key = config.api_key
        self.model = config.model or self.DEFAULT_MODEL
        self.kwargs = config.kwargs or {}
        
        # Import {Provider} client
        try:
            from {provider_package} import {ProviderClient}
            self.client = {ProviderClient}(api_key=self.api_key)
        except ImportError:
            raise ImportError(
                "{Provider} package not installed. Install with: pip install {package-name}"
            )
    
    def complete(
        self,
        messages: List[Dict[str, Any]],
        **kwargs
    ) -> CompletionResponse:
        """
        Generate completion using {Provider} API.
        
        Args:
            messages: List of message dictionaries
            **kwargs: Additional parameters
        
        Returns:
            CompletionResponse with generated text and usage info
        """
        # Validate messages
        if not self.validate_messages(messages):
            raise ValueError("Invalid message format")
        
        # Format messages for {Provider}
        formatted_messages = self.format_messages(messages)
        
        # Prepare API parameters
        api_params = {
            "model": self.model,
            "messages": formatted_messages,
        }
        
        # Add optional parameters
        for param in ["temperature", "max_tokens", "top_p", ...]:
            if param in kwargs:
                api_params[param] = kwargs[param]
        
        try:
            # Make API call
            response = self.client.chat.completions.create(**api_params)
            
            # Extract content and usage
            content = response.choices[0].message.content
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }
            
            return CompletionResponse(
                content=content,
                input_tokens=usage["prompt_tokens"],
                output_tokens=usage["completion_tokens"],
                finish_reason=response.choices[0].finish_reason,
                provider_response=response
            )
            
        except Exception as e:
            logger.error(f"{Provider} API error: {str(e)}")
            raise
    
    def format_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format messages for {Provider} API.
        
        Convert from standard format to provider-specific format.
        """
        formatted_messages = []
        
        for msg in messages:
            # Format based on provider requirements
            formatted_msg = {
                "role": msg["role"],
                "content": msg["content"]
            }
            
            # Handle images if supported
            if "images" in msg and self.supports_images:
                # Provider-specific image formatting
                pass
            
            formatted_messages.append(formatted_msg)
        
        return formatted_messages
    
    def validate_messages(self, messages: List[Dict[str, Any]]) -> bool:
        """Validate message format."""
        if not messages:
            return False
            
        for msg in messages:
            if not isinstance(msg, dict):
                return False
            if "role" not in msg or "content" not in msg:
                return False
            if msg["role"] not in ["system", "user", "assistant"]:
                return False
                
        return True
    
    def stream(
        self, 
        messages: List[Dict[str, Any]],
        **kwargs
    ) -> Generator[str, None, CompletionResponse]:
        """Generate a streaming completion.
        
        Args:
            messages: List of messages in standard format
            **kwargs: Additional parameters
            
        Yields:
            Text chunks during streaming
            
        Returns:
            Final CompletionResponse when complete
        """
        # Similar to complete() but with streaming
        # See openai_provider.py for example
        raise NotImplementedError("Streaming not yet implemented for {Provider}")
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in the given text.
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Number of tokens
        """
        # Use provider's token counter if available
        # Otherwise use estimation
        return len(text.split()) * 4 // 3
    
    @property
    def supports_images(self) -> bool:
        """Check if this provider/model supports image inputs."""
        # Return True if provider supports multimodal inputs
        return False
    
    @property
    def supports_streaming(self) -> bool:
        """Check if this provider/model supports streaming."""
        # Most providers support streaming
        return True
    
    @property
    def max_context_length(self) -> int:
        """Get maximum context length for this model."""
        # Define context lengths per model
        context_lengths = {
            "model-name": 4096,
            # Add more models
        }
        return context_lengths.get(self.model, 4096)


# Auto-register when module is imported
register_provider(Provider.{PROVIDER}.value, {Provider}Provider)
```

### 3. Key Migration Tasks

#### 3.1 Extract Model Information
From old provider's `__init__.py`:
```python
# Old
self.MODELS = {
    "model-1": "...",
    "model-2": "...",
}

# New
SUPPORTED_MODELS = [
    "model-1",
    "model-2",
]
```

#### 3.2 Update Client Initialization
From old provider's `init_client()`:
```python
# Old
def init_client(self):
    client = SomeClient(api_key=self.api_key)
    return client

# New (in __init__)
try:
    from some_package import SomeClient
    self.client = SomeClient(api_key=self.api_key)
except ImportError:
    raise ImportError("Package not installed...")
```

#### 3.3 Convert Message Formatting
From old provider's `format_history()`:
```python
# Old
def format_history(self, history):
    # Complex formatting logic
    return formatted

# New
def format_messages(self, messages):
    # Simpler, cleaner formatting
    return formatted_messages
```

#### 3.4 Update API Calls
From old provider's `call_static()` and `call_stream()`:
```python
# Old
def call_static(self, messages_formatted, **kwargs):
    response = self.client.some_method(...)
    return response

# New (in complete())
response = self.client.chat.completions.create(
    model=self.model,
    messages=formatted_messages,
    **api_params
)
return CompletionResponse(...)
```

### 4. Common Patterns by Provider

#### OpenAI-like Providers (Groq, DeepSeek, Perplexity)
These typically use OpenAI-compatible APIs:
```python
# Similar client initialization
from openai import OpenAI
self.client = OpenAI(
    api_key=self.api_key,
    base_url="https://api.{provider}.com/v1"  # Custom base URL
)

# Same API calls as OpenAI
response = self.client.chat.completions.create(...)
```

#### Google (Vertex AI / Gemini)
Different API structure:
```python
# Different client
from google.generativeai import GenerativeModel
self.client = GenerativeModel(model_name=self.model)

# Different message format
formatted_messages = [
    {"role": "user", "parts": [msg["content"]]},
    # ...
]
```

#### Local Model Providers (Llama)
May use different approaches:
```python
# Local model loading
from llama_cpp import Llama
self.client = Llama(model_path=self.model_path)

# Different completion method
response = self.client(prompt, max_tokens=kwargs.get("max_tokens", 100))
```

### 5. Testing the Migration

Create test file `test_{provider}_provider.py`:
```python
def test_{provider}_provider_complete():
    """Test {Provider} provider completion."""
    with patch('{provider_package}.{ProviderClient}') as mock_client:
        # Mock the API response
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(content="Test response"),
                finish_reason="stop"
            )
        ]
        mock_response.usage = MagicMock(
            prompt_tokens=10,
            completion_tokens=20,
            total_tokens=30
        )
        mock_client.return_value.chat.completions.create.return_value = mock_response
        
        # Test provider
        config = ProviderConfig(api_key="test-key", model="test-model")
        provider = {Provider}Provider(config)
        
        messages = [{"role": "user", "content": "Test"}]
        response = provider.complete(messages)
        
        assert response.content == "Test response"
        assert response.input_tokens == 10
        assert response.output_tokens == 20
```

### 6. Update Provider Registry

Ensure the provider is registered in `provider_factory.py`:
```python
# Check that Provider enum includes your provider
class Provider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    GROQ = "groq"
    DEEPSEEK = "deepseek"
    LLAMA = "llama"
    PERPLEXITY = "perplexity"
```

### 7. Deprecation Strategy

In the old provider file, add deprecation warning:
```python
import warnings

class {OldProvider}(BaseGenAI):
    def __init__(self, *args, **kwargs):
        warnings.warn(
            f"{OldProvider} is deprecated. Use GenAI(provider='{provider}') instead.",
            DeprecationWarning,
            stacklevel=2
        )
        super().__init__(*args, **kwargs)
```

## Validation Checklist

Before marking migration complete:
- [ ] New provider file created following template
- [ ] All SUPPORTED_MODELS copied from old provider
- [ ] DEFAULT_MODEL set correctly
- [ ] Client initialization working with proper error handling
- [ ] complete() method fully implemented
- [ ] format_messages() handles provider-specific formatting
- [ ] validate_messages() implemented
- [ ] stream() method implemented (or raises NotImplementedError)
- [ ] Properties (supports_images, supports_streaming, max_context_length) set
- [ ] Auto-registration line added at bottom
- [ ] Test file created with basic tests
- [ ] Old provider has deprecation warning
- [ ] Integration tests updated

## Migration Order

Recommended order:
1. **Groq** - Most similar to OpenAI, good practice
2. **DeepSeek** - Also OpenAI-compatible
3. **Perplexity** - Similar pattern
4. **Google** - Different API, more complex
5. **Llama** - Local models, most different

## Resources

- Reference implementations: `openai_provider.py`, `anthropic_provider.py`
- Test patterns: `test_openai_provider.py`, `test_anthropic_provider.py`
- Base classes: `base_provider.py`, `provider_base.py`
- Factory: `provider_factory.py`

## Common Issues

### Import Errors
Ensure proper imports:
```python
from .base_provider import BaseProvider, CompletionResponse, Provider
from .provider_factory import register_provider
```

### Registration Failures
Make sure to use the correct enum value:
```python
register_provider(Provider.GROQ.value, GroqProvider)  # Not "groq"
```

### API Response Differences
Each provider may return slightly different response formats. Always extract carefully:
```python
# Be defensive
content = getattr(response.choices[0].message, 'content', '')
usage = getattr(response, 'usage', {})
```