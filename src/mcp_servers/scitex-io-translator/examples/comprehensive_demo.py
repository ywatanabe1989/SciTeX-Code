#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-02 06:48:00 (ywatanabe)"
# File: ./examples/comprehensive_demo.py
# ----------------------------------------
"""
Comprehensive demonstration of SciTeX IO Translator MCP Server capabilities.
Shows various translation scenarios and patterns.
"""

import json
import asyncio
from pathlib import Path

# Sample code snippets for testing various translation patterns
SAMPLE_CODES = {
    "basic_pandas": """
import pandas as pd
import numpy as np

# Read data
df = pd.read_csv('data/raw_data.csv')
df_processed = df.groupby('category').mean()

# Save results
df_processed.to_csv('results/processed_data.csv', index=False)
""",
    
    "matplotlib_visualization": """
import matplotlib.pyplot as plt
import pandas as pd

data = pd.read_csv('measurements.csv')

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

ax1.plot(data['time'], data['signal'])
ax1.set_xlabel('Time (s)')
ax1.set_ylabel('Amplitude')
ax1.set_title('Signal Analysis')

ax2.hist(data['signal'], bins=50)
ax2.set_xlabel('Amplitude')
ax2.set_ylabel('Frequency')
ax2.set_title('Signal Distribution')

plt.tight_layout()
plt.savefig('signal_analysis.png', dpi=300)
""",
    
    "numpy_operations": """
import numpy as np
import pickle

# Load arrays
X = np.load('features.npy')
y = np.load('labels.npy')

# Process data
X_normalized = (X - X.mean(axis=0)) / X.std(axis=0)
correlation_matrix = np.corrcoef(X_normalized.T)

# Save results
np.save('features_normalized.npy', X_normalized)
np.save('correlation_matrix.npy', correlation_matrix)

# Save model
model = {'X': X_normalized, 'y': y, 'corr': correlation_matrix}
with open('model.pkl', 'wb') as f:
    pickle.dump(model, f)
""",
    
    "mixed_io_operations": """
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
import pickle

# Configuration
with open('config.json', 'r') as f:
    config = json.load(f)

# Load data from multiple sources
df = pd.read_csv(config['data_file'])
embeddings = np.load(config['embeddings_file'])

# Process
results = {
    'mean': df.mean().to_dict(),
    'std': df.std().to_dict(),
    'embedding_shape': embeddings.shape
}

# Save outputs
df.describe().to_csv('summary_stats.csv')
np.savez('processed_arrays.npz', embeddings=embeddings, stats=df.values)

with open('results.json', 'w') as f:
    json.dump(results, f, indent=2)

# Visualization
plt.figure(figsize=(12, 6))
plt.subplot(121)
plt.plot(df['value'])
plt.title('Time Series')
plt.subplot(122)
plt.imshow(embeddings[:100], aspect='auto')
plt.title('Embeddings')
plt.savefig('analysis_results.pdf')
""",
    
    "absolute_paths": """
import pandas as pd
import os

# Using absolute paths (bad practice)
df = pd.read_csv('/home/user/project/data/input.csv')
df.to_csv('/home/user/project/output/results.csv')

# Using parent directories
df2 = pd.read_csv('../../../shared_data/dataset.csv')
df2.to_csv('../../outputs/processed.csv')

# Mixed path styles
import numpy as np
arr = np.load('C:\\Users\\Name\\Documents\\data.npy')
np.save('/tmp/output.npy', arr)
"""
}


def print_translation_result(name: str, result: dict):
    """Pretty print translation results."""
    print(f"\n{'='*60}")
    print(f"TRANSLATION: {name}")
    print(f"{'='*60}")
    
    if result.get('success'):
        print("\n✓ Translation successful!")
        
        if 'translated_code' in result:
            print("\n--- Translated Code ---")
            print(result['translated_code'])
        
        if 'validation' in result:
            val = result['validation']
            print(f"\n--- Validation ---")
            print(f"Errors: {len(val.get('errors', []))}")
            print(f"Warnings: {len(val.get('warnings', []))}")
            print(f"Suggestions: {len(val.get('suggestions', []))}")
            
            if val.get('errors'):
                print("\nErrors:")
                for err in val['errors']:
                    print(f"  • {err}")
            
            if val.get('warnings'):
                print("\nWarnings:")
                for warn in val['warnings']:
                    print(f"  • {warn}")
            
            if val.get('suggestions'):
                print("\nSuggestions:")
                for sug in val['suggestions']:
                    print(f"  • {sug}")
        
        if 'config_files' in result and result['config_files']:
            print("\n--- Generated Config Files ---")
            for filename, content in result['config_files'].items():
                print(f"\n{filename}:")
                print(content)
        
        if 'changes_made' in result:
            print(f"\n--- Changes Summary ---")
            for key, value in result['changes_made'].items():
                print(f"{key}: {value}")
    
    else:
        print(f"\n✗ Translation failed: {result.get('error')}")


async def demonstrate_translations():
    """Demonstrate various translation scenarios."""
    
    # Note: In real usage, these would be called through the MCP protocol
    # This is a simulation to show expected inputs/outputs
    
    print("SciTeX IO Translator MCP Server - Comprehensive Demo")
    print("=" * 60)
    
    # Simulate translation calls
    for name, code in SAMPLE_CODES.items():
        # Simulate translate_to_scitex call
        result = {
            "tool": "translate_to_scitex",
            "arguments": {
                "source_code": code,
                "target_modules": ["io"],
                "preserve_comments": True,
                "add_config_support": name == "mixed_io_operations"
            }
        }
        
        print(f"\n\n{'#'*60}")
        print(f"# Testing: {name}")
        print(f"{'#'*60}")
        
        print("\n--- Original Code ---")
        print(code)
        
        print("\n--- MCP Request ---")
        print(json.dumps(result, indent=2))
        
        # Show what the expected translation would look like
        # (In real usage, this would come from the MCP server)
        print("\n--- Expected SciTeX Translation ---")
        
        if name == "basic_pandas":
            expected = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-02 06:48:00 (ywatanabe)"
