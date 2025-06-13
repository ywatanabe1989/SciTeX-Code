# Examples of Updating Code to New GenAI Module

## 1. Update Old Test File

**Old test file** (`tests/scitex/ai/_gen_ai/test__genai_factory.py`):
```python
def main(
    model="deepseek-coder",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    stream=False,
    prompt="Hi, please tell me about the hippocampus",
    seed=None,
    temperature=1.0,
):
    import scitex
    
    m = scitex.ai.GenAI(
        model=model,
        api_key=api_key,
        stream=stream,
        seed=seed,
        temperature=temperature,
    )
    out = m(prompt)  # Old style
    
    print(out)
    return out
```

**Updated version**:
```python
def main(
    model="deepseek-coder",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    stream=False,
    prompt="Hi, please tell me about the hippocampus",
    seed=None,
    temperature=1.0,
):
    from scitex.ai.genai import GenAI
    
    # Create GenAI instance with provider
    ai = GenAI(
        provider="deepseek",  # Specify provider
        model=model,
        api_key=api_key,
        # Note: streaming, seed support depends on provider implementation
    )
    
    # Use complete() method instead of calling instance
    response = ai.complete(
        prompt,
        temperature=temperature,
        # seed=seed,  # If supported by provider
    )
    
    print(response)
    
    # Optional: Check costs
    print(ai.get_cost_summary())
    
    return response
```

## 2. Create Example Script

**New example** (`examples/scitex/ai/genai_example.py`):
```python
#!/usr/bin/env python3
"""Example usage of the new GenAI module."""

from scitex.ai.genai import GenAI, complete, Provider


def basic_completion_example():
    """Basic completion with OpenAI."""
    # Method 1: Using GenAI instance
    ai = GenAI(provider="openai")
    response = ai.complete("What is the capital of France?")
    print(f"Response: {response}")
    print(f"Cost: {ai.get_cost_summary()}")
    
    # Method 2: Using convenience function
    response = complete("What is 2 + 2?", provider="openai")
    print(f"Quick response: {response}")


def conversation_example():
    """Multi-turn conversation example."""
    ai = GenAI(
        provider="anthropic",
        model="claude-3-sonnet-20240229",
        system_prompt="You are a helpful math tutor."
    )
    
    # Have a conversation
    questions = [
        "What is calculus?",
        "Can you give me an example?",
        "How is it used in real life?"
    ]
    
    for question in questions:
        print(f"\nUser: {question}")
        response = ai.complete(question)
        print(f"Assistant: {response}")
    
    # Check conversation history
    print("\n--- Conversation History ---")
    for msg in ai.get_history():
        print(f"{msg.role}: {msg.content[:50]}...")
    
    # Check costs
    print(f"\nTotal cost: {ai.get_cost_summary()}")


def multi_provider_example():
    """Compare responses from different providers."""
    prompt = "Explain quantum computing in one sentence."
    
    providers = ["openai", "anthropic"]
    
    for provider_name in providers:
        try:
            response = complete(prompt, provider=provider_name)
            print(f"\n{provider_name.title()}: {response}")
        except Exception as e:
            print(f"\n{provider_name.title()} error: {e}")


def image_analysis_example():
    """Example with image input (requires vision model)."""
    ai = GenAI(
        provider="openai",
        model="gpt-4-vision-preview"
    )
    
    # Assuming we have a base64 encoded image
    image_data = "your_base64_image_data_here"
    
    response = ai.complete(
        "What objects do you see in this image?",
        images=[f"data:image/jpeg;base64,{image_data}"]
    )
    
    print(f"Image analysis: {response}")


def cost_tracking_example():
    """Detailed cost tracking example."""
    ai = GenAI(provider="openai", model="gpt-4")
    
    # Make several requests
    prompts = [
        "Write a haiku about coding",
        "Explain recursion briefly",
        "What is a binary tree?"
    ]
    
    for prompt in prompts:
        response = ai.complete(prompt)
        print(f"Q: {prompt}")
        print(f"A: {response}\n")
    
    # Get detailed cost information
    costs = ai.get_detailed_costs()
    print(f"Total cost: ${costs['total_cost']:.4f}")
    print(f"Total tokens: {costs['total_tokens']:,}")
    print(f"Requests: {costs['request_count']}")
    print(f"Average cost per request: ${costs['average_cost_per_request']:.4f}")
    
    # Show cost by model
    print("\nCost breakdown by model:")
    for model, stats in costs['cost_by_model'].items():
        print(f"  {model}: ${stats['cost']:.4f} ({stats['requests']} requests)")


def error_handling_example():
    """Example of proper error handling."""
    from scitex.ai.genai import GenAI
    
    # Example 1: Missing API key
    try:
        ai = GenAI(provider="openai")  # No API key provided
        response = ai.complete("Hello")
    except ValueError as e:
        print(f"Configuration error: {e}")
    
    # Example 2: Invalid provider
    try:
        ai = GenAI(provider="invalid_provider", api_key="fake-key")
    except ValueError as e:
        print(f"Provider error: {e}")
    
    # Example 3: API errors
    ai = GenAI(provider="openai", api_key="fake-key")
    try:
        response = ai.complete("Test")
    except Exception as e:
        print(f"API error: {e}")


if __name__ == "__main__":
    print("=== Basic Completion Example ===")
    basic_completion_example()
    
    print("\n=== Conversation Example ===")
    conversation_example()
    
    print("\n=== Multi-Provider Example ===") 
    multi_provider_example()
    
    print("\n=== Cost Tracking Example ===")
    cost_tracking_example()
    
    print("\n=== Error Handling Example ===")
    error_handling_example()
```

