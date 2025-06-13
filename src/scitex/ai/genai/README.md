# GenAI Module

A unified interface for multiple generative AI providers with built-in cost tracking, chat history, and error handling.

## Features

- 🔌 **Unified Interface** - Same API for OpenAI, Anthropic, Google, and more
- 💰 **Cost Tracking** - Automatic token counting and cost calculation
- 💬 **Chat History** - Maintains conversation context
- 🛡️ **Error Handling** - Robust error handling across providers
- 🔒 **Type Safety** - Provider enum for type-safe provider selection
- 🌊 **Streaming Support** - Stream responses (provider-dependent)
- 🖼️ **Image Support** - Multi-modal capabilities (provider-dependent)

## Supported Providers

- **OpenAI** - GPT-3.5, GPT-4, GPT-4 Vision
- **Anthropic** - Claude 3 (Opus, Sonnet, Haiku), Claude 2
- **Google** - Gemini models
- **Groq** - Fast inference
- **DeepSeek** - Code and reasoning models
- **Perplexity** - Web-aware models
- **LLaMA** - Local models

## Installation

```bash
pip install scitex
```

## Quick Start

### Basic Usage

```python
from scitex.ai.genai import GenAI

# Create AI instance
ai = GenAI(provider="openai")

# Generate completion
response = ai.complete("What is the meaning of life?")
print(response)

# Check costs
print(ai.get_cost_summary())
```

### One-off Completions

```python
from scitex.ai.genai import complete

response = complete("Quick question: what is 2+2?", provider="anthropic")
```

### With Configuration

```python
ai = GenAI(
    provider="anthropic",
    model="claude-3-opus-20240229",
    system_prompt="You are a helpful coding assistant.",
    api_key="your-api-key"  # Optional if env var is set
)
```

## Advanced Usage

### Multi-turn Conversations

```python
ai = GenAI(provider="openai", model="gpt-4")

# Have a conversation
ai.complete("Hello! I'm learning Python.")
ai.complete("Can you show me how to read a file?")
ai.complete("What about writing to a file?")

# Review conversation
for msg in ai.get_history():
    print(f"{msg.role}: {msg.content[:50]}...")
```

### Cost Tracking

```python
# Get summary
print(ai.get_cost_summary())
# Output: Total cost: $0.045 | Requests: 3 | Tokens: 1,234

# Get detailed breakdown
costs = ai.get_detailed_costs()
print(f"Total cost: ${costs['total_cost']:.4f}")
print(f"Prompt tokens: {costs['total_prompt_tokens']:,}")
print(f"Completion tokens: {costs['total_completion_tokens']:,}")

# Cost by model
for model, stats in costs['cost_by_model'].items():
    print(f"{model}: ${stats['cost']:.4f}")
```

### Image Analysis

```python
ai = GenAI(provider="openai", model="gpt-4-vision-preview")

# Analyze image
response = ai.complete(
    "What's in this image?",
    images=["data:image/jpeg;base64,your_base64_data"]
)
```

### Provider Comparison

```python
from scitex.ai.genai import GenAI, Provider

prompt = "Explain recursion in one sentence"

for provider in [Provider.OPENAI, Provider.ANTHROPIC]:
    try:
        ai = GenAI(provider=provider)
        response = ai.complete(prompt)
        print(f"{provider.value}: {response}")
    except Exception as e:
        print(f"{provider.value} error: {e}")
```

### Error Handling

```python
try:
    ai = GenAI(provider="openai")
    response = ai.complete("Hello")
except ValueError as e:
    print(f"Configuration error: {e}")
except Exception as e:
    print(f"API error: {e}")
```

## Architecture

The GenAI module uses a component-based architecture:

```
GenAI (Main Interface)
├── AuthManager (API key management)
├── ChatHistory (Conversation management)
├── CostTracker (Token/cost tracking)
├── ResponseHandler (Response processing)
└── Provider (Specific implementations)
    ├── OpenAIProvider
    ├── AnthropicProvider
    ├── GoogleProvider
    └── ...
```

## Environment Variables

Set API keys as environment variables:

```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GOOGLE_API_KEY="..."
```

## Migration from Old API

See [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) for migrating from the old BaseGenAI pattern.

## Development

### Adding a New Provider

1. Create provider class inheriting from `BaseProvider`
2. Implement required methods:
   - `complete()`
   - `stream()`
   - `count_tokens()`
   - Properties: `supports_images`, `supports_streaming`, `max_context_length`
3. Register in `provider_factory.py`
4. Add tests

### Running Tests

```bash
# Unit tests
pytest tests/scitex/ai/genai/

# Integration tests
pytest tests/scitex/ai/genai/test_integration.py

# With coverage
pytest tests/scitex/ai/genai/ --cov=scitex.ai.genai
```

## Best Practices

1. **Always handle errors** - API calls can fail
2. **Monitor costs** - Especially with expensive models
3. **Clear history** - When starting new conversations
4. **Use type-safe providers** - With the Provider enum
5. **Set reasonable limits** - max_tokens, temperature, etc.

## License

Part of the SciTeX framework. See main LICENSE file.