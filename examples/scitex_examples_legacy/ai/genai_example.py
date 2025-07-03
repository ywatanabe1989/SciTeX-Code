#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-31 20:00:00 (ywatanabe)"
# File: ./examples/scitex/ai/genai_example.py
# ----------------------------------------
import os

__FILE__ = "./examples/scitex/ai/genai_example.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - Demonstrates basic GenAI completions with different providers
  - Shows multi-turn conversations and chat history management
  - Tracks cost and token usage across requests
  - Handles errors gracefully (missing API keys, invalid providers)
  - Compares responses from multiple AI providers
  - Shows type-safe provider usage with enums

Dependencies:
  - scripts: None
  - packages: scitex, os

IO:
  - input-files: None
  - output-files: None (console output only)
"""

"""Imports"""
import argparse

"""Warnings"""
# scitex.pd.ignore_SettingWithCopyWarning()
# warnings.simplefilter("ignore", UserWarning)

"""Parameters"""
# from scitex.io import load_configs
# CONFIG = load_configs()


def basic_completion_example():
    """Basic completion with OpenAI."""
    from scitex.ai.genai import GenAI, complete

    print("=== Basic Completion Example ===")

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
    from scitex.ai.genai import GenAI

    print("\n=== Conversation Example ===")

    ai = GenAI(
        provider="anthropic",
        model="claude-3-sonnet-20240229",
        system_prompt="You are a helpful math tutor.",
    )

    # Have a conversation
    questions = [
        "What is calculus?",
        "Can you give me an example?",
        "How is it used in real life?",
    ]

    for question in questions:
        print(f"\nUser: {question}")
        response = ai.complete(question)
        print(f"Assistant: {response[:100]}...")  # Truncate for display

    # Check conversation history
    print("\n--- Conversation History ---")
    for i, msg in enumerate(ai.get_history()):
        print(f"{i}. {msg.role}: {msg.content[:50]}...")

    # Check costs
    print(f"\nTotal: {ai.get_cost_summary()}")


def multi_provider_example():
    """Compare responses from different providers."""
    from scitex.ai.genai import complete

    print("\n=== Multi-Provider Example ===")

    prompt = "Explain quantum computing in one sentence."

    providers = ["openai", "anthropic"]

    for provider_name in providers:
        try:
            response = complete(prompt, provider=provider_name)
            print(f"\n{provider_name.title()}: {response}")
        except Exception as e:
            print(f"\n{provider_name.title()} error: {e}")


def cost_tracking_example():
    """Detailed cost tracking example."""
    from scitex.ai.genai import GenAI

    print("\n=== Cost Tracking Example ===")

    ai = GenAI(provider="openai", model="gpt-4")

    # Make several requests
    prompts = [
        "Write a haiku about coding",
        "Explain recursion briefly",
        "What is a binary tree?",
    ]

    for prompt in prompts:
        response = ai.complete(prompt)
        print(f"\nQ: {prompt}")
        print(f"A: {response}")

    # Get detailed cost information
    costs = ai.get_detailed_costs()
    print(f"\n--- Cost Summary ---")
    print(f"Total cost: ${costs['total_cost']:.4f}")
    print(f"Total tokens: {costs['total_tokens']:,}")
    print(f"Requests: {costs['request_count']}")

    if costs["request_count"] > 0:
        print(f"Average cost per request: ${costs['average_cost_per_request']:.4f}")

    # Show cost by model
    if costs["cost_by_model"]:
        print("\nCost breakdown by model:")
        for model, stats in costs["cost_by_model"].items():
            print(f"  {model}: ${stats['cost']:.4f} ({stats['requests']} requests)")


def error_handling_example():
    """Example of proper error handling."""
    import os
    from scitex.ai.genai import GenAI

    print("\n=== Error Handling Example ===")

    # Example 1: Missing API key
    print("\n1. Missing API key:")
    try:
        # Remove API key from environment temporarily
        old_key = os.environ.pop("OPENAI_API_KEY", None)
        ai = GenAI(provider="openai")  # No API key provided
        response = ai.complete("Hello")
    except ValueError as e:
        print(f"   Configuration error: {e}")
    finally:
        # Restore API key if it existed
        if old_key:
            os.environ["OPENAI_API_KEY"] = old_key

    # Example 2: Invalid provider
    print("\n2. Invalid provider:")
    try:
        ai = GenAI(provider="invalid_provider", api_key="fake-key")
    except ValueError as e:
        print(f"   Provider error: {e}")

    # Example 3: API errors (using fake key)
    print("\n3. API error with invalid key:")
    ai = GenAI(provider="openai", api_key="sk-fake-key-for-testing")
    try:
        response = ai.complete("Test")
    except Exception as e:
        print(f"   API error: {type(e).__name__}: {str(e)[:100]}...")


def streaming_example():
    """Example of streaming responses (if implemented)."""
    from scitex.ai.genai import GenAI

    print("\n=== Streaming Example ===")

    ai = GenAI(provider="openai")

    try:
        # Note: This will raise NotImplementedError until streaming is implemented
        print("Streaming response: ", end="", flush=True)
        for chunk in ai.stream("Tell me a short story"):
            print(chunk, end="", flush=True)
        print()  # New line at end
    except NotImplementedError:
        print("Streaming not yet implemented in this version")


def image_analysis_example():
    """Example with image input (requires vision model)."""
    from scitex.ai.genai import GenAI

    print("\n=== Image Analysis Example ===")

    # This requires a vision-capable model
    try:
        ai = GenAI(provider="openai", model="gpt-4-vision-preview")

        # For demo, we'll use a placeholder
        # In real usage, you would load and encode an actual image
        print("Note: Image analysis requires actual image data")
        print("Example code:")
        print(
            """
    # Load and encode image
    with open("image.jpg", "rb") as f:
        import base64
        image_data = base64.b64encode(f.read()).decode()
    
    response = ai.complete(
        "What objects do you see in this image?",
        images=[f"data:image/jpeg;base64,{image_data}"]
    )
    print(f"Image analysis: {response}")
        """
        )
    except Exception as e:
        print(f"Error setting up vision model: {e}")


def type_safe_provider_example():
    """Example using type-safe Provider enum."""
    from scitex.ai.genai import GenAI, Provider

    print("\n=== Type-Safe Provider Example ===")

    # Using the Provider enum for type safety
    ai = GenAI(provider=Provider.OPENAI)
    response = ai.complete("Hello from type-safe provider!")
    print(f"Response: {response}")

    # The enum helps catch typos at development time
    print("Available providers:")
    for provider in Provider:
        print(f"  - {provider.value}")


"""Functions & Classes"""


def main(args):
    """Run all examples."""
    print("SciTeX GenAI Module Examples")
    print("=" * 50)

    # Note: These examples will only work if you have API keys set
    # Set environment variables:
    # - OPENAI_API_KEY for OpenAI examples
    # - ANTHROPIC_API_KEY for Anthropic examples

    # Check for API keys
    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    has_anthropic = bool(os.getenv("ANTHROPIC_API_KEY"))

    if not has_openai and not has_anthropic:
        print("\nNote: No API keys found in environment.")
        print("Set OPENAI_API_KEY and/or ANTHROPIC_API_KEY to run examples.")
        print("\nRunning examples that don't require API calls...")

        error_handling_example()
        type_safe_provider_example()
        return 0

    # Run examples based on available API keys
    if has_openai:
        try:
            basic_completion_example()
            cost_tracking_example()
            streaming_example()
            image_analysis_example()
        except Exception as e:
            print(f"OpenAI example error: {e}")

    if has_anthropic:
        try:
            conversation_example()
        except Exception as e:
            print(f"Anthropic example error: {e}")

    if has_openai and has_anthropic:
        try:
            multi_provider_example()
        except Exception as e:
            print(f"Multi-provider example error: {e}")

    # Always run these
    error_handling_example()
    type_safe_provider_example()

    return 0


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    import scitex

    script_mode = scitex.gen.is_script()
    parser = argparse.ArgumentParser(description="SciTeX GenAI module examples")
    args = parser.parse_args()
    scitex.str.printc(args, c="yellow")
    return args


def run_main() -> None:
    """Initialize scitex framework, run main function, and cleanup."""
    global CONFIG, CC, sys, plt

    import sys
    import matplotlib.pyplot as plt
    import scitex

    args = parse_args()

    # Start scitex framework
    CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(
        sys,
        plt,
        args=args,
        file=__FILE__,
        verbose=False,
        agg=True,
    )

    # Main
    exit_status = main(args)

    # Close the scitex framework
    scitex.gen.close(
        CONFIG,
        verbose=False,
        notify=False,
        message="",
        exit_status=exit_status,
    )


if __name__ == "__main__":
    run_main()

# EOF
