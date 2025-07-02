<!-- ---
!-- Timestamp: 2025-06-29 09:52:32
!-- Author: ywatanabe
!-- File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/docs/from_user/scitex_translation_mcp_servers.md
!-- --- -->


Untitled chat
Shared by Yusuke
This is a copy of a chat between Claude and Yusuke. Content may include unverified or unsafe content that do not represent the views of Anthropic. Shared snapshot may contain attachments and data not displayed here.


<!-- --- !-- Timestamp: 2025-01-15 10:43:51 !-- Author: ywatanabe !-- File: ./src/scitex/io/README.md !-- --- --> # SciTeX IO Module The `scitex.io` module provides convenient functions for loading, saving, caching, and managing files and data in various formats. This guide will introduce some of

pasted

This is my io module of scitex pip pakcage

my scitex package has diverse modules like this  /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex:
  drwxr-sr-x 34 ywatanabe punim2354 4.0K Jun 26 09:20 .
  drwxr-sr-x  4 ywatanabe punim2354 4.0K Jun 21 13:39 ..
  drwxr-sr-x 18 ywatanabe punim2354 4.0K Jun 21 13:16 ai
  drwxr-sr-x  3 ywatanabe punim2354 4.0K Jun 21 14:04 context
  drwxr-sr-x  6 ywatanabe punim2354 4.0K Jun 21 14:04 db
  drwxr-sr-x  3 ywatanabe punim2354 4.0K Jun 21 14:04 decorators
  drwxr-sr-x  3 ywatanabe punim2354 4.0K Jun 21 14:04 dev
  drwxr-sr-x  3 ywatanabe punim2354 4.0K Jun 21 14:04 dict
  drwxr-sr-x  3 ywatanabe punim2354 4.0K Jun 21 13:16 dsp
  drwxr-sr-x  2 ywatanabe punim2354 4.0K Jun 13 22:53 dt
  drwxr-sr-x  2 ywatanabe punim2354 4.0K Jun 13 22:11 etc
  drwxr-sr-x  4 ywatanabe punim2354 4.0K Jun 21 14:04 gen
  drwxr-sr-x  2 ywatanabe punim2354 4.0K Jun 21 13:16 gists
  -rwxr-xr-x  1 ywatanabe punim2354 1.9K Jun 13 22:11 init.py
  drwxr-sr-x  5 ywatanabe punim2354 4.0K Jun 24 20:03 io
  drwxr-sr-x  2 ywatanabe punim2354 4.0K Jun 21 13:16 linalg
  -rwxr-xr-x  1 ywatanabe punim2354 2.1K Jun 13 22:11 main.py
  drwxr-sr-x  2 ywatanabe punim2354 4.0K Jun 21 13:16 nn
  drwxr-sr-x  2 ywatanabe punim2354 4.0K Jun 21 13:16 os
  drwxr-sr-x  2 ywatanabe punim2354 4.0K Jun 13 22:53 parallel
  drwxr-sr-x  3 ywatanabe punim2354 4.0K Jun 21 14:04 path
  drwxr-sr-x  2 ywatanabe punim2354 4.0K Jun 21 13:16 pd
  drwxr-sr-x  7 ywatanabe punim2354 4.0K Jun 21 14:04 plt
  drwxr-sr-x  2 ywatanabe punim2354 4.0K Jun 21 14:04 pycache
  drwxr-sr-x  3 ywatanabe punim2354 4.0K Jun 21 14:04 repro
  drwxr-sr-x  4 ywatanabe punim2354 4.0K Jun 21 13:16 resource
  drwxr-sr-x  2 ywatanabe punim2354 4.0K Jun 21 13:16 scholar
  -rwxr-xr-x  1 ywatanabe punim2354 1.4K Jun 13 22:51 _sh.py
  drwxr-sr-x  5 ywatanabe punim2354 4.0K Jun 21 13:16 stats
  drwxr-sr-x  3 ywatanabe punim2354 4.0K Jun 21 14:04 str
  drwxr-sr-x  2 ywatanabe punim2354 4.0K Jun 21 13:16 tex
  drwxr-sr-x  3 ywatanabe punim2354 4.0K Jun 21 14:04 torch
  drwxr-sr-x  2 ywatanabe punim2354 4.0K Jun 21 13:16 types
  drwxr-sr-x  3 ywatanabe punim2354 4.0K Jun 21 14:04 utils
  -rwxr-xr-x  1 ywatanabe punim2354  400 Jun 13 22:11 version.py
  drwxr-sr-x  2 ywatanabe punim2354 4.0K Jun 21 13:16 web


