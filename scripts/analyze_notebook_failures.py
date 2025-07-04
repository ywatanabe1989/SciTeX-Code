#!/usr/bin/env python3
"""Analyze notebook execution failures to identify common issues."""

import json
import re
from pathlib import Path
from collections import defaultdict


def analyze_execution_results(results_file):
    """Analyze execution results to identify failure patterns."""
    with open(results_file, 'r') as f:
        data = json.load(f)
    
    results = data['results']
    
    # Categorize results
    success = [r for r in results if r['status'] == 'success']
    failed = [r for r in results if r['status'] == 'failed']
    errors = [r for r in results if r['status'] == 'error']
    
    print(f"Execution Summary:")
    print(f"  Total: {len(results)}")
    print(f"  Success: {len(success)} ({len(success)/len(results)*100:.1f}%)")
    print(f"  Failed: {len(failed)}")
    print(f"  Errors: {len(errors)}")
    
    # Analyze successful notebooks
    print("\nSuccessful Notebooks:")
    for r in success:
        print(f"  ✓ {r['notebook']} ({r['time']:.1f}s)")
    
    # Group failures by error pattern
    error_patterns = defaultdict(list)
    
    # Check executed notebooks for specific errors
    examples_dir = Path("/home/ywatanabe/proj/SciTeX-Code/examples")
    
    print("\nAnalyzing Failed Notebooks:")
    for r in failed + errors:
        notebook_name = r['notebook']
        executed_path = examples_dir / notebook_name.replace('.ipynb', '_executed.ipynb')
        
        if executed_path.exists():
            # Read the executed notebook to find error details
            try:
                with open(executed_path, 'r') as f:
                    content = f.read()
                
                # Look for common error patterns
                if 'TypeError' in content:
                    match = re.search(r'TypeError: ([^\n]+)', content)
                    if match:
                        error_patterns['TypeError'].append((notebook_name, match.group(1)))
                elif 'AttributeError' in content:
                    match = re.search(r'AttributeError: ([^\n]+)', content)
                    if match:
                        error_patterns['AttributeError'].append((notebook_name, match.group(1)))
                elif 'NameError' in content:
                    match = re.search(r'NameError: ([^\n]+)', content)
                    if match:
                        error_patterns['NameError'].append((notebook_name, match.group(1)))
                elif 'ImportError' in content:
                    match = re.search(r'ImportError: ([^\n]+)', content)
                    if match:
                        error_patterns['ImportError'].append((notebook_name, match.group(1)))
                elif 'missing' in content and 'argument' in content:
                    match = re.search(r'missing \d+ required .* argument[s]?: ([^\n]+)', content)
                    if match:
                        error_patterns['Missing Arguments'].append((notebook_name, match.group(0)))
                else:
                    error_patterns['Other'].append((notebook_name, 'Unknown error'))
                        
            except Exception as e:
                print(f"  Could not analyze {notebook_name}: {e}")
    
    # Report error patterns
    print("\nError Patterns Found:")
    for error_type, occurrences in error_patterns.items():
        print(f"\n{error_type}: {len(occurrences)} occurrences")
        
        # Group by similar errors
        error_messages = defaultdict(list)
        for notebook, error in occurrences:
            error_messages[error].append(notebook)
        
        for error, notebooks in list(error_messages.items())[:5]:  # Show top 5
            print(f"  '{error[:100]}...'")
            print(f"    Affected: {', '.join(notebooks[:3])}" + 
                  (f" and {len(notebooks)-3} more" if len(notebooks) > 3 else ""))
    
    return error_patterns


def suggest_fixes(error_patterns):
    """Suggest fixes based on error patterns."""
    print("\nSuggested Fixes:")
    print("=" * 50)
    
    fixes = []
    
    # Check for common issues
    for error_type, occurrences in error_patterns.items():
        if error_type == 'TypeError':
            for notebook, error in occurrences:
                if 'gen_footer()' in error:
                    fixes.append({
                        'issue': 'gen_footer() missing arguments',
                        'fix': 'Update gen_footer() calls to include required arguments',
                        'notebooks': [nb for nb, err in occurrences if 'gen_footer()' in err]
                    })
                elif 'notify()' in error:
                    fixes.append({
                        'issue': 'notify() unexpected keyword argument',
                        'fix': 'Update notify() calls to match new API',
                        'notebooks': [nb for nb, err in occurrences if 'notify()' in err]
                    })
                elif 'search()' in error:
                    fixes.append({
                        'issue': 'search() unexpected keyword argument',
                        'fix': 'Update search() calls to use correct parameter names',
                        'notebooks': [nb for nb, err in occurrences if 'search()' in err]
                    })
        
        elif error_type == 'AttributeError':
            for notebook, error in occurrences:
                if "'re.Pattern' object is not callable" in error:
                    fixes.append({
                        'issue': 'ansi_escape is a compiled regex, not a function',
                        'fix': 'Fix ansi_escape usage - it should be used as a regex pattern',
                        'notebooks': [nb for nb, err in occurrences if 're.Pattern' in err]
                    })
    
    # Remove duplicates
    seen = set()
    unique_fixes = []
    for fix in fixes:
        key = fix['issue']
        if key not in seen:
            seen.add(key)
            unique_fixes.append(fix)
    
    # Print fixes
    for i, fix in enumerate(unique_fixes, 1):
        print(f"\n{i}. {fix['issue']}")
        print(f"   Fix: {fix['fix']}")
        print(f"   Affected notebooks: {len(fix['notebooks'])}")
        for nb in fix['notebooks'][:3]:
            print(f"     - {nb}")
        if len(fix['notebooks']) > 3:
            print(f"     ... and {len(fix['notebooks'])-3} more")
    
    return unique_fixes


def main():
    """Analyze notebook failures and suggest fixes."""
    examples_dir = Path("/home/ywatanabe/proj/SciTeX-Code/examples")
    
    # Find the most recent execution results
    results_files = sorted(examples_dir.glob("execution_results_*.json"))
    
    if not results_files:
        print("No execution results found")
        return
    
    latest_results = results_files[-1]
    print(f"Analyzing: {latest_results.name}")
    print("=" * 50)
    
    error_patterns = analyze_execution_results(latest_results)
    fixes = suggest_fixes(error_patterns)
    
    print(f"\nTotal unique issues found: {len(fixes)}")
    
    # Save analysis
    analysis_file = examples_dir / "notebook_failure_analysis.json"
    with open(analysis_file, 'w') as f:
        json.dump({
            'results_file': str(latest_results),
            'error_patterns': {k: v for k, v in error_patterns.items()},
            'suggested_fixes': fixes
        }, f, indent=2)
    
    print(f"\nAnalysis saved to: {analysis_file}")


if __name__ == "__main__":
    main()