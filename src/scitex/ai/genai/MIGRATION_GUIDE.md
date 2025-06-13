# GenAI Module Migration Guide

This guide helps you migrate from the old BaseGenAI god object pattern to the new component-based architecture.

## Overview of Changes

The AI module has been refactored from a monolithic god object pattern to a clean, component-based architecture following SOLID principles.

### Key Changes:
1. **BaseGenAI god object** → **Multiple focused components**
2. **Direct provider classes** → **Factory pattern with registry**
3. **Mixed responsibilities** → **Single Responsibility Principle**
4. **Tight coupling** → **Dependency injection**

## Breaking Changes

### 1. Import Path Changes

**Old:**
```python
from scitex.ai._gen_ai import genai_factory
from scitex.ai._gen_ai._BaseGenAI import BaseGenAI
from scitex.ai._gen_ai._Anthropic import Anthropic
```

**New:**
```python
from scitex.ai.genai import GenAI, complete
from scitex.ai.genai import Provider  # For type-safe provider names
```

### 2. Initialization Changes

**Old:**
```python
# Using factory
ai = genai_factory("openai", api_key="sk-...")

# Direct instantiation
ai = Anthropic(api_key="sk-...")
```

**New:**
```python
# Using GenAI class
ai = GenAI(provider="openai", api_key="sk-...")

# With specific model
ai = GenAI(
    provider="anthropic",
    model="claude-3-opus-20240229",
    system_prompt="You are a helpful assistant."
)

# One-off completion
response = complete("What is 2+2?", provider="openai")
```

### 3. Method Name Changes

| Old Method | New Method | Notes |
|------------|------------|-------|
| `ai.run()` | `ai.complete()` | More descriptive name |
| `ai.calc_costs()` | `ai.get_cost_summary()` | Returns formatted string |
| `ai.messages` | `ai.get_history()` | Returns list of Message objects |
| `ai.reset_messages()` | `ai.clear_history()` | More descriptive |

### 4. Cost Tracking Changes

**Old:**
```python
costs = ai.calc_costs()  # Returns dict
print(f"Cost: ${costs['total']}")
```

**New:**
```python
# Human-readable summary
print(ai.get_cost_summary())
# Output: "Total cost: $0.045 | Requests: 10 | Tokens: 1,234"

# Detailed breakdown
costs = ai.get_detailed_costs()
print(f"Total: ${costs['total_cost']:.3f}")
print(f"By model: {costs['cost_by_model']}")
```

### 5. Message History Changes

**Old:**
```python
# Direct access to messages list
ai.messages.append({"role": "user", "content": "Hello"})
```

**New:**
```python
# Messages are managed internally
# History is automatically maintained
response = ai.complete("Hello")

# Access history if needed
history = ai.get_history()  # Returns list of Message objects
for msg in history:
    print(f"{msg.role}: {msg.content}")
```

### 6. System Prompt Changes

**Old:**
```python
ai = Anthropic(api_key="...", system_prompt="You are helpful")
# Or
ai.system_prompt = "New prompt"
```

**New:**
```python
# Set during initialization
ai = GenAI(
    provider="anthropic",
    system_prompt="You are helpful"
)

# System prompt is immutable after creation
# Create new instance for different system prompt
```

## Migration Examples

### Example 1: Basic Completion

**Old:**
```python
from scitex.ai._gen_ai import genai_factory

ai = genai_factory("openai")
response = ai.run("What is the capital of France?")
print(response)
```

**New:**
```python
from scitex.ai.genai import GenAI

ai = GenAI(provider="openai")
response = ai.complete("What is the capital of France?")
print(response)
```

### Example 2: With Cost Tracking

**Old:**
```python
ai = genai_factory("gpt-4")
response = ai.run("Complex analysis...")
costs = ai.calc_costs()
print(f"This cost: ${costs['total']:.3f}")
```

**New:**
```python
ai = GenAI(provider="openai", model="gpt-4")
response = ai.complete("Complex analysis...")
print(ai.get_cost_summary())
```

### Example 3: Conversation with History

