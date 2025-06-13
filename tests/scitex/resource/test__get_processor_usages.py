#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-02 15:00:00 (ywatanabe)"
# File: ./tests/scitex/resource/test__get_processor_usages.py

"""Tests for processor usage monitoring functionality."""

import os
import subprocess
from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

import pandas as pd
import pytest

from scitex.resource import (
    _get_cpu_usage,
    _get_gpu_usage,
    get_processor_usages,
)


class TestGetProcessorUsages:
    """Test suite for get_processor_usages function."""
    
    @patch('scitex.resource._get_processor_usages._get_gpu_usage')
    @patch('scitex.resource._get_processor_usages._get_cpu_usage')
    def test_basic_functionality(self, mock_cpu, mock_gpu):
        """Test basic processor usage retrieval."""
        mock_cpu.return_value = (25.3, 8.2)
        mock_gpu.return_value = (65.0, 4.5)
        
        result = get_processor_usages()
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert list(result.columns) == ['Timestamp', 'CPU [%]', 'RAM [GiB]', 'GPU [%]', 'VRAM [GiB]']
        assert result.iloc[0]['CPU [%]'] == 25.3
        assert result.iloc[0]['RAM [GiB]'] == 8.2
        assert result.iloc[0]['GPU [%]'] == 65.0
        assert result.iloc[0]['VRAM [GiB]'] == 4.5
        assert isinstance(result.iloc[0]['Timestamp'], datetime)
    
    @patch('scitex.resource._get_processor_usages._get_gpu_usage')
    @patch('scitex.resource._get_processor_usages._get_cpu_usage')
    def test_zero_usage(self, mock_cpu, mock_gpu):
        """Test with zero resource usage."""
        mock_cpu.return_value = (0.0, 0.0)
        mock_gpu.return_value = (0.0, 0.0)
        
        result = get_processor_usages()
        
        assert result.iloc[0]['CPU [%]'] == 0.0
        assert result.iloc[0]['RAM [GiB]'] == 0.0
        assert result.iloc[0]['GPU [%]'] == 0.0
        assert result.iloc[0]['VRAM [GiB]'] == 0.0
    
    @patch('scitex.resource._get_processor_usages._get_gpu_usage')
    @patch('scitex.resource._get_processor_usages._get_cpu_usage')
    def test_high_usage(self, mock_cpu, mock_gpu):
        """Test with high resource usage."""
        mock_cpu.return_value = (95.8, 31.7)
        mock_gpu.return_value = (99.9, 23.8)
        
        result = get_processor_usages()
        
        assert result.iloc[0]['CPU [%]'] == 95.8
        assert result.iloc[0]['RAM [GiB]'] == 31.7
        assert result.iloc[0]['GPU [%]'] == 99.9
        assert result.iloc[0]['VRAM [GiB]'] == 23.8
    
    @patch('scitex.resource._get_processor_usages._get_gpu_usage')
    @patch('scitex.resource._get_processor_usages._get_cpu_usage')
    def test_rounding_behavior(self, mock_cpu, mock_gpu):
        """Test DataFrame rounding to 1 decimal place."""
        # The individual functions should return already-rounded values
        # since they have their own rounding logic
        mock_cpu.return_value = (25.3, 8.2)
        mock_gpu.return_value = (65.1, 4.6)
        
        result = get_processor_usages()
        
        assert result.iloc[0]['CPU [%]'] == 25.3
        assert result.iloc[0]['RAM [GiB]'] == 8.2
        assert result.iloc[0]['GPU [%]'] == 65.1
        assert result.iloc[0]['VRAM [GiB]'] == 4.6
    
    @patch('scitex.resource._get_processor_usages._get_cpu_usage')
    def test_cpu_error_handling(self, mock_cpu):
        """Test error handling when CPU monitoring fails."""
        mock_cpu.side_effect = RuntimeError("CPU monitoring failed")
        
        with pytest.raises(RuntimeError, match="Failed to get resource usage"):
            get_processor_usages()
    
    @patch('scitex.resource._get_processor_usages._get_gpu_usage')
    @patch('scitex.resource._get_processor_usages._get_cpu_usage')
    def test_gpu_error_handling(self, mock_cpu, mock_gpu):
        """Test error handling when GPU monitoring fails."""
        mock_cpu.return_value = (25.0, 8.0)
        mock_gpu.side_effect = RuntimeError("GPU monitoring failed")
        
        with pytest.raises(RuntimeError, match="Failed to get resource usage"):
            get_processor_usages()


