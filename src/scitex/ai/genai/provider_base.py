#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-15 12:00:00"
# Author: Yusuke Watanabe (ywatanabe@alumni.u-tokyo.ac.jp)

"""
Provider base implementation using composition pattern.

This module provides the concrete base class that combines all components
to implement the provider interface.
"""

import warnings
from dataclasses import dataclass
from typing import Any, Dict, Iterator, List, Optional, Union

from .auth_manager import AuthManager
from .base_provider import BaseProvider
from .chat_history import ChatHistory
from .cost_tracker import CostTracker, TokenUsage
from .image_processor import ImageProcessor
from .model_registry import ModelInfo, ModelRegistry
from .response_handler import ResponseHandler


@dataclass
class ProviderConfig:
    """Configuration for provider initialization."""

    api_key: Optional[str] = None
    model: str = "gpt-3.5-turbo"
    system_prompt: Optional[str] = None
    stream: bool = False
    seed: Optional[int] = None
    max_tokens: Optional[int] = None
    temperature: float = 0.0
    n_draft: int = 1
    kwargs: Optional[Dict[str, Any]] = None


class ProviderBase(BaseProvider):
    """
    Base implementation using composition pattern.

    This class combines all components to provide a complete implementation
    of the provider interface. Concrete providers should inherit from this
    class and implement provider-specific methods.
    """

    def __init__(
        self,
        provider_name: str,
        config: ProviderConfig,
        auth_manager: Optional[AuthManager] = None,
        model_registry: Optional[ModelRegistry] = None,
        chat_history: Optional[ChatHistory] = None,
        cost_tracker: Optional[CostTracker] = None,
        response_handler: Optional[ResponseHandler] = None,
        image_processor: Optional[ImageProcessor] = None,
    ):
        """Initialize provider with components."""
        self.provider_name = provider_name
        self.config = config

        # Initialize components
        self.auth_manager = auth_manager or AuthManager()
        self.model_registry = model_registry or ModelRegistry()
        self.chat_history = chat_history or ChatHistory()
        self.cost_tracker = cost_tracker or CostTracker()
        self.response_handler = response_handler or ResponseHandler()
        self.image_processor = image_processor or ImageProcessor()

        # Get and validate API key
        self.api_key = self.auth_manager.get_api_key(provider_name, config.api_key)

        # Initialize provider-specific attributes
        self.model = config.model
        self.system_prompt = config.system_prompt
        self.stream = config.stream
        self.seed = config.seed
        self.max_tokens = config.max_tokens
        self.temperature = config.temperature
        self.n_draft = config.n_draft
        self.kwargs = config.kwargs or {}

        # Get model info
        self.model_info = self._get_model_info()

    def _get_model_info(self) -> ModelInfo:
        """Get model information from registry."""
        model_info = self.model_registry.get_model_info(self.model)
        if not model_info:
            # Create default model info if not found
            model_info = ModelInfo(
                name=self.model,
                provider=self.provider_name,
                max_tokens=4096,  # Default
                supports_images=False,
                supports_streaming=True,
            )
            warnings.warn(
                f"Model {self.model} not found in registry. Using defaults.",
                UserWarning,
            )
        return model_info

    def call(
        self,
        messages: Union[str, List[Dict[str, Any]]],
        **kwargs: Any,
    ) -> Union[str, Iterator[str]]:
        """
        Main method to interact with the AI provider.

        Parameters
        ----------
        messages : Union[str, List[Dict[str, Any]]]
            Input messages or prompt
        **kwargs : Any
            Additional parameters for the API call

        Returns
        -------
        Union[str, Iterator[str]]
            Response text or streaming iterator
        """
        # Merge kwargs with instance kwargs
        call_kwargs = {**self.kwargs, **kwargs}

        # Process messages
        processed_messages = self._process_messages(messages)

        # Add system prompt if provided
        if self.system_prompt:
            processed_messages = self._add_system_prompt(processed_messages)

        # Process images if present
        processed_messages = self._process_images_in_messages(processed_messages)

        # Store messages in history
        for msg in processed_messages:
            if msg["role"] != "system":
                self.chat_history.add_message(msg["role"], msg["content"])

        # Ensure alternating messages
        self.chat_history.ensure_alternating()

        # Make API call (to be implemented by concrete providers)
        response = self._make_api_call(processed_messages, **call_kwargs)

        # Handle response based on stream mode
        if self.stream:
            return self._handle_streaming_response(response)
        else:
            return self._handle_static_response(response)

    def _process_messages(
        self, messages: Union[str, List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """Process input messages into standard format."""
        if isinstance(messages, str):
            return [{"role": "user", "content": messages}]
        return messages

    def _add_system_prompt(
        self, messages: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Add system prompt to messages."""
        if messages and messages[0]["role"] == "system":
            # Replace existing system prompt
            messages[0]["content"] = self.system_prompt
        else:
            # Insert system prompt at beginning
            messages.insert(0, {"role": "system", "content": self.system_prompt})
        return messages

    def _process_images_in_messages(
        self, messages: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Process images in messages if model supports it."""
        if not self.model_info.supports_images:
            return messages

        processed_messages = []
        for msg in messages:
            if isinstance(msg.get("content"), list):
                # Process multimodal content
                processed_content = []
                for item in msg["content"]:
                    if item.get("type") == "image" and "path" in item:
                        # Process image file
                        image_data = self.image_processor.process_image(
                            item["path"], max_size=item.get("max_size", 2048)
                        )
                        processed_content.append(
                            {
                                "type": "image",
                                "data": image_data["data"],
                                "mime_type": image_data["mime_type"],
                            }
                        )
                    else:
                        processed_content.append(item)

                processed_messages.append(
                    {
                        "role": msg["role"],
                        "content": processed_content,
                    }
                )
            else:
                processed_messages.append(msg)

        return processed_messages

    def _handle_static_response(self, response: Any) -> str:
        """Handle static response from API."""
        result = self.response_handler.handle_static_response(
            response, self.provider_name
        )

        # Track usage
        if result.usage:
            self.cost_tracker.track_usage(
                self.model,
                TokenUsage(
                    input_tokens=result.usage.input_tokens,
                    output_tokens=result.usage.output_tokens,
                ),
            )

        # Add to history
        self.chat_history.add_message("assistant", result.content)

        return result.content

    def _handle_streaming_response(self, response: Any) -> Iterator[str]:
        """Handle streaming response from API."""
        full_content = []
        total_usage = TokenUsage()

        for chunk in self.response_handler.handle_streaming_response(
            response, self.provider_name
        ):
            if chunk.content:
                full_content.append(chunk.content)
                yield chunk.content

            if chunk.usage:
                total_usage.input_tokens += chunk.usage.input_tokens
                total_usage.output_tokens += chunk.usage.output_tokens

        # Track total usage
        if total_usage.input_tokens > 0 or total_usage.output_tokens > 0:
            self.cost_tracker.track_usage(self.model, total_usage)

        # Add complete response to history
        complete_content = "".join(full_content)
        if complete_content:
            self.chat_history.add_message("assistant", complete_content)

    def _make_api_call(self, messages: List[Dict[str, Any]], **kwargs: Any) -> Any:
        """
        Make API call to the provider.

        This method must be implemented by concrete providers.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement _make_api_call"
        )

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        return self.cost_tracker.get_usage_stats()

    def reset_usage_stats(self) -> None:
        """Reset usage statistics."""
        self.cost_tracker.reset()

    def clear_history(self) -> None:
        """Clear chat history."""
        self.chat_history.clear()

    def get_history(self) -> List[Dict[str, str]]:
        """Get chat history."""
        return self.chat_history.get_messages()

    def set_system_prompt(self, prompt: str) -> None:
        """Update system prompt."""
        self.system_prompt = prompt

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"{self.__class__.__name__}("
            f"provider={self.provider_name}, "
            f"model={self.model}, "
            f"stream={self.stream})"
        )


## EOF
