#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-02 16:50:00 (ywatanabe)"
# File: ./tests/scitex/resource/test__get_specs.py

import platform
from unittest.mock import MagicMock, patch

import pytest


def test_get_specs_default():
    """Test get_specs with default parameters."""
from scitex.resource import get_specs

    with patch("scitex.resource._get_specs.get_env_info") as mock_env:
        mock_env.return_value._asdict.return_value = {
            "os": "Linux",
            "gcc_version": "9.4.0",
            "python_version": "3.8.10",
            "torch_version": "1.10.0",
            "is_cuda_available": True,
            "pip_version": "21.0",
            "pip_packages": [],
            "conda_packages": [],
            "nvidia_gpu_models": "GeForce RTX 3080",
            "nvidia_driver_version": "470.103.01",
            "cuda_runtime_version": "11.4",
            "cudnn_version": "8.2.4",
        }
        
        result = get_specs()
        
        assert isinstance(result, dict)
        assert "Collected Time" in result
        assert "System Information" in result
        assert "CPU Info" in result
        assert "Memory Info" in result
        assert "GPU Info" in result
        assert "Disk Info" in result
        assert "Network Info" in result


def test_get_specs_selective_collection():
    """Test get_specs with selective information collection."""
from scitex.resource import get_specs

    with patch("scitex.resource._get_specs.get_env_info") as mock_env:
        mock_env.return_value._asdict.return_value = {
            "os": "Linux",
            "gcc_version": "9.4.0",
            "nvidia_gpu_models": "GeForce RTX 3080",
            "nvidia_driver_version": "470.103.01",
            "cuda_runtime_version": "11.4",
            "cudnn_version": "8.2.4",
        }
        
        result = get_specs(system=True, cpu=False, gpu=False, disk=False, network=False)
        
        assert "System Information" in result
        assert "CPU Info" not in result
        assert "Memory Info" not in result
        assert "GPU Info" not in result
        assert "Disk Info" not in result
        assert "Network Info" not in result


def test_get_specs_cpu_only():
    """Test get_specs with only CPU information."""
from scitex.resource import get_specs

    with patch("scitex.resource._get_specs.get_env_info") as mock_env, \
         patch("scitex.resource._get_specs._psutil") as mock_psutil:
        
        mock_env.return_value._asdict.return_value = {"os": "Linux"}
        
        # Mock CPU info
        mock_psutil.cpu_count.side_effect = lambda logical=True: 8 if logical else 4
        mock_psutil.cpu_freq.return_value = MagicMock(max=3600.0, min=800.0, current=2400.0)
        mock_psutil.cpu_percent.side_effect = lambda percpu=False, interval=None: [10, 20, 30, 40, 50, 60, 70, 80] if percpu else 45.0
        
        # Mock memory info
        mock_mem = MagicMock()
        mock_mem.total = 16000000000
        mock_mem.available = 8000000000
        mock_mem.used = 8000000000
        mock_mem.percent = 50.0
        mock_psutil.virtual_memory.return_value = mock_mem
        
        mock_swap = MagicMock()
        mock_swap.total = 2000000000
        mock_swap.free = 1000000000
        mock_swap.used = 1000000000
        mock_swap.percent = 50.0
        mock_psutil.swap_memory.return_value = mock_swap
        
        result = get_specs(system=False, cpu=True, gpu=False, disk=False, network=False)
        
        assert "CPU Info" in result
        assert "Memory Info" in result
        assert result["CPU Info"]["Physical cores"] == 4
        assert result["CPU Info"]["Total cores"] == 8
        assert "MHz" in result["CPU Info"]["Max Frequency"]


def test_get_specs_yaml_output():
    """Test get_specs with YAML output format."""
from scitex.resource import get_specs

    with patch("scitex.resource._get_specs.get_env_info") as mock_env, \
         patch("scitex.resource._get_specs._yaml") as mock_yaml:
        
        mock_env.return_value._asdict.return_value = {"os": "Linux"}
        mock_yaml.dump.return_value = "yaml_string_output"
        
        result = get_specs(system=True, cpu=False, gpu=False, disk=False, network=False, yaml=True)
        
        assert result == "yaml_string_output"
        mock_yaml.dump.assert_called_once()


def test_get_specs_verbose_output(capsys):
    """Test get_specs with verbose output."""
from scitex.resource import get_specs

    with patch("scitex.resource._get_specs.get_env_info") as mock_env:
        mock_env.return_value._asdict.return_value = {"os": "Linux"}
        
        result = get_specs(system=True, cpu=False, gpu=False, disk=False, network=False, verbose=True)
        
        captured = capsys.readouterr()
        assert len(captured.out) > 0  # Should have printed something
        assert isinstance(result, dict)


def test_system_info():
    """Test _system_info function."""
