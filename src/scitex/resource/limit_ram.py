#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2021-09-20 21:02:04 (ywatanabe)"

import resource
import scitex


def limit_ram(ram_factor):
    soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    max_val = min(ram_factor * get_ram() * 1024, get_ram() * 1024)
    resource.setrlimit(resource.RLIMIT_AS, (max_val, hard))
    print(f"\nFree RAM was limited to {scitex.gen.fmt_size(max_val)}")


def get_ram():
    with open("/proc/meminfo", "r") as mem:
        free_memory = 0
        for i in mem:
            sline = i.split()
            if str(sline[0]) in ("MemFree:", "Buffers:", "Cached:"):
                free_memory += int(sline[1])
    return free_memory


# Backward compatibility
limit_RAM = limit_ram  # Deprecated: use limit_ram instead
get_RAM = get_ram  # Deprecated: use get_ram instead


if __name__ == "__main__":
    get_ram()
    limit_ram(0.1)
