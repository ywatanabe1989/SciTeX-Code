#!/usr/bin/env python3
"""Tests for cost_tracker module."""

import pytest
from unittest.mock import patch, MagicMock
from scitex.ai.genai.cost_tracker import CostTracker


class TestCostTracker:
    """Test cases for CostTracker class."""

    def test_init(self):
        """Test initialization."""
        tracker = CostTracker("openai", "gpt-4")
        assert tracker.provider == "openai"
        assert tracker.model == "gpt-4"
        assert tracker.input_tokens == 0
        assert tracker.output_tokens == 0
        assert tracker.session_input_tokens == 0
        assert tracker.session_output_tokens == 0

    def test_update(self):
        """Test updating token counts."""
        tracker = CostTracker("openai", "gpt-4")

        # First update
        tracker.update(100, 200)
        assert tracker.input_tokens == 100
        assert tracker.output_tokens == 200
        assert tracker.session_input_tokens == 100
        assert tracker.session_output_tokens == 200

        # Second update
        tracker.update(50, 75)
        assert tracker.input_tokens == 150
        assert tracker.output_tokens == 275
        assert tracker.session_input_tokens == 150
        assert tracker.session_output_tokens == 275

    @patch("scitex.ai.genai.cost_tracker.calc_cost")
    def test_calculate_cost(self, mock_calc_cost):
        """Test cost calculation."""
        mock_calc_cost.return_value = 0.0125

        tracker = CostTracker("openai", "gpt-4")
        tracker.update(1000, 500)

        cost = tracker.calculate_cost()

        mock_calc_cost.assert_called_once_with(
            model="gpt-4", input_tokens=1000, output_tokens=500
        )
        assert cost == 0.0125

    @patch("scitex.ai.genai.cost_tracker.calc_cost")
    def test_calculate_session_cost(self, mock_calc_cost):
        """Test session cost calculation."""
        mock_calc_cost.return_value = 0.005

        tracker = CostTracker("anthropic", "claude-3")
        tracker.update(500, 250)

        session_cost = tracker.calculate_session_cost()

        mock_calc_cost.assert_called_with(
            model="claude-3", input_tokens=500, output_tokens=250
        )
        assert session_cost == 0.005

    def test_reset_session(self):
        """Test resetting session counters."""
        tracker = CostTracker("openai", "gpt-4")
        tracker.update(100, 200)

        # Verify counts before reset
        assert tracker.input_tokens == 100
        assert tracker.session_input_tokens == 100

        # Reset session
        tracker.reset_session()

        # Total counts should remain, session should be zero
        assert tracker.input_tokens == 100
        assert tracker.output_tokens == 200
        assert tracker.session_input_tokens == 0
        assert tracker.session_output_tokens == 0

    def test_get_usage_stats(self):
        """Test getting usage statistics."""
        tracker = CostTracker("openai", "gpt-3.5-turbo")
        tracker.update(100, 200)
        tracker.update(50, 100)

        stats = tracker.get_usage_stats()

        assert stats["total_input_tokens"] == 150
        assert stats["total_output_tokens"] == 300
        assert stats["total_tokens"] == 450
        assert stats["session_input_tokens"] == 150
        assert stats["session_output_tokens"] == 300
        assert stats["session_total_tokens"] == 450

    def test_session_vs_total_tracking(self):
        """Test that session and total are tracked separately."""
        tracker = CostTracker("openai", "gpt-4")

        # First session
        tracker.update(100, 200)
        tracker.reset_session()

        # Second session
        tracker.update(50, 75)

        stats = tracker.get_usage_stats()

        # Total should include all
        assert stats["total_input_tokens"] == 150
        assert stats["total_output_tokens"] == 275

        # Session should only include current
        assert stats["session_input_tokens"] == 50
        assert stats["session_output_tokens"] == 75

    @patch("scitex.ai.genai.cost_tracker.calc_cost")
    def test_format_cost_summary(self, mock_calc_cost):
        """Test formatting cost summary."""
        # Mock different costs for total and session
        mock_calc_cost.side_effect = [0.0125, 0.005]

        tracker = CostTracker("openai", "gpt-4")
        tracker.update(1000, 500)
        tracker.reset_session()
        tracker.update(500, 250)

        summary = tracker.format_cost_summary()

        assert "openai - gpt-4" in summary
        assert "1,500" in summary  # Total input tokens
        assert "750" in summary  # Total output tokens
        assert "$0.0125" in summary  # Total cost
        assert "500" in summary  # Session input tokens
        assert "250" in summary  # Session output tokens
        assert "$0.0050" in summary  # Session cost

    def test_repr(self):
        """Test string representation."""
        with patch("scitex.ai.genai.cost_tracker.calc_cost", return_value=0.0075):
            tracker = CostTracker("anthropic", "claude-3")
            tracker.update(500, 250)

            repr_str = repr(tracker)

            assert "CostTracker" in repr_str
            assert "anthropic" in repr_str
            assert "claude-3" in repr_str
            assert "$0.0075" in repr_str