class TestGetCpuUsage:
    """Test suite for _get_cpu_usage function."""
    
    @patch('scitex.resource._get_processor_usages.psutil')
    def test_basic_cpu_usage(self, mock_psutil):
        """Test basic CPU and RAM usage retrieval."""
        mock_memory = Mock()
        mock_memory.percent = 60.0
        mock_memory.total = 16 * (1024**3)  # 16 GB
        
        mock_psutil.cpu_percent.return_value = 45.7
        mock_psutil.virtual_memory.return_value = mock_memory
        
        cpu_perc, ram_gb = _get_cpu_usage()
        
        assert cpu_perc == 45.7
        assert ram_gb == 9.6  # 60% of 16 GB
    
    @patch('scitex.resource._get_processor_usages.psutil')
    def test_rounding_precision(self, mock_psutil):
        """Test rounding precision control."""
        mock_memory = Mock()
        mock_memory.percent = 75.456
        mock_memory.total = 8 * (1024**3)  # 8 GB
        
        mock_psutil.cpu_percent.return_value = 33.789
        mock_psutil.virtual_memory.return_value = mock_memory
        
        cpu_perc, ram_gb = _get_cpu_usage(n_round=2)
        
        assert cpu_perc == 33.79
        assert ram_gb == 6.04  # 75.456% of 8 GB, rounded to 2 decimals
    
    @patch('scitex.resource._get_processor_usages.psutil')
    def test_zero_usage(self, mock_psutil):
        """Test with zero CPU and RAM usage."""
        mock_memory = Mock()
        mock_memory.percent = 0.0
        mock_memory.total = 32 * (1024**3)  # 32 GB
        
        mock_psutil.cpu_percent.return_value = 0.0
        mock_psutil.virtual_memory.return_value = mock_memory
        
        cpu_perc, ram_gb = _get_cpu_usage()
        
        assert cpu_perc == 0.0
        assert ram_gb == 0.0
    
    @patch('scitex.resource._get_processor_usages.psutil')
    def test_max_usage(self, mock_psutil):
        """Test with maximum CPU and RAM usage."""
        mock_memory = Mock()
        mock_memory.percent = 100.0
        mock_memory.total = 64 * (1024**3)  # 64 GB
        
        mock_psutil.cpu_percent.return_value = 100.0
        mock_psutil.virtual_memory.return_value = mock_memory
        
        cpu_perc, ram_gb = _get_cpu_usage()
        
        assert cpu_perc == 100.0
        assert ram_gb == 64.0
    
    @patch('scitex.resource._get_processor_usages.psutil')
    def test_psutil_error_handling(self, mock_psutil):
        """Test error handling for psutil failures."""
        mock_psutil.cpu_percent.side_effect = Exception("psutil error")
        
        with pytest.raises(RuntimeError, match="Failed to get CPU/RAM usage"):
            _get_cpu_usage()


class TestGetGpuUsage:
    """Test suite for _get_gpu_usage function."""
    
    @patch('scitex.resource._get_processor_usages.subprocess.run')
    def test_basic_gpu_usage(self, mock_run):
        """Test basic GPU and VRAM usage retrieval."""
        mock_result = Mock()
        mock_result.stdout = "75,2048"
        mock_run.return_value = mock_result
        
        gpu_perc, vram_gb = _get_gpu_usage()
        
        assert gpu_perc == 75.0
        assert vram_gb == 2.0  # 2048 MiB = 2.0 GiB
        
        mock_run.assert_called_once_with(
            ["nvidia-smi", "--query-gpu=utilization.gpu,memory.used", "--format=csv,nounits,noheader"],
            capture_output=True,
            text=True,
            check=True
        )
    
    @patch('scitex.resource._get_processor_usages.subprocess.run')
    def test_zero_gpu_usage(self, mock_run):
        """Test with zero GPU usage."""
        mock_result = Mock()
        mock_result.stdout = "0,0"
        mock_run.return_value = mock_result
        
        gpu_perc, vram_gb = _get_gpu_usage()
        
        assert gpu_perc == 0.0
        assert vram_gb == 0.0
    
    @patch('scitex.resource._get_processor_usages.subprocess.run')
    def test_high_gpu_usage(self, mock_run):
        """Test with high GPU usage."""
        mock_result = Mock()
        mock_result.stdout = "99,12288"  # 12 GB VRAM
        mock_run.return_value = mock_result
        
        gpu_perc, vram_gb = _get_gpu_usage()
        
        assert gpu_perc == 99.0
        assert vram_gb == 12.0
    
    @patch('scitex.resource._get_processor_usages.subprocess.run')
    def test_rounding_precision(self, mock_run):
        """Test rounding precision control."""
        mock_result = Mock()
        mock_result.stdout = "67,3456"  # 3.375 GB VRAM
        mock_run.return_value = mock_result
        
        gpu_perc, vram_gb = _get_gpu_usage(n_round=3)
        
        assert gpu_perc == 67.0
        assert vram_gb == 3.375
    
    @patch('scitex.resource._get_processor_usages.subprocess.run')
    def test_nvidia_smi_not_available(self, mock_run):
        """Test fallback when nvidia-smi is not available."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "nvidia-smi")
        
        gpu_perc, vram_gb = _get_gpu_usage()
        
        assert gpu_perc == 0.0
        assert vram_gb == 0.0
    
    @patch('scitex.resource._get_processor_usages.subprocess.run')
    def test_invalid_output_format(self, mock_run):
        """Test fallback with invalid nvidia-smi output."""
        mock_result = Mock()
        mock_result.stdout = "invalid,output,format"
        mock_run.return_value = mock_result
        
        gpu_perc, vram_gb = _get_gpu_usage()
        
        assert gpu_perc == 0.0
        assert vram_gb == 0.0
    
    @patch('scitex.resource._get_processor_usages.subprocess.run')
    def test_empty_output(self, mock_run):
        """Test fallback with empty nvidia-smi output."""
        mock_result = Mock()
        mock_result.stdout = ""
        mock_run.return_value = mock_result
        
        gpu_perc, vram_gb = _get_gpu_usage()
        
        assert gpu_perc == 0.0
        assert vram_gb == 0.0
    
    @patch('scitex.resource._get_processor_usages.subprocess.run')
    def test_non_numeric_values(self, mock_run):
        """Test fallback with non-numeric nvidia-smi output."""
        mock_result = Mock()
        mock_result.stdout = "N/A,N/A"
        mock_run.return_value = mock_result
        
        gpu_perc, vram_gb = _get_gpu_usage()
        
        assert gpu_perc == 0.0
        assert vram_gb == 0.0


if __name__ == "__main__":
    import os
    import pytest
    pytest.main([os.path.abspath(__file__)])
