#!/usr/bin/env python3
"""Refactored Anthropic provider using component architecture."""

from typing import List, Dict, Any, Generator
import anthropic

from .provider_base import ProviderBase, ProviderConfig


class AnthropicProvider(ProviderBase):
    """Anthropic (Claude) provider implementation."""

    def _init_client(self) -> anthropic.Anthropic:
        """Initialize Anthropic client."""
        client_config = self.auth.get_client_config()
        return anthropic.Anthropic(**client_config)

    def _api_call(self, messages: List[Dict[str, Any]]) -> Any:
        """Make a non-streaming API call to Anthropic."""
        # Extract system prompt if present
        system_prompt = None
        filtered_messages = []

        for msg in messages:
            if msg["role"] == "system":
                system_prompt = msg["content"]
            else:
                filtered_messages.append(msg)

        # Make API call
        response = self.client.messages.create(
            model=self.config.model,
            messages=filtered_messages,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            system=system_prompt or self.config.system_prompt,
            stream=False,
        )

        return response

    def _api_stream(self, messages: List[Dict[str, Any]]) -> Generator[Any, None, None]:
        """Make a streaming API call to Anthropic."""
        # Extract system prompt
        system_prompt = None
        filtered_messages = []

        for msg in messages:
            if msg["role"] == "system":
                system_prompt = msg["content"]
            else:
                filtered_messages.append(msg)

        # Make streaming API call
        stream = self.client.messages.create(
            model=self.config.model,
            messages=filtered_messages,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            system=system_prompt or self.config.system_prompt,
            stream=True,
        )

        for chunk in stream:
            yield chunk

    def _extract_token_counts(self, response: Any) -> tuple[int, int]:
        """Extract token counts from Anthropic response."""
        input_tokens = getattr(response.usage, "input_tokens", 0)
        output_tokens = getattr(response.usage, "output_tokens", 0)
        return input_tokens, output_tokens

    def count_tokens(self, text: str) -> int:
        """Count tokens using Anthropic's tokenizer."""
        # Anthropic doesn't provide a public tokenizer
        # Use approximation for now
        # Claude's tokenization is roughly 1 token per 3.5 characters
        return len(text) // 3


# Example usage:
if __name__ == "__main__":
    # Create configuration
    config = ProviderConfig(
        provider="anthropic",
        model="claude-3-opus-20240229",
        system_prompt="You are a helpful assistant.",
        temperature=0.7,
        max_tokens=1024,
    )

    # Create provider instance
    claude = AnthropicProvider(config)

    # Use it
    messages = [{"role": "user", "content": "Hello, how are you?"}]

    # Non-streaming
    response = claude.complete(messages)
    print(response.content)
    print(f"Tokens: {response.input_tokens} in, {response.output_tokens} out")

    # Streaming
    print("\nStreaming response:")
    for chunk in claude.stream(messages):
        print(chunk, end="", flush=True)

    # Get cost summary
    print("\n\n" + claude.get_cost_summary())
