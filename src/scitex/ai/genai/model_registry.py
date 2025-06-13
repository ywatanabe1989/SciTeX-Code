#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-05-31 10:05:00"
# Author: ywatanabe
# File: ./src/scitex/ai/genai/model_registry.py

"""
Central registry for AI model information.

This module maintains a registry of available models across providers,
including their capabilities, costs, and constraints.
"""

from typing import Dict, List, Optional, NamedTuple, Union, Any
import pandas as pd
from dataclasses import dataclass

try:
    from .params import MODELS
except ImportError:
    # For testing, use a default empty dataframe
    MODELS = pd.DataFrame()


@dataclass
class ModelInfo:
    """Information about a specific model.

    Attributes
    ----------
    name : str
        Model identifier
    provider : str
        Provider name
    max_tokens : int
        Maximum token limit
    supports_images : bool
        Whether model supports image inputs
    supports_streaming : bool
        Whether model supports streaming responses
    cost_per_1k_input : float
        Cost per 1000 input tokens
    cost_per_1k_output : float
        Cost per 1000 output tokens
    """

    name: str
    provider: str
    max_tokens: int
    supports_images: bool = False
    supports_streaming: bool = True
    cost_per_1k_input: float = 0.0
    cost_per_1k_output: float = 0.0


class ModelRegistry:
    """Central registry for model information.

    Example
    -------
    >>> registry = ModelRegistry()
    >>> models = registry.get_models_for_provider("OpenAI")
    >>> print(models)
    ['gpt-3.5-turbo', 'gpt-4', ...]

    >>> info = registry.get_model_info("gpt-4")
    >>> print(info.max_tokens)
    8192
    """

    def __init__(self):
        """Initialize the model registry."""
        self._models_df = MODELS
        self._model_cache: Dict[str, ModelInfo] = {}
        self._build_cache()

    def _build_cache(self) -> None:
        """Build the internal model cache from the dataframe."""
        if self._models_df.empty:
            return

        for _, row in self._models_df.iterrows():
            # Handle different column names from fixtures
            cost_input = row.get(
                "cost_1k_input_tokens", row.get("cost_per_1k_input", 0.0)
            )
            cost_output = row.get(
                "cost_1k_output_tokens", row.get("cost_per_1k_output", 0.0)
            )

            info = ModelInfo(
                name=row["name"],
                provider=row["provider"],
                max_tokens=row.get("max_tokens", 4096),
                supports_images=row.get("supports_images", False),
                supports_streaming=row.get("supports_streaming", True),
                cost_per_1k_input=cost_input,
                cost_per_1k_output=cost_output,
            )
            self._model_cache[row["name"]] = info

    def get_models_for_provider(self, provider: str) -> List[str]:
        """Get all available models for a specific provider.

        Parameters
        ----------
        provider : str
            The provider name

        Returns
        -------
        List[str]
            List of model names
        """
        if self._models_df.empty:
            return []
        mask = self._models_df["provider"].str.lower() == provider.lower()
        return self._models_df[mask]["name"].tolist()

    def verify_model(self, provider: str, model: str) -> bool:
        """Verify if a model is available for a provider.

        Parameters
        ----------
        provider : str
            The provider name
        model : str
            The model name

        Returns
        -------
        bool
            True if model is available

        Raises
        ------
        ValueError
            If model is not available for the provider
        """
        if model not in self._model_cache:
            raise ValueError(f"Model '{model}' not available for provider '{provider}'")
        if self._model_cache[model].provider.lower() != provider.lower():
            raise ValueError(f"Model '{model}' not available for provider '{provider}'")
        return True

    def get_model_info(self, provider: str, model: str) -> Dict[str, Any]:
        """Get detailed information about a model.

        Parameters
        ----------
        provider : str
            The provider name
        model : str
            The model name

        Returns
        -------
        Dict[str, any]
            Model information dictionary

        Raises
        ------
        ValueError
            If model not found
        """
        if model not in self._model_cache:
            raise ValueError(f"Model {model} not found")

        info = self._model_cache[model]
        if info.provider.lower() != provider.lower():
            raise ValueError(f"Model {model} not found for provider {provider}")

        # Return info as dictionary (matching test expectations)
        return {
            "name": info.name,
            "provider": info.provider.lower(),
            "max_tokens": info.max_tokens,
            "supports_images": info.supports_images,
            "supports_streaming": info.supports_streaming,
            "cost_per_1k_input_tokens": info.cost_per_1k_input,
            "cost_per_1k_output_tokens": info.cost_per_1k_output,
        }

    def list_all_models(self) -> Dict[str, List[str]]:
        """List all available models grouped by provider.

        Returns
        -------
        Dict[str, List[str]]
            Dictionary mapping providers to their model lists
        """
        result = {}
        for provider in self._models_df["provider"].unique():
            result[provider] = self.get_models_for_provider(provider)
        return result

    def get_provider_for_model(self, model: str) -> Optional[str]:
        """Get the provider for a specific model.

        Parameters
        ----------
        model : str
            The model name

        Returns
        -------
        Optional[str]
            Provider name if model found, None otherwise
        """
        info = self._model_cache.get(model)
        return info.provider if info else None

    def list_models(self, provider: Optional[str] = None) -> List[str]:
        """List available models.

        Parameters
        ----------
        provider : Optional[str]
            If specified, only return models for this provider

        Returns
        -------
        List[str]
            List of model names
        """
        if provider:
            return self.get_models_for_provider(provider.lower())
        else:
            return list(self._model_cache.keys())

    def list_providers(self) -> List[str]:
        """List available providers.

        Returns
        -------
        List[str]
            List of unique provider names
        """
        if self._models_df.empty:
            return []
        return sorted(self._models_df["provider"].str.lower().unique().tolist())

    def get_default_model(self, provider: str) -> str:
        """Get default model for a provider.

        Parameters
        ----------
        provider : str
            The provider name

        Returns
        -------
        str
            Default model name

        Raises
        ------
        ValueError
            If no models available for provider
        """
        models = self.get_models_for_provider(provider.lower())
        if not models:
            raise ValueError(f"No models available for provider {provider}")
        return models[0]

    def supports_images(self, provider: str, model: str) -> bool:
        """Check if model supports images.

        Parameters
        ----------
        provider : str
            The provider name
        model : str
            The model name

        Returns
        -------
        bool
            True if model supports images
        """
        info = self._model_cache.get(model)
        if not info or info.provider.lower() != provider.lower():
            return False
        return info.supports_images

    def print_models(self, provider: Optional[str] = None) -> None:
        """Print available models in a formatted way.

        Parameters
        ----------
        provider : Optional[str]
            If specified, only show models for this provider
        """
        if provider:
            models = self.get_models_for_provider(provider.lower())
            for model in models:
                info = self._model_cache[model]
                print(f"- {info.provider.lower()} - {model}")
        else:
            for model, info in self._model_cache.items():
                print(f"- {info.provider.lower()} - {model}")


# EOF