## 3. Update Documentation

**Old documentation**:
```python
from scitex.ai._gen_ai import genai_factory

# Create AI instance
ai = genai_factory("gpt-4")
response = ai.run("Hello world")
```

**New documentation**:
```python
from scitex.ai.genai import GenAI

# Create AI instance
ai = GenAI(provider="openai", model="gpt-4")
response = ai.complete("Hello world")
```

## 4. Deprecation Wrapper

For backward compatibility, you could create a deprecation wrapper:

```python
# src/scitex/ai/_gen_ai/_genai_factory.py (compatibility wrapper)
import warnings
from ..genai import GenAI as NewGenAI


def genai_factory(model_or_provider, api_key=None, **kwargs):
    """
    Deprecated: Use scitex.ai.genai.GenAI instead.
    
    This function is provided for backward compatibility only.
    """
    warnings.warn(
        "genai_factory is deprecated. Use scitex.ai.genai.GenAI instead.",
        DeprecationWarning,
        stacklevel=2
    )
    
    # Try to determine provider from model name
    model = model_or_provider
    provider = None
    
    if "gpt" in model.lower():
        provider = "openai"
    elif "claude" in model.lower():
        provider = "anthropic"
    elif "gemini" in model.lower():
        provider = "google"
    elif model.lower() in ["openai", "anthropic", "google", "groq", "deepseek"]:
        provider = model.lower()
        model = None
    
    if not provider:
        raise ValueError(f"Cannot determine provider for model: {model}")
    
    # Create wrapper that mimics old behavior
    class OldStyleWrapper:
        def __init__(self):
            self.ai = NewGenAI(
                provider=provider,
                model=model,
                api_key=api_key,
                **kwargs
            )
            # Copy some attributes for compatibility
            self.messages = self.ai.chat_history.messages
            
        def run(self, prompt, **kwargs):
            """Old method name for compatibility."""
            return self.ai.complete(prompt, **kwargs)
            
        def __call__(self, prompt, **kwargs):
            """Allow calling instance directly."""
            return self.run(prompt, **kwargs)
            
        def calc_costs(self):
            """Old method name for compatibility."""
            costs = self.ai.get_detailed_costs()
            return {
                'total': costs['total_cost'],
                'prompt_tokens': costs['total_prompt_tokens'],
                'completion_tokens': costs['total_completion_tokens']
            }
            
        def reset_messages(self):
            """Old method name for compatibility."""
            self.ai.clear_history()
            
        def __getattr__(self, name):
            """Forward other attributes to new AI instance."""
            return getattr(self.ai, name)
    
    return OldStyleWrapper()
```

## Summary

The key changes when updating code:
1. Import from `scitex.ai.genai` instead of `scitex.ai._gen_ai`
2. Specify provider explicitly
3. Use `complete()` instead of `run()` or calling instance
4. Use new method names for cost tracking and history management
5. Handle errors appropriately
6. Take advantage of new features like detailed cost tracking