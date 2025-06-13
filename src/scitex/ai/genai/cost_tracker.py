#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-05-31 10:15:00"
# Author: ywatanabe
# File: ./src/scitex/ai/genai/cost_tracker.py

"""
Tracks token usage and costs for AI API calls.

This module provides cost tracking functionality including:
- Token counting for input/output
- Cost calculation based on model pricing
- Usage statistics aggregation
"""

from typing import Dict, Optional, List, Any
from dataclasses import dataclass, field

from .calc_cost import calc_cost


@dataclass
class TokenUsage:
    """Token usage statistics.

    Attributes
    ----------
    input_tokens : int
        Total input tokens used
    output_tokens : int
        Total output tokens used
    total_tokens : int
        Total tokens (input + output)
    """

    input_tokens: int = 0
    output_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        """Get total token count."""
        return self.input_tokens + self.output_tokens


class CostTracker:
    """Tracks token usage and associated costs.

    Example
    -------
    >>> tracker = CostTracker("openai", "gpt-4")
    >>> tracker.update(input_tokens=100, output_tokens=50)
    >>> cost = tracker.calculate_cost()
    >>> print(f"Total cost: ${cost:.4f}")
    Total cost: $0.0045

    Parameters
    ----------
    provider : str
        The provider name (e.g., "openai", "anthropic")
    model : str
        The model name for cost calculation
    """

    def __init__(self, provider: str, model: str):
        """Initialize cost tracker.

        Parameters
        ----------
        provider : str
            The provider name
        model : str
            The model name
        """
        self.provider = provider
        self.model = model

        # Total token counters
        self.input_tokens = 0
        self.output_tokens = 0

        # Session token counters
        self.session_input_tokens = 0
        self.session_output_tokens = 0

        # Token history for detailed tracking
        self._history: List[TokenUsage] = []

        # Request counter
        self.request_count = 0

    # Properties for backward compatibility
    @property
    def total_prompt_tokens(self) -> int:
        """Get total prompt (input) tokens."""
        return self.input_tokens

    @property
    def total_completion_tokens(self) -> int:
        """Get total completion (output) tokens."""
        return self.output_tokens

    @property
    def total_cost(self) -> float:
        """Get total cost."""
        return self.calculate_cost()

    def update(self, input_tokens: int, output_tokens: int) -> None:
        """Update token counts.

        Parameters
        ----------
        input_tokens : int
            Number of input tokens to add
        output_tokens : int
            Number of output tokens to add
        """
        # Update total counters
        self.input_tokens += input_tokens
        self.output_tokens += output_tokens

        # Update session counters
        self.session_input_tokens += input_tokens
        self.session_output_tokens += output_tokens

        # Record in history
        usage = TokenUsage(input_tokens=input_tokens, output_tokens=output_tokens)
        self._history.append(usage)

        # Increment request count
        self.request_count += 1

    def track_usage(self, model: str, usage: TokenUsage) -> None:
        """Track usage (for backward compatibility).

        Parameters
        ----------
        model : str
            Model name (ignored, uses instance model)
        usage : TokenUsage
            Token usage to track
        """
        self.update(usage.input_tokens, usage.output_tokens)

    def calculate_cost(self) -> float:
        """Calculate total cost based on token usage.

        Returns
        -------
        float
            Total cost in USD
        """
        return calc_cost(
            model=self.model,
            input_tokens=self.input_tokens,
            output_tokens=self.output_tokens,
        )

    def calculate_session_cost(self) -> float:
        """Calculate session cost based on session token usage.

        Returns
        -------
        float
            Session cost in USD
        """
        return calc_cost(
            model=self.model,
            input_tokens=self.session_input_tokens,
            output_tokens=self.session_output_tokens,
        )

    def reset_session(self) -> None:
        """Reset session counters while keeping totals."""
        self.session_input_tokens = 0
        self.session_output_tokens = 0

    def reset(self) -> None:
        """Reset all token usage and cost tracking."""
        self.input_tokens = 0
        self.output_tokens = 0
        self.session_input_tokens = 0
        self.session_output_tokens = 0
        self._history = []

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get comprehensive usage statistics.

        Returns
        -------
        Dict[str, Any]
            Dictionary containing usage statistics
        """
        return {
            "total_input_tokens": self.input_tokens,
            "total_output_tokens": self.output_tokens,
            "total_tokens": self.input_tokens + self.output_tokens,
            "session_input_tokens": self.session_input_tokens,
            "session_output_tokens": self.session_output_tokens,
            "session_total_tokens": self.session_input_tokens
            + self.session_output_tokens,
        }

    def get_summary(self) -> str:
        """Get a cost summary (alias for format_cost_summary).

        Returns
        -------
        str
            Formatted cost summary
        """
        return self.format_cost_summary()

    def format_cost_summary(self) -> str:
        """Format a human-readable cost summary.

        Returns
        -------
        str
            Formatted cost summary
        """
        total_cost = self.calculate_cost()
        session_cost = self.calculate_session_cost()

        return (
            f"Cost Summary for {self.provider} - {self.model}\n"
            f"{'=' * 50}\n"
            f"Total Usage:\n"
            f"  Input tokens:  {self.input_tokens:,}\n"
            f"  Output tokens: {self.output_tokens:,}\n"
            f"  Total tokens:  {self.input_tokens + self.output_tokens:,}\n"
            f"  Total cost:    ${total_cost:.4f}\n"
            f"\n"
            f"Session Usage:\n"
            f"  Input tokens:  {self.session_input_tokens:,}\n"
            f"  Output tokens: {self.session_output_tokens:,}\n"
            f"  Total tokens:  {self.session_input_tokens + self.session_output_tokens:,}\n"
            f"  Session cost:  ${session_cost:.4f}\n"
        )

    def get_detailed_report(self) -> Dict[str, Any]:
        """Get a detailed cost and usage report.

        Returns
        -------
        Dict[str, Any]
            Comprehensive report including usage, costs, and statistics
        """
        return {
            "provider": self.provider,
            "model": self.model,
            "total_cost": self.calculate_cost(),
            "session_cost": self.calculate_session_cost(),
            "usage_stats": self.get_usage_stats(),
            "num_api_calls": len(self._history),
            "average_per_call": {
                "input_tokens": (
                    self.input_tokens / len(self._history) if self._history else 0
                ),
                "output_tokens": (
                    self.output_tokens / len(self._history) if self._history else 0
                ),
            },
        }

    def __repr__(self) -> str:
        """String representation of CostTracker."""
        cost = self.calculate_cost()
        return (
            f"CostTracker(provider={self.provider}, "
            f"model={self.model}, "
            f"total_tokens={self.input_tokens + self.output_tokens}, "
            f"cost=${cost:.4f})"
        )


# EOF
