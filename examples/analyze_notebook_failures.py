#!/usr/bin/env python3
"""Analyze common failure patterns in notebooks."""

import subprocess
import json
import sys
from pathlib import Path

# Test a subset of failing notebooks
notebooks_to_test = [
    '05_scitex_path.ipynb',
    '07_scitex_dict.ipynb',
    '08_scitex_types.ipynb',
    '14_scitex_plt.ipynb',
    '15_scitex_pd.ipynb'
]

failure_patterns = []

for notebook in notebooks_to_test:
    print(f'\n=== Testing {notebook} ===')
    
    try:
        result = subprocess.run(
            ['papermill', notebook, f'test_{notebook}'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            stderr = result.stderr if result.stderr else ''
            
            # Extract key error patterns
            if 'FileNotFoundError' in stderr:
                pattern = 'FileNotFoundError - Missing directory'
            elif 'AttributeError' in stderr:
                pattern = 'AttributeError - API mismatch'
            elif 'NameError' in stderr:
                pattern = 'NameError - Undefined variable'
            elif 'TypeError' in stderr:
                pattern = 'TypeError - Function signature mismatch'
            elif 'ModuleNotFoundError' in stderr:
                pattern = 'ModuleNotFoundError - Missing import'
            else:
                pattern = 'Unknown error'
            
            # Extract specific error message
            error_lines = stderr.strip().split('\n')
            if error_lines:
                error_msg = error_lines[-1][:200]  # Last line, truncated
            else:
                error_msg = 'No error message'
            
            failure_patterns.append({
                'notebook': notebook,
                'pattern': pattern,
                'error_msg': error_msg,
                'return_code': result.returncode
            })
            
            print(f'  Pattern: {pattern}')
            print(f'  Error: {error_msg[:100]}...')
        else:
            print('  SUCCESS')
            
    except subprocess.TimeoutExpired:
        failure_patterns.append({
            'notebook': notebook,
            'pattern': 'Timeout - Execution too long',
            'error_msg': 'Process timed out after 30 seconds',
            'return_code': -1
        })
        print('  Pattern: Timeout')
    except Exception as e:
        failure_patterns.append({
            'notebook': notebook,
            'pattern': f'Exception - {type(e).__name__}',
            'error_msg': str(e),
            'return_code': -2
        })
        print(f'  Exception: {e}')

# Save analysis results
with open('notebook_failure_patterns.json', 'w') as f:
    json.dump(failure_patterns, f, indent=2)

# Print summary
print('\n\n=== SUMMARY ===')
pattern_counts = {}
for fp in failure_patterns:
    pattern = fp['pattern']
    pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1

for pattern, count in sorted(pattern_counts.items()):
    print(f'{pattern}: {count} notebooks')

print(f'\nTotal failures analyzed: {len(failure_patterns)}')
print('Results saved to notebook_failure_patterns.json')