<!-- --- !-- Timestamp: 2025-06-14 06:38:24 !-- Author: ywatanabe !-- File: /home/ywatanabe/.dotfiles/.claude/to_claude/guidelines/python/IMPORTANT-SCITEX-01-basic.md !-- --- --> # SCITEX Basic Guidelines **!!! IMPORATANT !!!** **ANY PYTHON SCRIPTS MUST BE WRITTEN IN THE SCITEX FORMAT EXPLAINED BE

pasted

Then, i am planning to create MCP servers to translate any existing python code to follow scitex rules; and reverse translator as well. do you think this is ideal for users and agents to migrate to scitex? as scitex is designed to reduce code amount and reproducibility and readability for researchers but mgiration will be burden. for example, i have these scitex guidelines and it is not good for a single agent with every information given, beyond scitex.

Looking at your comprehensive scitex guidelines and the io module documentation, I think creating MCP servers for bidirectional translation is an excellent strategy for scitex adoption. Here's why this would be particularly valuable:

Why MCP Translation Servers Are Ideal
1. Reduces Migration Friction
Researchers can gradually adopt scitex without rewriting entire codebases
Existing matplotlib/pandas/numpy scripts can be automatically converted
Teams can maintain both scitex and standard Python versions during transition
2. Handles Complexity Distribution
Your scitex guidelines are indeed comprehensive (18+ different modules, specific patterns, etc.). An MCP server can:

Specialize in scitex-specific transformations
Maintain context about scitex conventions across translation sessions
Handle the cognitive load of remembering all the rules
3. Bidirectional Benefits
To scitex: Convert legacy research code to gain reproducibility benefits
From scitex: Share code with collaborators who don't use scitex
Validation: Round-trip translation to verify correctness
Recommended MCP Server Architecture

SciTeX MCP Server Design
Document 
Key Benefits for Adoption
1. Gradual Migration Path
Convert one script at a time
Maintain working standard Python versions
Learn scitex patterns through translation examples
2. Collaboration Bridge
Share with non-scitex users via reverse translation
Onboard team members gradually
Maintain compatibility with external tools
3. Quality Assurance
Automated compliance checking
Best practice suggestions
Round-trip validation ensures correctness
4. Cognitive Load Reduction
Agents don't need to memorize all 18+ guideline files
Specialized translation context
Consistent application of patterns
Implementation Priorities
Start with io module - Highest impact, clearest patterns
Add plt module - Visual feedback helps adoption
Framework conversion - Template and boilerplate handling
Config extraction - Advanced reproducibility features
This approach would make scitex much more accessible while preserving its benefits for reproducibility and standardization. The MCP servers could become essential tools for the research community transitioning to more standardized scientific computing practices.

Would you like me to elaborate on any specific aspect of this design or help you start implementing one of the translation servers?


