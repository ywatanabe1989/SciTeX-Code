#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-29 10:25:00 (ywatanabe)"
# File: ./mcp_servers/examples/demo_translation.py
# ----------------------------------------

"""
Demo script showing SciTeX MCP server translations.
This demonstrates what the MCP servers can do for code migration.
"""

# Example 1: Standard matplotlib + pandas code
standard_code = '''
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load data
data = pd.read_csv('/home/user/experiments/results.csv')
config = pd.read_excel('config.xlsx')

# Process data
x = data['time'].values
y = data['signal'].values

# Create plot
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(x, y, 'b-', label='Signal')
ax.set_xlabel('Time (s)')
ax.set_ylabel('Amplitude')
ax.set_title('Signal Analysis')
ax.legend()

# Save outputs
plt.savefig('/home/user/experiments/figures/signal_plot.png')
data.to_csv('processed_data.csv', index=False)
'''

# Expected SciTeX translation
scitex_code = '''
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import scitex as stx

# Load data
data = stx.io.load('./results.csv')
config = stx.io.load('./config.xlsx')

# Process data
x = data['time'].values
y = data['signal'].values

# Create plot
fig, ax = stx.plt.subplots(figsize=(10, 6))
ax.plot(x, y, 'b-', label='Signal')
ax.set_xyt('Time (s)', 'Amplitude', 'Signal Analysis')
ax.legend()

# Save outputs
stx.io.save(fig, './figures/signal_plot.png', symlink_from_cwd=True)
stx.io.save(data, './processed_data.csv', symlink_from_cwd=True)
'''

print("=== Standard Python Code ===")
print(standard_code)
print("\n=== SciTeX Translation ===")
print(scitex_code)

print("\n=== Key Transformations ===")
print("1. pd.read_csv() → stx.io.load()")
print("2. plt.subplots() → stx.plt.subplots() [with data tracking]")
print("3. set_xlabel/ylabel/title → set_xyt() [combined method]")
print("4. Absolute paths → Relative paths")
print("5. savefig() → stx.io.save() [creates both .png and .csv]")
print("\n=== Benefits ===")
print("✅ Automatic CSV export of plot data")
print("✅ Path management with symlinks")
print("✅ Cleaner, more concise code")
print("✅ Better reproducibility")

# EOF