# File: ./script.py
# ----------------------------------------
import os
__FILE__ = "./script.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import scitex as stx

def main():
    """Main function."""
    # Read data
    df = stx.io.load('./data/raw_data.csv')
    df_processed = df.groupby('category').mean()
    
    # Save results
    stx.io.save(df_processed, './results/processed_data.csv', index=False, symlink_from_cwd=True)
    return 0

def run_main():
    """Run main function with proper setup."""
    import sys
    CONFIG, sys.stdout, sys.stderr, plt, CC = stx.gen.start(
        sys, plt, verbose=True
    )
    main(CONFIG)
    stx.gen.close(CONFIG, verbose=True)

if __name__ == "__main__":
    run_main()"""
            print(expected)
        
        elif name == "absolute_paths":
            print("(Paths converted to relative, organized by type)")
            print("• /home/user/project/data/input.csv → ./data/input.csv")
            print("• /home/user/project/output/results.csv → ./output/results.csv")
            print("• C:\\Users\\Name\\Documents\\data.npy → ./data.npy")
            print("• /tmp/output.npy → ./output.npy")


def demonstrate_reverse_translation():
    """Show reverse translation from SciTeX to standard Python."""
    
    print("\n\n" + "="*60)
    print("REVERSE TRANSLATION DEMO")
    print("="*60)
    
    scitex_code = """import scitex as stx

def main():
    # Load and process data
    df = stx.io.load('./data/measurements.csv')
    processed = df.rolling(window=10).mean()
    
    # Create visualization
    fig, ax = stx.plt.subplots()
    ax.plot(processed['value'])
    ax.set_xyt('Time', 'Value', 'Rolling Average')
    
    # Save outputs
    stx.io.save(processed, './results/rolling_avg.csv', symlink_from_cwd=True)
    stx.io.save(fig, './figures/rolling_plot.png', symlink_from_cwd=True)
"""
    
    print("\n--- SciTeX Code ---")
    print(scitex_code)
    
    print("\n--- MCP Request ---")
    request = {
        "tool": "translate_from_scitex",
        "arguments": {
            "scitex_code": scitex_code,
            "target_style": "pandas",
            "include_dependencies": True
        }
    }
    print(json.dumps(request, indent=2))
    
    print("\n--- Expected Standard Python ---")
    expected = """import pandas as pd
import matplotlib.pyplot as plt
import os

# Create output directories
os.makedirs(os.path.dirname("./results/rolling_avg.csv"), exist_ok=True)
os.makedirs(os.path.dirname("./figures/rolling_plot.png"), exist_ok=True)

def main():
    # Load and process data
    df = pd.read_csv('./data/measurements.csv')
    processed = df.rolling(window=10).mean()
    
    # Create visualization
    fig, ax = plt.subplots()
    ax.plot(processed['value'])
    ax.set_xlabel('Time')
    ax.set_ylabel('Value')
    ax.set_title('Rolling Average')
    
    # Save outputs
    processed.to_csv('./results/rolling_avg.csv')
    plt.savefig('./figures/rolling_plot.png')"""
    print(expected)


def demonstrate_validation():
    """Show validation capabilities."""
    
    print("\n\n" + "="*60)
    print("VALIDATION DEMO")
    print("="*60)
    
    code_to_validate = """import scitex as stx
import pandas as pd

# Missing proper header
df = pd.read_csv('data.csv')  # Should use stx.io.load
plt.savefig('/tmp/plot.png')  # Absolute path

# Good practice
result = stx.io.load('./input.csv')
stx.io.save(result, './output/result.csv')
"""
    
    print("\n--- Code to Validate ---")
    print(code_to_validate)
    
    print("\n--- MCP Request ---")
    request = {
        "tool": "validate_scitex_compliance",
        "arguments": {
            "code": code_to_validate,
            "strict_mode": True
        }
    }
    print(json.dumps(request, indent=2))
    
    print("\n--- Expected Validation Results ---")
    print("Errors:")
    print("  • Missing shebang: #!/usr/bin/env python3")
    print("  • Missing encoding declaration")
    print("  • Missing timestamp in header")
    print("  • Missing __FILE__ definition")
    print("  • Missing __DIR__ definition")
    print("\nWarnings:")
    print("  • Use stx.io.load() instead of pd.read_csv()")
    print("  • Use stx.io.save() instead of plt.savefig()")
    print("  • Avoid absolute paths; use relative paths starting with ./")
    print("\nSuggestions:")
    print("  • Consider organizing image outputs in ./figures/")
    print("  • Consider using symlink_from_cwd=True for outputs")


if __name__ == "__main__":
    # Run demonstrations
    asyncio.run(demonstrate_translations())
    demonstrate_reverse_translation()
    demonstrate_validation()
    
    print("\n\n" + "="*60)
    print("Demo completed!")
    print("\nTo use these translations in practice:")
    print("1. Install the MCP server: pip install -e .")
    print("2. Configure in Claude Desktop or your MCP client")
    print("3. Call the tools through the MCP protocol")
    print("="*60)