SciTeX MCP Server Design
Server Structure
1. Core Translation Server (scitex-translator)
json
{
  "tools": [
    {
      "name": "translate_to_scitex",
      "description": "Convert standard Python to scitex format",
      "parameters": {
        "source_code": "string",
        "target_modules": ["io", "plt", "stats", "dsp"],
        "preserve_comments": "boolean",
        "add_config_support": "boolean"
      }
    },
    {
      "name": "translate_from_scitex", 
      "description": "Convert scitex code to standard Python",
      "parameters": {
        "scitex_code": "string",
        "target_style": "matplotlib|pandas|numpy",
        "include_dependencies": "boolean"
      }
    },
    {
      "name": "validate_scitex_compliance",
      "description": "Check if code follows scitex guidelines",
      "parameters": {
        "code": "string",
        "strict_mode": "boolean"
      }
    }
  ]
}
2. Module-Specific Servers
IO Translation Server (scitex-io-translator)
matplotlib.pyplot.savefig() → stx.io.save(fig, path, symlink_from_cwd=True)
pd.read_csv() → stx.io.load(path)
numpy.save() → stx.io.save(array, path)
Path management: relative path conversion
Config integration: extract hardcoded paths to ./config/PATH.yaml
Plotting Translation Server (scitex-plt-translator)
plt.subplots() → stx.plt.subplots()
ax.set_xlabel(), ax.set_ylabel(), ax.set_title() → ax.set_xyt()
Data tracking integration
Legend handling with separate export
Framework Translation Server (scitex-framework-translator)
Script template conversion
if __name__ == "__main__": → scitex run_main() pattern
Argument parsing integration
Config loading insertion
Translation Patterns
1. Standard Python → SciTeX
python
# Input (standard)
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

data = pd.read_csv('input.csv')
fig, ax = plt.subplots()
ax.plot(data['x'], data['y'])
ax.set_xlabel('X values')
ax.set_ylabel('Y values') 
ax.set_title('My Plot')
plt.savefig('output.png')

# Output (scitex)
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-29 12:00:00 (ywatanabe)"
# File: ./script.py
# ----------------------------------------
import os
__FILE__ = "./script.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import scitex as stx

def main(args):
    data = stx.io.load('./input.csv')
    fig, ax = stx.plt.subplots()
    ax.plot(data['x'], data['y'])
    ax.set_xyt('X values', 'Y values', 'My Plot')
    stx.io.save(fig, './output.png', symlink_from_cwd=True)
    return 0

# ... standard scitex boilerplate ...
2. SciTeX → Standard Python
python
# Input (scitex)
import scitex as stx
data = stx.io.load('./input.csv')
fig, ax = stx.plt.subplots()
ax.plot(data['x'], data['y'])
ax.set_xyt('X values', 'Y values', 'My Plot')
stx.io.save(fig, './output.png', symlink_from_cwd=True)

# Output (standard)
import matplotlib.pyplot as plt
import pandas as pd
import os

# Create output directory
os.makedirs('./output', exist_ok=True)

data = pd.read_csv('./input.csv')
fig, ax = plt.subplots()
ax.plot(data['x'], data['y'])
ax.set_xlabel('X values')
ax.set_ylabel('Y values')
ax.set_title('My Plot')
plt.savefig('./output/output.png')

# Export plot data to CSV
plot_data = pd.DataFrame({'x': data['x'], 'y': data['y']})
plot_data.to_csv('./output/output.csv', index=False)
Advanced Features
1. Configuration Extraction
Detect hardcoded paths and extract to PATH.yaml
Identify magic numbers for PARAMS.yaml
Color definitions to COLORS.yaml
2. Smart Path Conversion
Absolute paths → relative paths
CWD-relative → script-relative for saves
Config f-string generation
3. Dependency Management
Auto-detect required scitex modules
Generate appropriate import statements
Suggest config file templates
4. Validation & Suggestions
Check scitex compliance
Suggest improvements
Validate output directory patterns
Integration Strategy
Phase 1: Core Translation
Basic io/plt/framework translation
Template conversion
Path management
Phase 2: Advanced Features
Config extraction
Smart analysis
Round-trip validation
Phase 3: Ecosystem Integration
IDE plugins
Git hooks for automatic conversion
CI/CD integration
Example MCP Usage
python
# Agent using MCP server
import mcp

# Translate existing research code
result = mcp.call_tool("scitex-translator", "translate_to_scitex", {
    "source_code": legacy_code,
    "target_modules": ["io", "plt", "stats"],
    "add_config_support": True
})

# Validate compliance
compliance = mcp.call_tool("scitex-translator", "validate_scitex_compliance", {
    "code": result["translated_code"],
    "strict_mode": True
})

# Convert back for sharing
standard_code = mcp.call_tool("scitex-translator", "translate_from_scitex", {
    "scitex_code": result["translated_code"],
    "include_dependencies": True
})

<!-- EOF -->