**Old:**
```python
ai = genai_factory("claude-3")
ai.run("Hello, I need help with Python")
ai.run("How do I read a CSV file?")
ai.run("What about writing?")

# Access history
for msg in ai.messages:
    print(f"{msg['role']}: {msg['content'][:50]}...")
```

**New:**
```python
ai = GenAI(provider="anthropic", model="claude-3-opus-20240229")
ai.complete("Hello, I need help with Python")
ai.complete("How do I read a CSV file?")
ai.complete("What about writing?")

# Access history
for msg in ai.get_history():
    print(f"{msg.role}: {msg.content[:50]}...")
```

### Example 4: Image Analysis

**Old:**
```python
ai = genai_factory("gpt-4-vision-preview")
response = ai.run(
    "What's in this image?",
    images=["base64_image_data"]
)
```

**New:**
```python
ai = GenAI(provider="openai", model="gpt-4-vision-preview")
response = ai.complete(
    "What's in this image?",
    images=["data:image/jpeg;base64,base64_image_data"]
)
```

### Example 5: Provider Switching

**Old:**
```python
# Need separate instances
openai = genai_factory("openai")
anthropic = genai_factory("claude-3")

response1 = openai.run("Question")
response2 = anthropic.run("Same question")
```

**New:**
```python
# Create separate instances
openai = GenAI(provider="openai")
anthropic = GenAI(provider="anthropic")

response1 = openai.complete("Question")
response2 = anthropic.complete("Same question")

# Or use convenience function
from scitex.ai.genai import complete
response1 = complete("Question", provider="openai")
response2 = complete("Question", provider="anthropic")
```

## Component Architecture

The new architecture separates concerns into focused components:

1. **AuthManager**: Handles API key management
2. **ChatHistory**: Manages conversation history
3. **CostTracker**: Tracks token usage and costs
4. **ResponseHandler**: Processes API responses
5. **ModelRegistry**: Validates model names
6. **ImageProcessor**: Handles image inputs
7. **Provider implementations**: OpenAI, Anthropic, etc.

## Best Practices

1. **Use Type-Safe Provider Names**:
   ```python
   from scitex.ai.genai import GenAI, Provider
   
   ai = GenAI(provider=Provider.OPENAI)  # Type-safe enum
   ```

2. **Handle Errors Appropriately**:
   ```python
   try:
       response = ai.complete("Question")
   except ValueError as e:
       print(f"Configuration error: {e}")
   except Exception as e:
       print(f"API error: {e}")
   ```

3. **Monitor Costs**:
   ```python
   ai = GenAI(provider="openai", model="gpt-4")
   
   # Do work...
   for question in questions:
       ai.complete(question)
   
   # Check costs
   print(ai.get_cost_summary())
   ```

4. **Use Convenience Function for One-offs**:
   ```python
   from scitex.ai.genai import complete
   
   # No need to manage instance
   answer = complete("Quick question", provider="anthropic")
   ```

## Backward Compatibility

For temporary backward compatibility, the old interfaces are still available but deprecated:

```python
# These still work but are deprecated
from scitex.ai.genai import genai_factory  # Old factory
from scitex.ai.genai import Anthropic, OpenAI  # Old classes

# Will show deprecation warning
ai = genai_factory("openai")
```

## Troubleshooting

### Issue: "Model not found in pricing table"
The new system has a fallback for unknown models. Cost tracking will still work with estimated prices.

### Issue: "No API key provided"
The new system checks environment variables. Set:
- `OPENAI_API_KEY` for OpenAI
- `ANTHROPIC_API_KEY` for Anthropic
- etc.

### Issue: "Messages are being trimmed"
The new system keeps all messages by default. If you need trimming, this will be added in a future update.

## Need Help?

1. Check the [API documentation](../README.md)
2. Look at the [examples](../../../../examples/scitex/ai/)
3. Review the [test files](../../../../tests/scitex/ai/genai/) for usage patterns

## Summary

The new GenAI module provides:
- ✅ Cleaner, more maintainable code
- ✅ Better error handling
- ✅ Improved cost tracking
- ✅ Type safety with Provider enum
- ✅ Consistent interface across providers
- ✅ Easier testing and mocking

While migration requires some code changes, the new architecture provides a more robust and maintainable foundation for AI integrations.