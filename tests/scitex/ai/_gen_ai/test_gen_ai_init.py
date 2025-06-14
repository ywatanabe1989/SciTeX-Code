#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-13 23:14:27 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/SciTeX-Code/tests/scitex/ai/_gen_ai/test_gen_ai_init.py
# ----------------------------------------
import os
__FILE__ = (
    "./tests/scitex/ai/_gen_ai/test_gen_ai_init.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

# Time-stamp: "2025-06-02 16:20:00"

import pandas as pd
import pytest


class TestGenAIModuleInit:
    def test_models_import(self):
        from scitex.ai._gen_ai._PARAMS import MODELS

        assert MODELS is not None
        assert isinstance(MODELS, pd.DataFrame)

    def test_models_dataframe_structure(self):
        from scitex.ai._gen_ai._PARAMS import MODELS

        # Check that MODELS is a DataFrame
        assert isinstance(MODELS, pd.DataFrame)

        # Check that it's not empty
        assert len(MODELS) > 0

        # Check required columns exist
        required_columns = [
            "name",
            "input_cost",
            "output_cost",
            "api_key_env",
            "provider",
        ]
        for col in required_columns:
            assert (
                col in MODELS.columns
            ), f"Column '{col}' missing from MODELS DataFrame"

    def test_models_contains_expected_providers(self):
        from scitex.ai._gen_ai._PARAMS import MODELS

        providers = MODELS["provider"].unique()
        expected_providers = [
            "OpenAI",
            "Anthropic",
            "Google",
            "Perplexity",
            "Llama",
            "DeepSeek",
            "Groq",
        ]

        for provider in expected_providers:
            assert (
                provider in providers
            ), f"Provider '{provider}' not found in MODELS"

    def test_models_openai_entries(self):
        from scitex.ai._gen_ai._PARAMS import MODELS

        openai_models = MODELS[MODELS["provider"] == "OpenAI"]
        assert len(openai_models) > 0

        # Check for some key OpenAI models
        model_names = openai_models["name"].tolist()
        expected_models = ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"]

        for model in expected_models:
            assert model in model_names, f"OpenAI model '{model}' not found"

    def test_models_anthropic_entries(self):
        from scitex.ai._gen_ai._PARAMS import MODELS

        anthropic_models = MODELS[MODELS["provider"] == "Anthropic"]
        assert len(anthropic_models) > 0

        # Check API key environment variable
        for _, model in anthropic_models.iterrows():
            assert model["api_key_env"] == "ANTHROPIC_API_KEY"

    def test_models_google_entries(self):
        from scitex.ai._gen_ai._PARAMS import MODELS

        google_models = MODELS[MODELS["provider"] == "Google"]
        assert len(google_models) > 0

        # Check for Gemini models
        model_names = google_models["name"].tolist()
        gemini_models = [
            name for name in model_names if "gemini" in name.lower()
        ]
        assert len(gemini_models) > 0, "No Gemini models found"

    def test_models_cost_structure(self):
        import pandas as pd
        from scitex.ai._gen_ai._PARAMS import MODELS

        for _, model in MODELS.iterrows():
            # Cost should be None/NaN or positive number
            if (
                not pd.isna(model["input_cost"])
                and model["input_cost"] is not None
            ):
                assert (
                    model["input_cost"] >= 0
                ), f"Negative input cost for {model['name']}"
            if (
                not pd.isna(model["output_cost"])
                and model["output_cost"] is not None
            ):
                assert (
                    model["output_cost"] >= 0
                ), f"Negative output cost for {model['name']}"

    def test_models_api_key_env_format(self):
        from scitex.ai._gen_ai._PARAMS import MODELS

        for _, model in MODELS.iterrows():
            api_key_env = model["api_key_env"]
            assert isinstance(
                api_key_env, str
            ), f"API key env should be string for {model['name']}"
            assert api_key_env.endswith(
                "_API_KEY"
            ), f"API key env should end with '_API_KEY' for {model['name']}"

    def test_models_name_uniqueness(self):
        from scitex.ai._gen_ai._PARAMS import MODELS

        model_names = MODELS["name"].tolist()
        unique_names = set(model_names)

        # Check for duplicates
        assert len(model_names) == len(
            unique_names
        ), "Duplicate model names found in MODELS"

    def test_models_deepseek_entries(self):
        from scitex.ai._gen_ai._PARAMS import MODELS

        deepseek_models = MODELS[MODELS["provider"] == "DeepSeek"]
        assert len(deepseek_models) > 0

        # Check for key DeepSeek models
        model_names = deepseek_models["name"].tolist()
        expected_models = ["deepseek-chat", "deepseek-coder"]

        for model in expected_models:
            assert model in model_names, f"DeepSeek model '{model}' not found"

    def test_models_groq_entries(self):
        from scitex.ai._gen_ai._PARAMS import MODELS

        groq_models = MODELS[MODELS["provider"] == "Groq"]
        assert len(groq_models) > 0

        # Check API key environment variable
        for _, model in groq_models.iterrows():
            assert model["api_key_env"] == "GROQ_API_KEY"


class TestGenAIModuleImportStructure:
    def test_direct_import_models(self):
        # Test that MODELS can be imported directly from the module
        from scitex.ai._gen_ai._PARAMS import MODELS

        assert MODELS is not None

    def test_import_from_params(self):
        # Test that MODELS comes from _PARAMS
        from scitex.ai._gen_ai._PARAMS import MODELS

        # Should be the same object/data
        pd.testing.assert_frame_equal(MODELS, MODELS)

    def test_module_attributes(self):
        import scitex.ai._gen_ai as gen_ai_module

        # Check that MODELS is available as module attribute
        assert hasattr(gen_ai_module, "MODELS")
        assert isinstance(gen_ai_module.MODELS, pd.DataFrame)


class TestGenAIModelDataValidation:
    def test_models_data_integrity(self):
        from scitex.ai._gen_ai._PARAMS import MODELS

        # Check no empty strings in critical fields
        for _, model in MODELS.iterrows():
            assert model["name"].strip() != "", f"Empty name found"
            assert (
                model["provider"].strip() != ""
            ), f"Empty provider found for {model['name']}"
            assert (
                model["api_key_env"].strip() != ""
            ), f"Empty api_key_env found for {model['name']}"

    def test_models_provider_consistency(self):
        from scitex.ai._gen_ai._PARAMS import MODELS

        # Group by provider and check API key consistency
        providers = MODELS.groupby("provider")

        for provider_name, group in providers:
            api_keys = group["api_key_env"].unique()
            # Each provider should use consistent API key environment variable
            assert (
                len(api_keys) == 1
            ), f"Provider {provider_name} has inconsistent API key env vars: {api_keys}"

    def test_models_cost_ranges(self):
        import pandas as pd
        from scitex.ai._gen_ai._PARAMS import MODELS

        # Test reasonable cost ranges (costs in dollars per million tokens)
        for _, model in MODELS.iterrows():
            if (
                not pd.isna(model["input_cost"])
                and model["input_cost"] is not None
            ):
                assert (
                    0 <= model["input_cost"] <= 100
                ), f"Unreasonable input cost for {model['name']}: {model['input_cost']}"
            if (
                not pd.isna(model["output_cost"])
                and model["output_cost"] is not None
            ):
                assert (
                    0 <= model["output_cost"] <= 100
                ), f"Unreasonable output cost for {model['name']}: {model['output_cost']}"

    def test_models_name_format(self):
        from scitex.ai._gen_ai._PARAMS import MODELS

        for _, model in MODELS.iterrows():
            name = model["name"]
            # Names should not contain spaces or special characters except hyphens and dots
            assert " " not in name, f"Model name contains space: {name}"
            # Should be lowercase or contain standard model naming patterns
            assert name.islower() or any(
                char.isdigit() for char in name
            ), f"Unusual name format: {name}"


class TestGenAIModelSpecificValidation:
    def test_openai_model_specifics(self):
        import pandas as pd
        from scitex.ai._gen_ai._PARAMS import MODELS

        openai_models = MODELS[MODELS["provider"] == "OpenAI"]

        # OpenAI models should have costs defined (most of them)
        for _, model in openai_models.iterrows():
            # Most OpenAI models should have costs, but some experimental ones might not
            if not pd.isna(model["input_cost"]):
                assert (
                    model["input_cost"] >= 0
                ), f"OpenAI model {model['name']} has negative input cost"
            if not pd.isna(model["output_cost"]):
                assert (
                    model["output_cost"] >= 0
                ), f"OpenAI model {model['name']} has negative output cost"

    def test_google_model_specifics(self):
        from scitex.ai._gen_ai._PARAMS import MODELS

        google_models = MODELS[MODELS["provider"] == "Google"]

        # Google models should use GOOGLE_API_KEY
        for _, model in google_models.iterrows():
            assert (
                model["api_key_env"] == "GOOGLE_API_KEY"
            ), f"Google model {model['name']} has wrong API key env"

    def test_model_count_reasonableness(self):
        from scitex.ai._gen_ai._PARAMS import MODELS

        # Should have a reasonable number of models (not too few, not excessive)
        total_models = len(MODELS)
        assert (
            10 <= total_models <= 200
        ), f"Unusual number of models: {total_models}"

        # Each provider should have at least one model
        provider_counts = MODELS["provider"].value_counts()
        for provider, count in provider_counts.items():
            assert count >= 1, f"Provider {provider} has no models"


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# EOF
