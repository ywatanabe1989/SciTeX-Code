#!/usr/bin/env python3
"""Tests for chat_history module."""

import pytest
from scitex.ai.genai.chat_history import ChatHistory, Message


class TestMessage:
    """Test cases for Message dataclass."""

    def test_message_creation(self):
        """Test creating a message."""
        msg = Message(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"
        assert msg.images is None

    def test_message_with_images(self):
        """Test creating a message with images."""
        images = ["base64image1", "base64image2"]
        msg = Message(role="user", content="What is this?", images=images)
        assert msg.images == images

    def test_message_to_dict(self):
        """Test converting message to dictionary."""
        msg = Message(role="assistant", content="I can help")
        d = msg.to_dict()
        assert d == {"role": "assistant", "content": "I can help"}

        # With images
        msg_with_img = Message(role="user", content="Look", images=["img1"])
        d2 = msg_with_img.to_dict()
        assert d2 == {"role": "user", "content": "Look", "images": ["img1"]}


class TestChatHistory:
    """Test cases for ChatHistory class."""

    def test_init_empty(self):
        """Test initialization with no system prompt."""
        history = ChatHistory()
        assert len(history) == 0
        assert history.system_prompt == ""
        assert history.n_keep == 1

    def test_init_with_system_prompt(self):
        """Test initialization with system prompt."""
        history = ChatHistory(system_prompt="You are helpful")
        assert len(history) == 1
        assert history.messages[0].role == "system"
        assert history.messages[0].content == "You are helpful"

    def test_add_message(self):
        """Test adding messages."""
        history = ChatHistory()

        history.add_message("user", "Hello")
        assert len(history) == 1
        assert history.messages[0].content == "Hello"

        history.add_message("assistant", "Hi there")
        assert len(history) == 2
        assert history.messages[1].content == "Hi there"

    def test_add_message_invalid_role(self):
        """Test adding message with invalid role."""
        history = ChatHistory()

        with pytest.raises(ValueError, match="Invalid role"):
            history.add_message("invalid", "test")

    def test_trim_history(self):
        """Test history trimming with n_keep."""
        history = ChatHistory(n_keep=2)

        # Add more than n_keep exchanges
        for i in range(5):
            history.add_message("user", f"Question {i}")
            history.add_message("assistant", f"Answer {i}")

        # Should only keep last 2 exchanges (4 messages)
        assert len(history) == 4
        assert history.messages[0].content == "Question 3"
        assert history.messages[-1].content == "Answer 4"

    def test_trim_history_with_system(self):
        """Test that system message is preserved during trimming."""
        history = ChatHistory(system_prompt="System", n_keep=1)

        # Add multiple exchanges
        for i in range(3):
            history.add_message("user", f"Q{i}")
            history.add_message("assistant", f"A{i}")

        # Should keep system + last exchange
        assert len(history) == 3  # system + 1 exchange
        assert history.messages[0].role == "system"
        assert history.messages[1].content == "Q2"
        assert history.messages[2].content == "A2"

    def test_keep_all_messages(self):
        """Test n_keep=-1 keeps all messages."""
        history = ChatHistory(n_keep=-1)

        for i in range(10):
            history.add_message("user", f"Message {i}")

        assert len(history) == 10

    def test_format_for_openai(self):
        """Test formatting for OpenAI API."""
        history = ChatHistory(system_prompt="Be helpful")
        history.add_message("user", "Hello")
        history.add_message("assistant", "Hi!")

        formatted = history.format_for_api("openai")

        assert len(formatted) == 3
        assert formatted[0] == {"role": "system", "content": "Be helpful"}
        assert formatted[1] == {"role": "user", "content": "Hello"}
        assert formatted[2] == {"role": "assistant", "content": "Hi!"}

    def test_format_for_openai_with_images(self):
        """Test formatting multimodal messages for OpenAI."""
        history = ChatHistory()
        history.add_message("user", "What is this?", images=["imgdata"])

        formatted = history.format_for_api("openai")

        assert len(formatted) == 1
        msg = formatted[0]
        assert msg["role"] == "user"
        assert isinstance(msg["content"], list)
        assert len(msg["content"]) == 2
        assert msg["content"][0] == {"type": "text", "text": "What is this?"}
        assert msg["content"][1]["type"] == "image_url"
        assert "base64,imgdata" in msg["content"][1]["image_url"]["url"]

    def test_format_for_anthropic(self):
        """Test formatting for Anthropic API."""
        history = ChatHistory(system_prompt="Be helpful")
        history.add_message("user", "Hello")
        history.add_message("assistant", "Hi!")

        formatted = history.format_for_api("anthropic")

        # Anthropic doesn't include system in messages
        assert len(formatted) == 2
        assert formatted[0] == {"role": "user", "content": "Hello"}
        assert formatted[1] == {"role": "assistant", "content": "Hi!"}

    def test_format_for_google(self):
        """Test formatting for Google API."""
        history = ChatHistory()
        history.add_message("user", "Hello", images=["imgdata"])

        formatted = history.format_for_api("google")

        assert len(formatted) == 1
        msg = formatted[0]
        assert msg["role"] == "user"
        assert "parts" in msg
        assert len(msg["parts"]) == 2
        assert msg["parts"][0] == {"text": "Hello"}
        assert msg["parts"][1]["inline_data"]["data"] == "imgdata"

    def test_ensure_valid_sequence(self):
        """Test ensuring alternating user/assistant messages."""
        history = ChatHistory()

        # Add two user messages in a row
        history.messages.append(Message("user", "First"))
        history.messages.append(Message("user", "Second"))

        history.ensure_valid_sequence()

        # Should have inserted assistant message
        assert len(history) == 3
        assert history.messages[1].role == "assistant"
        assert history.messages[1].content == "..."

    def test_ensure_valid_sequence_start_with_assistant(self):
        """Test ensuring sequence starts with user."""
        history = ChatHistory()
        history.messages.append(Message("assistant", "I start"))

        history.ensure_valid_sequence()

        assert len(history) == 2
        assert history.messages[0].role == "user"
        assert history.messages[0].content == "Hello"

    def test_clear(self):
        """Test clearing history."""
        history = ChatHistory(system_prompt="System")
        history.add_message("user", "Hello")
        history.add_message("assistant", "Hi")

        history.clear()

        # Should only keep system message
        assert len(history) == 1
        assert history.messages[0].role == "system"

    def test_get_messages(self):
        """Test getting copy of messages."""
        history = ChatHistory()
        history.add_message("user", "Test")

        messages = history.get_messages()

        # Should be a copy
        messages[0].content = "Modified"
        assert history.messages[0].content == "Test"

    def test_repr(self):
        """Test string representation."""
        history = ChatHistory(n_keep=5)
        history.add_message("user", "Test")

        repr_str = repr(history)
        assert "ChatHistory" in repr_str
        assert "messages=1" in repr_str
        assert "n_keep=5" in repr_str