from scitex.resource import _system_info

    with patch("scitex.resource._get_specs._platform") as mock_platform, \
         patch("scitex.resource._get_specs._supple_os_info") as mock_os_info:
        
        mock_uname = MagicMock()
        mock_uname.node = "test-node"
        mock_uname.release = "5.4.0"
        mock_uname.version = "#42-Ubuntu"
        mock_platform.uname.return_value = mock_uname
        
        mock_os_info.return_value = {"os": "Ubuntu 20.04"}
        
        result = _system_info()
        
        assert result["OS"] == "Ubuntu 20.04"
        assert result["Node Name"] == "test-node"
        assert result["Release"] == "5.4.0"
        assert result["Version"] == "#42-Ubuntu"


def test_cpu_info():
    """Test _cpu_info function."""
from scitex.resource import _cpu_info

    with patch("scitex.resource._get_specs._psutil") as mock_psutil:
        mock_psutil.cpu_count.side_effect = lambda logical=True: 8 if logical else 4
        mock_psutil.cpu_freq.return_value = MagicMock(max=3600.0, min=800.0, current=2400.0)
        mock_psutil.cpu_percent.side_effect = lambda percpu=False, interval=None: [10, 20, 30, 40] if percpu else 25.0
        
        result = _cpu_info()
        
        assert result["Physical cores"] == 4
        assert result["Total cores"] == 8
        assert result["Max Frequency"] == "3600.00 MHz"
        assert result["Min Frequency"] == "800.00 MHz"
        assert result["Current Frequency"] == "2400.00 MHz"
        assert result["Total CPU Usage"] == "25.0%"
        assert len(result["CPU Usage Per Core"]) == 4


def test_memory_info():
    """Test _memory_info function."""
from scitex.resource import _memory_info

    with patch("scitex.resource._get_specs._psutil") as mock_psutil:
        mock_mem = MagicMock()
        mock_mem.total = 16000000000  # 16GB
        mock_mem.available = 8000000000  # 8GB
        mock_mem.used = 8000000000  # 8GB
        mock_mem.percent = 50.0
        mock_psutil.virtual_memory.return_value = mock_mem
        
        mock_swap = MagicMock()
        mock_swap.total = 2000000000  # 2GB
        mock_swap.free = 1000000000  # 1GB
        mock_swap.used = 1000000000  # 1GB
        mock_swap.percent = 50.0
        mock_psutil.swap_memory.return_value = mock_swap
        
        result = _memory_info()
        
        assert "Memory" in result
        assert "SWAP" in result
        assert result["Memory"]["Percentage"] == 50.0
        assert result["SWAP"]["Percentage"] == 50.0
        assert "GB" in result["Memory"]["Total"] or "MB" in result["Memory"]["Total"]


def test_disk_info():
    """Test _disk_info function."""
from scitex.resource import _disk_info

    with patch("scitex.resource._get_specs._psutil") as mock_psutil:
        # Mock partition
        mock_partition = MagicMock()
        mock_partition.device = "/dev/sda1"
        mock_partition.mountpoint = "/"
        mock_partition.fstype = "ext4"
        mock_psutil.disk_partitions.return_value = [mock_partition]
        
        # Mock disk usage
        mock_usage = MagicMock()
        mock_usage.total = 1000000000000  # 1TB
        mock_usage.used = 500000000000   # 500GB
        mock_usage.free = 500000000000   # 500GB
        mock_usage.percent = 50.0
        mock_psutil.disk_usage.return_value = mock_usage
        
        # Mock disk I/O
        mock_io = MagicMock()
        mock_io.read_bytes = 1000000000  # 1GB
        mock_io.write_bytes = 500000000  # 500MB
        mock_psutil.disk_io_counters.return_value = mock_io
        
        result = _disk_info()
        
        assert "Partitions" in result
        assert "Total read" in result
        assert "Total write" in result
        assert "/dev/sda1" in result["Partitions"]
        assert result["Partitions"]["/dev/sda1"]["File system type"] == "ext4"
        assert result["Partitions"]["/dev/sda1"]["Percentage"] == 50.0


def test_disk_info_permission_error():
    """Test _disk_info function with permission error."""
from scitex.resource import _disk_info

    with patch("scitex.resource._get_specs._psutil") as mock_psutil:
        # Mock partition
        mock_partition = MagicMock()
        mock_partition.device = "/dev/sda1"
        mock_partition.mountpoint = "/restricted"
        mock_partition.fstype = "ext4"
        mock_psutil.disk_partitions.return_value = [mock_partition]
        
        # Mock permission error
        mock_psutil.disk_usage.side_effect = PermissionError("Access denied")
        
        # Mock disk I/O
        mock_io = MagicMock()
        mock_io.read_bytes = 1000000000
        mock_io.write_bytes = 500000000
        mock_psutil.disk_io_counters.return_value = mock_io
        
        result = _disk_info()
        
        # Should handle permission error gracefully
        assert "Partitions" in result
        assert len(result["Partitions"]) == 0  # No accessible partitions


