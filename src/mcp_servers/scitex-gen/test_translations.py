#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-02 06:37:00 (ywatanabe)"
# File: ./mcp_servers/scitex-gen/test_translations.py
# ----------------------------------------

"""Test gen module translations without MCP runtime."""

import sys
import os
import re
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class MockScitexGenTranslator:
    """Mock translator for testing gen module patterns."""
    
    def __init__(self):
        self.normalization_patterns = [
            (r"(\w+)\s*=\s*\((\w+)\s*-\s*np\.mean\((\w+)\)\)\s*/\s*np\.std\((\w+)\)", "manual_zscore"),
            (r"(\w+)\s*=\s*\((\w+)\s*-\s*(\w+)\.min\(\)\)\s*/\s*\((\w+)\.max\(\)\s*-\s*(\w+)\.min\(\)\)", "manual_minmax"),
        ]
        
    def translate_normalization(self, code):
        """Translate normalization operations to SciTeX."""
        translated = code
        conversions = []
        
        # Add import if needed
        if any(pattern[0] in code for pattern, _ in self.normalization_patterns):
            if "import scitex as stx" not in translated:
                translated = "import scitex as stx\n" + translated
        
        # Manual z-score
        zscore_pattern = r"(\w+)\s*=\s*\((\w+)\s*-\s*np\.mean\((\w+)\)\)\s*/\s*np\.std\((\w+)\)"
        matches = list(re.finditer(zscore_pattern, translated))
        for match in reversed(matches):
            var_out = match.group(1)
            var_in = match.group(2)
            if match.group(3) == var_in and match.group(4) == var_in:
                replacement = f"{var_out} = stx.gen.to_z({var_in})"
                translated = translated[:match.start()] + replacement + translated[match.end():]
                conversions.append("Converted manual z-score to stx.gen.to_z()")
        
        # Manual min-max
        minmax_pattern = r"(\w+)\s*=\s*\((\w+)\s*-\s*(\w+)\.min\(\)\)\s*/\s*\((\w+)\.max\(\)\s*-\s*(\w+)\.min\(\)\)"
        matches = list(re.finditer(minmax_pattern, translated))
        for match in reversed(matches):
            var_out = match.group(1)
            var_in = match.group(2)
            if all(match.group(i) == var_in for i in [3, 4, 5]):
                replacement = f"{var_out} = stx.gen.to_01({var_in})"
                translated = translated[:match.start()] + replacement + translated[match.end():]
                conversions.append("Converted manual min-max to stx.gen.to_01()")
        
        return translated, conversions
    
    def suggest_improvements(self, code):
        """Suggest gen module improvements."""
        suggestions = []
        
        # Check for manual normalization
        if re.search(r"\(.*-.*\.mean\(\)\).*\/.*\.std\(\)", code):
            suggestions.append({
                "issue": "Manual z-score normalization",
                "suggestion": "Use stx.gen.to_z() for cleaner z-score normalization",
                "example": "normalized = stx.gen.to_z(data)"
            })
        
        # Check for manual min-max
        if re.search(r"\(.*-.*\.min\(\)\).*\/.*\(.*\.max\(\).*-.*\.min\(\)\)", code):
            suggestions.append({
                "issue": "Manual min-max normalization",
                "suggestion": "Use stx.gen.to_01() for 0-1 normalization",
                "example": "scaled = stx.gen.to_01(data)"
            })
        
        # Check for caching opportunities
        if "@functools.lru_cache" in code or "@lru_cache" in code:
            suggestions.append({
                "issue": "Using functools caching",
                "suggestion": "Use @stx.gen.cache for simpler caching",
                "example": "@stx.gen.cache\ndef my_function(...):"
            })
        
        # Check for manual timestamps
        if "datetime.now()" in code or "time.time()" in code:
            count = code.count("datetime.now()") + code.count("time.time()")
            if count > 2:
                suggestions.append({
                    "issue": f"Multiple timestamp operations ({count} found)",
                    "suggestion": "Use stx.gen.TimeStamper for organized time tracking",
                    "example": "ts = stx.gen.TimeStamper()\nts.stamp('event')"
                })
        
        return suggestions


