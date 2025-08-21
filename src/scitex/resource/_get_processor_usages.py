#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-04 16:12:50 (ywatanabe)"
# File: ./scitex_repo/src/scitex/resource/_get_processor_usages.py

"""
Functionality:
    * Monitors and records system resource utilization (CPU, RAM, GPU, VRAM)
Input:
    * None (uses system calls and psutil library)
Output:
    * DataFrame containing resource usage statistics
Prerequisites:
    * NVIDIA GPU with nvidia-smi installed
    * psutil package
"""

import os
import subprocess
import sys
from datetime import datetime
from typing import Optional, Tuple

import matplotlib.pyplot as plt
import pandas as pd
import psutil


def get_processor_usages() -> pd.DataFrame:
    """Gets current system resource usage statistics.

    Returns
    -------
    pd.DataFrame
        Resource usage data with columns:
        - Timestamp: Timestamp
        - CPU [%]: CPU utilization
        - RAM [GiB]: RAM usage
        - GPU [%]: GPU utilization
        - VRAM [GiB]: VRAM usage

    Example
    -------
    >>> df = get_proccessor_usages()
    >>> print(df)
                 Timestamp  CPU [%]  RAM [GiB]  GPU [%]  VRAM [GiB]
    0  2024-11-04 10:30:15    25.3      8.2     65.0        4.5
    """
    try:
        cpu_perc, ram_gb = _get_cpu_usage()
        gpu_perc, vram_gb = _get_gpu_usage()

        sr = pd.Series(
            {
                "Timestamp": datetime.now(),
                "CPU [%]": cpu_perc,
                "RAM [GiB]": ram_gb,
                "GPU [%]": gpu_perc,
                "VRAM [GiB]": vram_gb,
            }
        )

        return pd.DataFrame(sr).round(1).T
    except Exception as err:
        raise RuntimeError(f"Failed to get resource usage: {err}")


def _get_cpu_usage(
    process: Optional[int] = os.getpid(), n_round: int = 1
) -> Tuple[float, float]:
    """Gets CPU and RAM usage statistics.

    Parameters
    ----------
    process : int, optional
        Process ID to monitor
    n_round : int, optional
        Number of decimal places to round to

    Returns
    -------
    Tuple[float, float]
        CPU usage percentage and RAM usage in GiB
    """
    try:
        cpu_usage_perc = psutil.cpu_percent()
        ram_usage_gb = (
            psutil.virtual_memory().percent
            / 100
            * psutil.virtual_memory().total
            / (1024**3)
        )
        return round(cpu_usage_perc, n_round), round(ram_usage_gb, n_round)
    except Exception as err:
        raise RuntimeError(f"Failed to get CPU/RAM usage: {err}")


def _get_gpu_usage(n_round: int = 1) -> Tuple[float, float]:
    """Gets GPU and VRAM usage statistics.

    Parameters
    ----------
    n_round : int, optional
        Number of decimal places to round to

    Returns
    -------
    Tuple[float, float]
        GPU usage percentage and VRAM usage in GiB
    """
    try:
        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=utilization.gpu,memory.used",
                "--format=csv,nounits,noheader",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        gpu_usage_perc, vram_usage_mib = result.stdout.strip().split(",")
        vram_usage_gb = float(vram_usage_mib) / 1024
        return round(float(gpu_usage_perc), n_round), round(vram_usage_gb, n_round)
    except:
        return 0.0, 0.0
    # except subprocess.CalledProcessError as err:
    #     raise RuntimeError(f"Failed to execute nvidia-smi: {err}")
    # except Exception as err:
    #     raise RuntimeError(f"Failed to get GPU/VRAM usage: {err}")


# def _get_gpu_usage(n_round: int = 1) -> Tuple[float, float]:
#     """Gets GPU and VRAM usage statistics.

#     Parameters
#     ----------
#     n_round : int, optional
#         Number of decimal places to round to

