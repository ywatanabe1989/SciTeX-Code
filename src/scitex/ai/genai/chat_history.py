#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-05-31 10:10:00"
# Author: ywatanabe
# File: ./src/scitex/ai/genai/chat_history.py

"""
Manages conversation history for AI providers.

This module handles chat history management including:
- Message storage and retrieval
- Role alternation enforcement
- System message handling
- History truncation
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from copy import deepcopy


@dataclass
class Message:
    """Represents a single message in chat history.

    Attributes
    ----------
    role : str
        Message role (system, user, assistant)
    content : str
        Message content
    images : Optional[List[str]]
        Optional base64-encoded images
    """

    role: str
    content: str
    images: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary.

        Returns
        -------
        Dict[str, Any]
            Dictionary representation
        """
        d = {"role": self.role, "content": self.content}
        if self.images:
            d["images"] = self.images
        return d


class ChatHistory:
    """Manages conversation history with role enforcement.

    Example
    -------
    >>> history = ChatHistory(n_keep=5)
    >>> history.add_message("user", "Hello")
    >>> history.add_message("assistant", "Hi there!")
    >>> messages = history.get_messages()
    >>> print(len(messages))
    2

    Parameters
    ----------
    system_prompt : Optional[str]
        Optional system prompt to prepend
    n_keep : int
        Number of recent exchanges to keep (default: 1)
    """

    VALID_ROLES = {"system", "user", "assistant"}

    def __init__(self, system_prompt: Optional[str] = None, n_keep: int = 1):
        """Initialize chat history manager.

        Parameters
        ----------
        system_prompt : Optional[str]
            Optional system prompt
        n_keep : int
            Number of recent exchanges to keep (-1 to keep all)
        """
        self.system_prompt = system_prompt or ""
        self.n_keep = n_keep
        self.messages: List[Message] = []

        # Add system message if provided
        if system_prompt:
            self.messages.append(Message(role="system", content=system_prompt))

    def add_message(
        self, role: str, content: str, images: Optional[List[str]] = None
    ) -> None:
        """Add a message to the history.

        Parameters
        ----------
        role : str
            Message role ("user", "assistant", "system")
        content : str
            Message content
        images : Optional[List[str]]
            Optional images for multimodal messages

        Raises
        ------
        ValueError
            If role is invalid
        """
        if role not in self.VALID_ROLES:
            raise ValueError(f"Invalid role: {role}. Must be one of {self.VALID_ROLES}")

        # Don't add duplicate system messages
        if role == "system" and self.messages and self.messages[0].role == "system":
            self.messages[0] = Message(role=role, content=content)
            return

        self.messages.append(Message(role=role, content=content, images=images))
        self._trim_history()

    def _trim_history(self) -> None:
        """Trim history to n_keep exchanges."""
        if self.n_keep == -1:
            return

        # Count system message
        has_system = self.messages and self.messages[0].role == "system"
        start_idx = 1 if has_system else 0

        # Keep only last n_keep exchanges (2 messages per exchange)
        if len(self.messages) - start_idx > self.n_keep * 2:
            kept_messages = self.messages[-self.n_keep * 2 :]
            if has_system:
                self.messages = [self.messages[0]] + kept_messages
            else:
                self.messages = kept_messages

    def format_for_api(self, provider: str) -> List[Dict[str, Any]]:
        """Format messages for specific provider API.

        Parameters
        ----------
        provider : str
            Provider name (openai, anthropic, google)

        Returns
        -------
        List[Dict[str, Any]]
            Formatted messages
        """
        provider = provider.lower()

        if provider == "openai":
            return self._format_for_openai()
        elif provider == "anthropic":
            return self._format_for_anthropic()
        elif provider == "google":
            return self._format_for_google()
        else:
            # Default format
            return [msg.to_dict() for msg in self.messages]

    def _format_for_openai(self) -> List[Dict[str, Any]]:
        """Format messages for OpenAI API."""
        formatted = []

        for msg in self.messages:
            if msg.images:
                # Multimodal message
                content = [{"type": "text", "text": msg.content}]
                for img in msg.images:
                    content.append(
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{img}"},
                        }
                    )
                formatted.append({"role": msg.role, "content": content})
            else:
                formatted.append({"role": msg.role, "content": msg.content})

        return formatted

    def _format_for_anthropic(self) -> List[Dict[str, Any]]:
        """Format messages for Anthropic API (excludes system)."""
        formatted = []

        for msg in self.messages:
            if msg.role == "system":
                continue  # Anthropic handles system separately
            formatted.append({"role": msg.role, "content": msg.content})

        return formatted

    def _format_for_google(self) -> List[Dict[str, Any]]:
        """Format messages for Google API."""
        formatted = []

        for msg in self.messages:
            if msg.images:
                parts = [{"text": msg.content}]
                for img in msg.images:
                    parts.append(
                        {"inline_data": {"mime_type": "image/jpeg", "data": img}}
                    )
                formatted.append({"role": msg.role, "parts": parts})
            else:
                formatted.append({"role": msg.role, "parts": [{"text": msg.content}]})

        return formatted

    def ensure_valid_sequence(self) -> None:
        """Ensure messages follow valid sequence rules.

        - Must start with user message (after system)
        - Must alternate between user and assistant
        """
        if not self.messages:
            return

        # Skip system message if present
        start_idx = 1 if self.messages and self.messages[0].role == "system" else 0

        # Ensure starts with user
        if (
            len(self.messages) > start_idx
            and self.messages[start_idx].role == "assistant"
        ):
            self.messages.insert(start_idx, Message(role="user", content="Hello"))

        # Ensure alternating
        i = start_idx
        while i < len(self.messages) - 1:
            current = self.messages[i]
            next_msg = self.messages[i + 1]

            if current.role == next_msg.role:
                # Insert appropriate message
                if current.role == "user":
                    self.messages.insert(
                        i + 1, Message(role="assistant", content="...")
                    )
                else:
                    self.messages.insert(i + 1, Message(role="user", content="..."))
            i += 1

    def clear(self) -> None:
        """Clear history, keeping only system message if present."""
        if self.messages and self.messages[0].role == "system":
            self.messages = [self.messages[0]]
        else:
            self.messages = []

    def get_messages(self) -> List[Message]:
        """Get copy of messages.

        Returns
        -------
        List[Message]
            Copy of message list
        """
        return deepcopy(self.messages)

    def __len__(self) -> int:
        """Get number of messages in history."""
        return len(self.messages)

    def __repr__(self) -> str:
        """String representation of ChatHistory."""
        return f"ChatHistory(messages={len(self.messages)}, n_keep={self.n_keep})"


# Backward compatibility aliases
def get_history(self) -> List[Dict[str, Any]]:
    """Get history as list of dicts (backward compatibility)."""
    return [msg.to_dict() for msg in self.messages]


def ensure_alternating(self) -> None:
    """Ensure alternating messages (backward compatibility)."""
    self.ensure_valid_sequence()


def ensure_user_first(self) -> None:
    """Ensure user first (backward compatibility)."""
    self.ensure_valid_sequence()


def reset(self, system_message: Optional[str] = None) -> None:
    """Reset history (backward compatibility)."""
    self.clear()
    if system_message:
        self.system_prompt = system_message
        self.messages.append(Message(role="system", content=system_message))


# Add backward compatibility methods to ChatHistory
ChatHistory.get_history = get_history
ChatHistory.ensure_alternating = ensure_alternating
ChatHistory.ensure_user_first = ensure_user_first
ChatHistory.reset = reset


# EOF