def test_translations():
    """Test gen module translation patterns."""
    translator = MockScitexGenTranslator()
    
    print("Testing SciTeX Gen Module Translation Patterns")
    print("=" * 60)
    
    # Test case 1: Manual normalization
    print("\n1. Testing normalization translations:")
    test_code1 = """
import numpy as np

# Load data
data = np.random.randn(1000, 50)

# Manual z-score normalization
data_normalized = (data - np.mean(data)) / np.std(data)

# Manual min-max scaling
data_scaled = (data - data.min()) / (data.max() - data.min())

# Process normalized data
result = np.dot(data_normalized, data_scaled.T)
"""
    
    translated1, conversions1 = translator.translate_normalization(test_code1)
    print("Original code:")
    print(test_code1)
    print("\nTranslated code:")
    print(translated1)
    print("\nConversions made:")
    for conv in conversions1:
        print(f"  - {conv}")
    
    # Test case 2: Complex example with multiple patterns
    print("\n\n2. Testing complex example:")
    test_code2 = """
import numpy as np
import functools
from datetime import datetime

@functools.lru_cache(maxsize=128)
def process_data(n):
    # Generate data
    data = np.random.randn(n, 10)
    
    # Normalize
    normalized = (data - np.mean(data)) / np.std(data)
    
    # Scale
    scaled = (data - data.min()) / (data.max() - data.min())
    
    # Track time
    start_time = datetime.now()
    result = np.corrcoef(normalized.T)
    end_time = datetime.now()
    
    print(f"Processing took: {end_time - start_time}")
    return result

# Multiple timestamps
for i in range(5):
    timestamp = datetime.now()
    print(f"Iteration {i} at {timestamp}")
    process_data(100)
"""
    
    suggestions2 = translator.suggest_improvements(test_code2)
    print("Code to analyze:")
    print(test_code2)
    print("\nImprovement suggestions:")
    for i, sugg in enumerate(suggestions2, 1):
        print(f"\n{i}. {sugg['issue']}")
        print(f"   Suggestion: {sugg['suggestion']}")
        print(f"   Example: {sugg['example']}")
    
    # Test case 3: Experiment setup pattern
    print("\n\n3. Testing experiment setup pattern:")
    experiment_template = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Experiment: neural_network_training
# ----------------------------------------

import scitex as stx

# Initialize experiment with reproducible settings
config = stx.gen.start(
    description="Train a neural network on MNIST dataset",
    config_path="./config/training.yaml",
    verbose=True
)

# Set up time tracking
ts = stx.gen.TimeStamper()
ts.stamp('Experiment started')

# Your experiment code here
data = stx.io.load('./data/mnist.npz')
data_normalized = stx.gen.to_z(data['train_images'])

# Model training would go here...

# Close experiment and save outputs
ts.stamp('Experiment completed')
stx.gen.close()
"""
    
    print("Generated experiment template:")
    print(experiment_template)
    
    # Test case 4: Reverse translation
    print("\n\n4. Testing reverse translation (SciTeX to standard Python):")
    scitex_code = """
import scitex as stx

# Normalization with gen module
data_z = stx.gen.to_z(data)
data_scaled = stx.gen.to_01(data)
data_clipped = stx.gen.clip_perc(data, percentile=95)

# Caching
@stx.gen.cache
def compute_features(x):
    return np.mean(x, axis=0)
"""
    
    # Simple reverse translation
    reverse_translated = scitex_code
    reverse_translated = reverse_translated.replace("stx.gen.to_z(data)", "(data - np.mean(data)) / np.std(data)")
    reverse_translated = reverse_translated.replace("stx.gen.to_01(data)", "(data - data.min()) / (data.max() - data.min())")
    reverse_translated = reverse_translated.replace("stx.gen.clip_perc(data, percentile=95)", "np.clip(data, *np.percentile(data, [5, 95]))")
    reverse_translated = reverse_translated.replace("@stx.gen.cache", "@functools.lru_cache(maxsize=None)")
    
    print("SciTeX code:")
    print(scitex_code)
    print("\nReverse translated to standard Python:")
    print(reverse_translated)
    
    print("\n" + "=" * 60)
    print("Translation tests completed successfully!")


if __name__ == "__main__":
    test_translations()

# EOF