#     Returns
#     -------
#     Tuple[float, float]
#         GPU usage percentage and VRAM usage in GiB
#     """
#     try:
#         result = subprocess.run(
#             [
#                 "nvidia-smi",
#                 "--query-gpu=utilization.gpu,memory.used",
#                 "--format=csv,nounits,noheader",
#             ],
#             capture_output=True,
#             text=True,
#             check=True,
#         )
#         gpu_usage_perc, vram_usage_mib = result.stdout.strip().split(",")
#         vram_usage_gb = float(vram_usage_mib) / 1024
#         return round(float(gpu_usage_perc), n_round), round(vram_usage_gb, n_round)
#     except Exception as e:
#         print(e)
#         return 0.0, 0.0  # Return zeros when nvidia-smi is not available


if __name__ == "__main__":
    import scitex

    CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.session.start(sys, plt, verbose=False)

    usage = scitex.resource.get_processor_usages()
    scitex.io.save(usage, "usage.csv")

    scitex.session.close(CONFIG, verbose=False, notify=False)

# EOF

# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-04 10:27:35 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/resource/_get_processor_usages.py

# """
# This script does XYZ.
# """

# # Functions
# import os
# import subprocess
# import sys
# from datetime import datetime

# import matplotlib.pyplot as plt
# import scitex
# import pandas as pd
# import psutil


# # Functions
# def get_processor_usages():
#     """
#     Retrieves the current usage statistics for the CPU, RAM, GPU, and VRAM.

#     This function fetches the current usage percentages for the CPU and GPU, as well as the current usage in GiB for RAM and VRAM.
#     The data is then compiled into a pandas DataFrame with the current timestamp.

#     Returns:
#         pd.DataFrame: A pandas DataFrame containing the current usage statistics with the following columns:
#                       - Time: The timestamp when the data was retrieved.
#                       - CPU [%]: The CPU usage percentage.
#                       - RAM [GiB]: The RAM usage in GiB.
#                       - GPU [%]: The GPU usage percentage.
#                       - VRAM [GiB]: The VRAM usage in GiB.
#                       Each row in the DataFrame represents a single instance of data retrieval, rounded to 1 decimal place.

#     Example:
#         >>> usage_df = get_processor_usages()
#         >>> print(usage_df)
#     """
#     cpu_perc, ram_gb = _get_cpu_usage()
#     gpu_perc, vram_gb = _get_gpu_usage()

#     sr = pd.Series(
#         {
#             "Time": datetime.now(),
#             "CPU [%]": cpu_perc,
#             "RAM [GiB]": ram_gb,
#             "GPU [%]": gpu_perc,
#             "VRAM [GiB]": vram_gb,
#         }
#     )

#     df = pd.DataFrame(sr).round(1).T

#     return df


# def _get_cpu_usage(process=os.getpid(), n_round=1):
#     cpu_usage_perc = psutil.cpu_percent()
#     ram_usage_gb = (
#         psutil.virtual_memory().percent
#         / 100
#         * psutil.virtual_memory().total
#         / (1024**3)
#     )
#     return round(cpu_usage_perc, n_round), round(ram_usage_gb, n_round)


# def _get_gpu_usage(n_round=1):
#     result = subprocess.run(
#         [
#             "nvidia-smi",
#             "--query-gpu=utilization.gpu,memory.used",
#             "--format=csv,nounits,noheader",
#         ],
#         capture_output=True,
#         text=True,
#     )
#     gpu_usage_perc, _vram_usage_mib = result.stdout.strip().split(",")
#     vram_usage_gb = float(_vram_usage_mib) / 1024
#     return round(float(gpu_usage_perc), n_round), round(
#         float(vram_usage_gb), n_round
#     )


# # (YOUR AWESOME CODE)

# if __name__ == "__main__":
#     # Start
#     CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.session.start(
#         sys, plt, verbose=False
#     )

#     usage = scitex.resource.get_processor_usages()
#     scitex.io.save(usage, "usage.csv")

#     # Close
#     scitex.session.close(CONFIG, verbose=False, notify=False)

#

# EOF