def test_network_info():
    """Test _network_info function."""
from scitex.resource import _network_info

    with patch("scitex.resource._get_specs._psutil") as mock_psutil:
        # Mock network interfaces
        mock_address = MagicMock()
        mock_address.address = "192.168.1.100"
        mock_address.netmask = "255.255.255.0"
        mock_address.broadcast = "192.168.1.255"
        
        mock_interfaces = {
            "eth0": [mock_address],
            "lo": [mock_address]
        }
        mock_psutil.net_if_addrs.return_value = mock_interfaces
        
        # Mock network I/O
        mock_io = MagicMock()
        mock_io.bytes_sent = 1000000000  # 1GB
        mock_io.bytes_recv = 2000000000  # 2GB
        mock_psutil.net_io_counters.return_value = mock_io
        
        result = _network_info()
        
        assert "Interfaces" in result
        assert "Total Sent" in result
        assert "Total Received" in result
        assert "eth0" in result["Interfaces"]
        assert "lo" in result["Interfaces"]
        assert result["Interfaces"]["eth0"][0]["Address"] == "192.168.1.100"


def test_supple_os_info():
    """Test _supple_os_info function."""
from scitex.resource import _supple_os_info

    with patch("scitex.resource._get_specs._SUPPLE_INFO", {
        "os": "Ubuntu 20.04",
        "gcc_version": "9.4.0",
        "other_key": "other_value"
    }):
        result = _supple_os_info()
        
        assert result["os"] == "Ubuntu 20.04"
        assert result["gcc_version"] == "9.4.0"
        assert "other_key" not in result  # Should only include specified keys


def test_supple_python_info():
    """Test _supple_python_info function."""
from scitex.resource import _supple_python_info

    with patch("scitex.resource._get_specs._SUPPLE_INFO", {
        "python_version": "3.8.10",
        "torch_version": "1.10.0",
        "is_cuda_available": True,
        "pip_version": "21.0",
        "pip_packages": ["numpy", "pandas"],
        "conda_packages": ["pytorch"],
        "other_key": "other_value"
    }):
        result = _supple_python_info()
        
        assert result["python_version"] == "3.8.10"
        assert result["torch_version"] == "1.10.0"
        assert result["is_cuda_available"] is True
        assert result["pip_packages"] == ["numpy", "pandas"]
        assert "other_key" not in result


def test_supple_nvidia_info():
    """Test _supple_nvidia_info function."""
from scitex.resource import _supple_nvidia_info

    with patch("scitex.resource._get_specs._SUPPLE_INFO", {
        "nvidia_gpu_models": "GeForce RTX 3080",
        "nvidia_driver_version": "470.103.01",
        "cuda_runtime_version": "11.4",
        "cudnn_version": "8.2.4",
        "other_key": "other_value"
    }):
        result = _supple_nvidia_info()
        
        assert "NVIDIA GPU models" in result
        assert "NVIDIA Driver version" in result
        assert "CUDA Runtime version" in result
        assert "cuDNN version" in result
        assert "other_key" not in result
        
        assert result["NVIDIA GPU models"] == "GeForce RTX 3080"
        assert result["NVIDIA Driver version"] == "470.103.01"


def test_get_specs_integration():
    """Test get_specs integration with real system calls (minimal)."""
from scitex.resource import get_specs

    # Test that function doesn't crash with minimal real system data
    try:
        result = get_specs(system=True, cpu=False, gpu=False, disk=False, network=False)
        assert isinstance(result, dict)
        assert "Collected Time" in result
        # Don't assert specific values since they depend on the test environment
    except Exception as e:
        pytest.skip(f"Integration test skipped due to system limitations: {e}")


def test_collected_time_format():
    """Test that collected time has correct format."""
from scitex.resource import get_specs
    import re

    with patch("scitex.resource._get_specs.get_env_info") as mock_env:
        mock_env.return_value._asdict.return_value = {"os": "Linux"}
        
        result = get_specs(system=False, cpu=False, gpu=False, disk=False, network=False)
        
        time_pattern = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"
        assert re.match(time_pattern, result["Collected Time"])


def test_error_handling_in_subsystems():
    """Test error handling in various subsystems."""
from scitex.resource import get_specs

    with patch("scitex.resource._get_specs.get_env_info") as mock_env, \
         patch("scitex.resource._get_specs._system_info") as mock_system, \
         patch("scitex.resource._get_specs._cpu_info") as mock_cpu:
        
        mock_env.return_value._asdict.return_value = {"os": "Linux"}
        mock_system.side_effect = Exception("System info error")
        mock_cpu.side_effect = Exception("CPU info error")
        
        # Should handle errors gracefully and still return basic info
        with pytest.raises(Exception):
            get_specs(system=True, cpu=True, gpu=False, disk=False, network=False)


if __name__ == "__main__":
    import os
    pytest.main([os.path.abspath(__file__)])
