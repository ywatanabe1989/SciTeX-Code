#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-01 13:45:00 (ywatanabe)"
# File: ./tests/scitex/ai/_gen_ai/test__PARAMS.py

"""Tests for scitex.ai._gen_ai._PARAMS module."""

import pytest
import pandas as pd
from scitex.ai._gen_ai import MODELS
# Individual model lists are not exported, only the combined MODELS DataFrame


class TestParams:
    """Test suite for _PARAMS module constants and model definitions."""

    def test_models_dataframe_structure(self):
        """Test that MODELS is a properly structured DataFrame."""
        assert isinstance(MODELS, pd.DataFrame)
        
        # Check required columns
        required_columns = ['name', 'input_cost', 'output_cost', 'api_key_env', 'provider']
        for col in required_columns:
            assert col in MODELS.columns, f"Missing required column: {col}"

    def test_models_not_empty(self):
        """Test that MODELS DataFrame is not empty."""
        assert len(MODELS) > 0
        assert not MODELS.empty

    def test_openai_models_in_dataframe(self):
        """Test OpenAI models have correct structure in MODELS DataFrame."""
        openai_models = MODELS[MODELS['provider'] == 'OpenAI']
        assert len(openai_models) > 0
        
        for _, model in openai_models.iterrows():
            assert model['api_key_env'] == 'OPENAI_API_KEY'
            assert pd.notna(model['name'])
            assert pd.notna(model['input_cost'])
            assert pd.notna(model['output_cost'])

    def test_anthropic_models_in_dataframe(self):
        """Test Anthropic models have correct structure in MODELS DataFrame."""
        anthropic_models = MODELS[MODELS['provider'] == 'Anthropic']
        assert len(anthropic_models) > 0
        
        for _, model in anthropic_models.iterrows():
            assert model['api_key_env'] == 'ANTHROPIC_API_KEY'
            assert 'claude' in model['name']

    def test_google_models_in_dataframe(self):
        """Test Google models have correct structure in MODELS DataFrame."""
        google_models = MODELS[MODELS['provider'] == 'Google']
        assert len(google_models) > 0
        
        for _, model in google_models.iterrows():
            assert model['api_key_env'] == 'GOOGLE_API_KEY'
            assert 'gemini' in model['name']

    def test_deepseek_models_in_dataframe(self):
        """Test DeepSeek models have correct structure in MODELS DataFrame."""
        deepseek_models = MODELS[MODELS['provider'] == 'DeepSeek']
        assert len(deepseek_models) > 0
        
        for _, model in deepseek_models.iterrows():
            assert model['api_key_env'] == 'DEEPSEEK_API_KEY'
            assert 'deepseek' in model['name']

    def test_groq_models_in_dataframe(self):
        """Test Groq models have correct structure in MODELS DataFrame."""
        groq_models = MODELS[MODELS['provider'] == 'Groq']
        assert len(groq_models) > 0
        
        for _, model in groq_models.iterrows():
            assert model['api_key_env'] == 'GROQ_API_KEY'

    def test_perplexity_models_in_dataframe(self):
        """Test Perplexity models have correct structure in MODELS DataFrame."""
        perplexity_models = MODELS[MODELS['provider'] == 'Perplexity']
        assert len(perplexity_models) > 0
        
        for _, model in perplexity_models.iterrows():
            assert model['api_key_env'] == 'PERPLEXITY_API_KEY'

    def test_llama_models_in_dataframe(self):
        """Test Llama models have correct structure in MODELS DataFrame."""
        llama_models = MODELS[MODELS['provider'] == 'Llama']
        assert len(llama_models) > 0
        
        for _, model in llama_models.iterrows():
            assert model['api_key_env'] == 'LLAMA_API_KEY'
            assert 'llama' in model['name'].lower()

    def test_cost_values_are_numeric_or_none(self):
        """Test that all cost values are numeric or None."""
        for _, row in MODELS.iterrows():
            input_cost = row['input_cost']
            output_cost = row['output_cost']
            
            # Cost should be numeric (float/int) or None/NaN
            if pd.notna(input_cost):
                assert isinstance(input_cost, (int, float))
                assert input_cost >= 0
            
            if pd.notna(output_cost):
                assert isinstance(output_cost, (int, float))
                assert output_cost >= 0

    def test_model_names_are_unique(self):
        """Test that all model names are unique."""
        model_names = MODELS['name'].tolist()
        assert len(model_names) == len(set(model_names)), "Duplicate model names found"

    def test_providers_are_consistent(self):
        """Test that provider names are consistent."""
        expected_providers = {'OpenAI', 'Anthropic', 'Google', 'Perplexity', 
                            'Llama', 'DeepSeek', 'Groq'}
        actual_providers = set(MODELS['provider'].unique())
        
        assert actual_providers.issubset(expected_providers), \
            f"Unexpected providers: {actual_providers - expected_providers}"

    def test_api_key_env_format(self):
        """Test that API key environment variables follow naming convention."""
        for api_key_env in MODELS['api_key_env'].unique():
            assert api_key_env.endswith('_API_KEY')
            assert api_key_env.isupper()

    def test_specific_model_availability(self):
        """Test that commonly used models are available."""
        common_models = [
            'gpt-4', 'gpt-3.5-turbo', 'gpt-4o',
            'claude-3-opus-20240229', 'claude-3-5-sonnet-20241022',
            'gemini-1.5-pro', 'gemini-1.5-flash',
            'deepseek-chat', 'deepseek-coder'
        ]
        
        available_model_names = MODELS['name'].tolist()
        for model in common_models:
            assert model in available_model_names, f"Expected model {model} not found"

    def test_models_dataframe_has_all_providers(self):
        """Test that MODELS contains models from all expected providers."""
        expected_providers = {'OpenAI', 'Anthropic', 'Google', 'DeepSeek', 'Groq', 'Perplexity', 'Llama'}
        actual_providers = set(MODELS['provider'].unique())
        
        assert expected_providers.issubset(actual_providers), \
            f"Missing providers: {expected_providers - actual_providers}"

    def test_each_provider_has_models(self):
        """Test that each provider has at least one model."""
        provider_counts = MODELS['provider'].value_counts()
        
        expected_providers = ['OpenAI', 'Anthropic', 'Google', 'DeepSeek', 'Groq', 'Perplexity', 'Llama']
        for provider in expected_providers:
            assert provider in provider_counts.index, f"No models found for provider: {provider}"
            assert provider_counts[provider] > 0, f"Provider {provider} has no models"

    def test_no_missing_values_in_required_fields(self):
        """Test that required fields don't have missing values."""
        required_fields = ['name', 'api_key_env', 'provider']
        
        for field in required_fields:
            assert MODELS[field].notna().all(), f"Missing values in {field} column"

    def test_cost_values_exist(self):
        """Test that models have cost information defined."""
        # For models with both costs defined, they should be valid numbers
        valid_costs = MODELS.dropna(subset=['input_cost', 'output_cost'])
        
        # At least some models should have both costs defined
        assert len(valid_costs) > 0, "No models have both input and output costs defined"
        
        for _, row in valid_costs.iterrows():
            # Both costs should be non-negative numbers (some models like Llama are free)
            assert row['input_cost'] >= 0, f"Model {row['name']} has negative input_cost"
            assert row['output_cost'] >= 0, f"Model {row['name']} has negative output_cost"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
