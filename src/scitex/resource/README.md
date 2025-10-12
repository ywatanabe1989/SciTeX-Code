<!-- ---
!-- title: README
!-- author: ywatanabe
!-- date: 2024-11-02 16:50:19
!-- --- -->


# [`scitex.resource`](https://github.com/ywatanabe1989/scitex/tree/main/src/scitex/resource/)

## Overview
The `scitex.resource` module provides comprehensive system resource monitoring and information gathering utilities. It offers an easy-to-use API for collecting detailed information about various system components, including CPU, memory, GPU, disk, and network.

## Installation
```bash
pip install scitex
```

## Features
- Comprehensive system information gathering
- Easy-to-use API for resource monitoring
- Support for CPU, memory, GPU, disk, and network information
- Output in easily readable and parsable formats (YAML, JSON)

## Quick Start
```python
import scitex

# Gather system information
info = scitex.resource.gather_info()

# Save the information to a file
scitex.io.save(info, "system_info.yaml")

# Print specific information
print(f"CPU Usage: {info['cpu']['usage']}%")
print(f"Total RAM: {info['memory']['total']} GB")
print(f"GPU Name: {info['gpu'][0]['name']}")

# Monitor system resources over time
for _ in range(10):
    cpu_usage = scitex.resource.get_cpu_usage()
    mem_usage = scitex.resource.get_memory_usage()
    print(f"CPU: {cpu_usage}%, Memory: {mem_usage}%")
    time.sleep(1)
```

## API Reference
- `scitex.resource.gather_info()`: Collects comprehensive system resource information
- `scitex.resource.get_cpu_info()`: Returns detailed CPU information
- `scitex.resource.get_memory_info()`: Returns memory usage statistics
- `scitex.resource.get_gpu_info()`: Returns GPU information (if available)
- `scitex.resource.get_disk_info()`: Returns disk usage and I/O statistics
- `scitex.resource.get_network_info()`: Returns network interface information
- `scitex.resource.get_cpu_usage()`: Returns current CPU usage percentage
- `scitex.resource.get_memory_usage()`: Returns current memory usage percentage

## Example Output
The `gather_info()` function returns a dictionary containing detailed system information. For a full example of the output, please refer to:
https://github.com/ywatanabe1989/scitex/tree/main/src/scitex/res/_gather_info/info.yaml

## Use Cases
- System monitoring and diagnostics
- Performance benchmarking
- Resource usage analysis
- Debugging hardware-related issues
- Generating system reports
- Automated system health checks

## Performance
The `scitex.resource` module is designed to be lightweight and efficient, with minimal impact on system performance during monitoring.

## Contributing
Contributions to improve `scitex.resource` are welcome. Please submit pull requests or open issues on the GitHub repository.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact
Yusuke Watanabe (ywatanabe@scitex.ai)

For more information and updates, please visit the [scitex GitHub repository](https://github.com/ywatanabe1989/scitex).
