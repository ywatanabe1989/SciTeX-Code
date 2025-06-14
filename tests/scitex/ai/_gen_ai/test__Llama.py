#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-01 14:40:00 (ywatanabe)"
# File: ./tests/scitex/ai/_gen_ai/test__Llama.py

"""Tests for scitex.ai._gen_ai._Llama module."""

import pytest
import os
from unittest.mock import Mock, MagicMock, patch


class TestLlama:
    """Test suite for Llama class."""

    @pytest.fixture
    def mock_llama_builder(self):
        """Create a mock Llama builder."""
        mock_generator = Mock()
        mock_result = [
            {
                "generation": {
                    "content": "Test response"
                }
            }
        ]
        mock_generator.chat_completion.return_value = mock_result
        return mock_generator

    @pytest.fixture
    def mock_env_setup(self):
        """Mock environment variables for distributed setup."""
        env_vars = {
            'MASTER_ADDR': 'localhost',
            'MASTER_PORT': '12355',
            'WORLD_SIZE': '1',
            'RANK': '0'
        }
        with patch.dict(os.environ, env_vars):
            yield

    @pytest.fixture
    def mock_llama_module(self):
        """Mock the llama module."""
        with patch('scitex.ai._gen_ai._Llama.Dialog') as mock_dialog:
            with patch('scitex.ai._gen_ai._Llama._Llama') as mock_llama_class:
                yield mock_dialog, mock_llama_class

    def test_init_with_default_paths(self, mock_env_setup):
        """Test initialization with default paths."""
        from scitex.ai._gen_ai import Llama
        
        with patch('scitex.ai._gen_ai._Llama.MODELS', MagicMock()):
            with patch.object(Llama, '_init_client', return_value=Mock()):
                llama_ai = Llama(model="Meta-Llama-3-8B")
                assert llama_ai.model == "Meta-Llama-3-8B"
                assert llama_ai.ckpt_dir == "Meta-Meta-Llama-3-8B/"
                assert llama_ai.tokenizer_path == "./Meta-Meta-Llama-3-8B/tokenizer.model"
                assert llama_ai.max_seq_len == 32_768
                assert llama_ai.max_batch_size == 4

    def test_init_with_custom_paths(self, mock_env_setup):
        """Test initialization with custom paths."""
        from scitex.ai._gen_ai import Llama
        
        with patch('scitex.ai._gen_ai._Llama.MODELS', MagicMock()):
            with patch.object(Llama, '_init_client', return_value=Mock()):
                llama_ai = Llama(
                    ckpt_dir="/custom/path/",
                    tokenizer_path="/custom/tokenizer.model",
                    model="Meta-Llama-3-8B"
                )
                assert llama_ai.ckpt_dir == "/custom/path/"
                assert llama_ai.tokenizer_path == "/custom/tokenizer.model"

    def test_environment_setup(self, mock_env_setup):
        """Test environment variables are set correctly."""
        from scitex.ai._gen_ai import Llama
        
        with patch('scitex.ai._gen_ai._Llama.MODELS', MagicMock()):
            with patch.object(Llama, '_init_client', return_value=Mock()):
                with patch('scitex.ai._gen_ai._Llama.print_envs') as mock_print:
                    llama_ai = Llama(model="Meta-Llama-3-8B")
                    mock_print.assert_called_once()
                    assert os.environ['MASTER_ADDR'] == 'localhost'
                    assert os.environ['MASTER_PORT'] == '12355'
                    assert os.environ['WORLD_SIZE'] == '1'
                    assert os.environ['RANK'] == '0'

    def test_init_client(self, mock_env_setup, mock_llama_module, mock_llama_builder):
        """Test client initialization."""
        from scitex.ai._gen_ai import Llama
        
        mock_dialog, mock_llama_class = mock_llama_module
        mock_llama_class.build.return_value = mock_llama_builder
        
        with patch('scitex.ai._gen_ai._Llama.MODELS', MagicMock()):
            llama_ai = Llama(model="Meta-Llama-3-8B")
            
            mock_llama_class.build.assert_called_once_with(
                ckpt_dir="Meta-Meta-Llama-3-8B/",
                tokenizer_path="./Meta-Meta-Llama-3-8B/tokenizer.model",
                max_seq_len=32_768,
                max_batch_size=4
            )
            assert llama_ai.client == mock_llama_builder

    def test_api_call_static(self, mock_env_setup, mock_llama_module, mock_llama_builder):
        """Test static API call."""
        from scitex.ai._gen_ai import Llama
        
        mock_dialog, mock_llama_class = mock_llama_module
        mock_llama_class.build.return_value = mock_llama_builder
        
        with patch('scitex.ai._gen_ai._Llama.MODELS', MagicMock()):
            llama_ai = Llama(model="Meta-Llama-3-8B")
            llama_ai.history = [{"role": "user", "content": "Test"}]
            
            result = llama_ai._api_call_static()
            
            assert result == "Test response"
            mock_llama_builder.chat_completion.assert_called_once()
            call_args = mock_llama_builder.chat_completion.call_args
            assert call_args[0][0] == [llama_ai.history]  # dialogs
            assert call_args[1]['temperature'] == 1.0
            assert call_args[1]['top_p'] == 0.9

    def test_api_call_stream(self, mock_env_setup, mock_llama_module, mock_llama_builder):
        """Test streaming API call (simulated)."""
        from scitex.ai._gen_ai import Llama
        
        mock_dialog, mock_llama_class = mock_llama_module
        mock_llama_class.build.return_value = mock_llama_builder
        
        with patch('scitex.ai._gen_ai._Llama.MODELS', MagicMock()):
            llama_ai = Llama(model="Meta-Llama-3-8B", stream=True)
            llama_ai.history = [{"role": "user", "content": "Test"}]
            
            # Since Llama doesn't have native streaming, it simulates by character
            result = list(llama_ai._api_call_stream())
            
            assert ''.join(result) == "Test response"
            assert len(result) == len("Test response")  # One char per yield

    def test_max_gen_len_parameter(self, mock_env_setup, mock_llama_module, mock_llama_builder):
        """Test max_gen_len parameter."""
        from scitex.ai._gen_ai import Llama
        
        mock_dialog, mock_llama_class = mock_llama_module
        mock_llama_class.build.return_value = mock_llama_builder
        
        with patch('scitex.ai._gen_ai._Llama.MODELS', MagicMock()):
            llama_ai = Llama(model="Meta-Llama-3-8B", max_gen_len=2048)
            llama_ai.history = [{"role": "user", "content": "Test"}]
            
            llama_ai._api_call_static()
            
            call_kwargs = mock_llama_builder.chat_completion.call_args[1]
            assert call_kwargs['max_gen_len'] == 2048

    def test_temperature_setting(self, mock_env_setup, mock_llama_module, mock_llama_builder):
        """Test temperature parameter is passed correctly."""
        from scitex.ai._gen_ai import Llama
        
        mock_dialog, mock_llama_class = mock_llama_module
        mock_llama_class.build.return_value = mock_llama_builder
        
        with patch('scitex.ai._gen_ai._Llama.MODELS', MagicMock()):
            llama_ai = Llama(
                model="Meta-Llama-3-8B",
                temperature=0.5
            )
            llama_ai.history = [{"role": "user", "content": "Test"}]
            llama_ai._api_call_static()
            
            call_kwargs = mock_llama_builder.chat_completion.call_args[1]
            assert call_kwargs['temperature'] == 0.5

    @pytest.mark.parametrize("stream", [True, False])
    def test_stream_parameter(self, mock_env_setup, stream):
        """Test stream parameter handling."""
        from scitex.ai._gen_ai import Llama
        
        with patch('scitex.ai._gen_ai._Llama.MODELS', MagicMock()):
            with patch.object(Llama, '_init_client', return_value=Mock()):
                llama_ai = Llama(
                    model="Meta-Llama-3-8B",
                    stream=stream
                )
                assert llama_ai.stream == stream

    def test_n_keep_parameter(self, mock_env_setup):
        """Test n_keep parameter for history management."""
        from scitex.ai._gen_ai import Llama
        
        with patch('scitex.ai._gen_ai._Llama.MODELS', MagicMock()):
            with patch.object(Llama, '_init_client', return_value=Mock()):
                llama_ai = Llama(
                    model="Meta-Llama-3-8B",
                    n_keep=5
                )
                assert llama_ai.n_keep == 5

    def test_seed_parameter(self, mock_env_setup):
        """Test seed parameter initialization."""
        from scitex.ai._gen_ai import Llama
        
        with patch('scitex.ai._gen_ai._Llama.MODELS', MagicMock()):
            with patch.object(Llama, '_init_client', return_value=Mock()):
                llama_ai = Llama(
                    model="Meta-Llama-3-8B",
                    seed=42
                )
                assert llama_ai.seed == 42

    def test_system_setting(self, mock_env_setup):
        """Test system setting initialization."""
        from scitex.ai._gen_ai import Llama
        
        with patch('scitex.ai._gen_ai._Llama.MODELS', MagicMock()):
            with patch.object(Llama, '_init_client', return_value=Mock()):
                system_msg = "You are a helpful assistant"
                llama_ai = Llama(
                    model="Meta-Llama-3-8B",
                    system_setting=system_msg
                )
                assert llama_ai.system_setting == system_msg

    def test_str_method(self, mock_env_setup):
        """Test __str__ method returns 'Llama'."""
        from scitex.ai._gen_ai import Llama
        
        with patch('scitex.ai._gen_ai._Llama.MODELS', MagicMock()):
            with patch.object(Llama, '_init_client', return_value=Mock()):
                llama_ai = Llama(model="Meta-Llama-3-8B")
                assert str(llama_ai) == "Llama"

    def test_verify_model(self, mock_env_setup):
        """Test verify_model method (should pass for Llama)."""
        from scitex.ai._gen_ai import Llama
        
        with patch('scitex.ai._gen_ai._Llama.MODELS', MagicMock()):
            with patch.object(Llama, '_init_client', return_value=Mock()):
                llama_ai = Llama(model="Meta-Llama-3-8B")
                # Should not raise any exception
                llama_ai.verify_model()

    @pytest.mark.parametrize("model,expected_ckpt", [
        ("Meta-Llama-3-8B", "Meta-Meta-Llama-3-8B/"),
        ("Meta-Llama-3-70B", "Meta-Meta-Llama-3-70B/"),
        ("Llama-2-7b", "Meta-Llama-2-7b/"),
    ])
    def test_different_models(self, mock_env_setup, model, expected_ckpt):
        """Test initialization with different Llama models."""
        from scitex.ai._gen_ai import Llama
        
        with patch('scitex.ai._gen_ai._Llama.MODELS', MagicMock()):
            with patch.object(Llama, '_init_client', return_value=Mock()):
                llama_ai = Llama(model=model)
                assert llama_ai.model == model
                assert llama_ai.ckpt_dir == expected_ckpt


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-05 21:11:08 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/ai/_gen_ai/_Llama.py
#
# """Imports"""
# import os
# import sys
# from typing import List, Optional
#
# import matplotlib.pyplot as plt
# import scitex
#
# try:
#     from llama import Dialog
#     from llama import Llama as _Llama
# except:
#     pass
#
# from ._BaseGenAI import BaseGenAI
#
# """Functions & Classes"""
# def print_envs():
#     settings = {
#         "MASTER_ADDR": os.getenv("MASTER_ADDR", "localhost"),
#         "MASTER_PORT": os.getenv("MASTER_PORT", "12355"),
#         "WORLD_SIZE": os.getenv("WORLD_SIZE", "1"),
#         "RANK": os.getenv("RANK", "0"),
#     }
#
#     print("Environment Variable Settings:")
#     for key, value in settings.items():
#         print(f"{key}: {value}")
#     print()
#
#
# class Llama(BaseGenAI):
#     def __init__(
#         self,
#         ckpt_dir: str = "",
#         tokenizer_path: str = "",
#         system_setting: str = "",
#         model: str = "Meta-Llama-3-8B",
#         max_seq_len: int = 32_768,
#         max_batch_size: int = 4,
#         max_gen_len: Optional[int] = None,
#         stream: bool = False,
#         seed: Optional[int] = None,
#         n_keep: int = 1,
#         temperature: float = 1.0,
#         provider="Llama",
#         chat_history=None,
#         **kwargs,
#     ):
#
#         # Configure environment variables
#         os.environ["MASTER_ADDR"] = os.getenv("MASTER_ADDR", "localhost")
#         os.environ["MASTER_PORT"] = os.getenv("MASTER_PORT", "12355")
#         os.environ["WORLD_SIZE"] = os.getenv("WORLD_SIZE", "1")
#         os.environ["RANK"] = os.getenv("RANK", "0")
#         print_envs()
#
#         self.ckpt_dir = (
#             ckpt_dir if ckpt_dir else f"Meta-{model}/"
#         )
#         self.tokenizer_path = (
#             tokenizer_path
#             if tokenizer_path
#             else f"./Meta-{model}/tokenizer.model"
#         )
#         self.max_seq_len = max_seq_len
#         self.max_batch_size = max_batch_size
#         self.max_gen_len = max_gen_len
#
#         super().__init__(
#             system_setting=system_setting,
#             model=model,
#             api_key="",
#             stream=stream,
#             seed=seed,
#             n_keep=n_keep,
#             temperature=temperature,
#             chat_history=chat_history,
#         )
#
#     def __str__(self):
#         return "Llama"
#
#     def _init_client(self):
#         generator = _Llama.build(
#             ckpt_dir=self.ckpt_dir,
#             tokenizer_path=self.tokenizer_path,
#             max_seq_len=self.max_seq_len,
#             max_batch_size=self.max_batch_size,
#         )
#         return generator
#
#     def _api_call_static(self):
#         dialogs: List[Dialog] = [self.history]
#         results = self.client.chat_completion(
#             dialogs,
#             max_gen_len=self.max_gen_len,
#             temperature=self.temperature,
#             top_p=0.9,
#         )
#         out_text = results[0]["generation"]["content"]
#         return out_text
#
#     def _api_call_stream(self):
#         # Llama3 doesn't have built-in streaming, so we'll simulate it
#         full_response = self._api_call_static()
#         for char in full_response:
#             yield char
#
#     # def _get_available_models(self):
#     #     # Llama3 doesn't have a list of available models, so we'll return a placeholder
#     #     return ["llama3"]
#
#     def verify_model(self):
#         # Llama3 doesn't require model verification, so we'll skip it
#         pass
#
#
# def main():
#     m = Llama(
#         ckpt_dir="/path/to/checkpoint",
#         tokenizer_path="/path/to/tokenizer",
#         system_setting="You are a helpful assistant.",
#         max_seq_len=512,
#         max_batch_size=4,
#         stream=True,
#         temperature=0.7,
#     )
#     m("Hi")
#     pass
#
#
# if __name__ == "__main__":
#     # Main
#     CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(
#         sys, plt, verbose=False
#     )
#     main()
#     scitex.gen.close(CONFIG, verbose=False, notify=False)
#
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/ai/_gen_ai/_Llama.py
# --------------------------------------------------------------------------------
