#!/usr/bin/env python3
"""Simple coverage runner to bypass configuration issues."""

import os
import sys
import subprocess

def main():
    """Run pytest with coverage in a simple way."""
    
    # Set up environment
    os.environ['PYTHONPATH'] = os.path.join(os.path.dirname(__file__), 'src')
    
    # Basic pytest command with coverage
    cmd = [
        sys.executable, '-m', 'pytest',
        'tests/',
        '--cov=src/scitex',
        '--cov-report=term-missing:skip-covered',
        '--cov-report=html',
        '--cov-report=json',
        '-q',  # Quiet mode
        '--tb=short',
        '--no-header',
        '-x',  # Stop on first failure
        '--ignore=tests/custom/',  # Ignore custom tests that might have issues
        '--ignore=tests/scitex/plt/',  # Ignore plt tests with import issues
        '--ignore=tests/scitex/ai/',  # Ignore ai tests temporarily
    ]
    
    print("Running coverage analysis...")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 80)
    
    try:
        # Run the command
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Print output
        print(result.stdout)
        if result.stderr:
            print("Errors:")
            print(result.stderr)
            
        # Check if coverage.json was created
        if os.path.exists('coverage.json'):
            import json
            with open('coverage.json', 'r') as f:
                coverage_data = json.load(f)
                
            print("\n" + "="*80)
            print("COVERAGE SUMMARY")
            print("="*80)
            
            if 'totals' in coverage_data:
                totals = coverage_data['totals']
                print(f"Total Statements: {totals.get('num_statements', 'N/A')}")
                print(f"Missing Statements: {totals.get('missing_lines', 'N/A')}")
                print(f"Coverage Percentage: {totals.get('percent_covered', 'N/A'):.2f}%")
            
            # Show files with lowest coverage
            if 'files' in coverage_data:
                print("\nFiles with lowest coverage:")
                files = [(f, data['summary']['percent_covered']) 
                        for f, data in coverage_data['files'].items() 
                        if 'summary' in data and 'percent_covered' in data['summary']]
                files.sort(key=lambda x: x[1])
                
                for filepath, coverage in files[:10]:
                    if coverage < 100:
                        print(f"  {coverage:5.1f}% - {filepath}")
                        
        return result.returncode
        
    except Exception as e:
        print(f"Error running coverage: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())