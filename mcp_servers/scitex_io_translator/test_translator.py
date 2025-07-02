#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test script for scitex_io_translator

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from translators.io_translator import IOTranslator
from translators.template_translator import TemplateTranslator
from translators.validation_engine import ValidationEngine

def test_enhanced_translation():
    """Test the enhanced translation functionality."""
    
    translator = IOTranslator()
    template = TemplateTranslator()
    validator = ValidationEngine()
    
    # Test case with matplotlib patterns that should use ax.set_xyt()
    test_code = '''import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load data
df = pd.read_csv('input_data.csv')
array_data = np.load('features.npy')

# Visualize
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(df['x'], df['y'], label='Data')
ax.set_xlabel('X Values')
ax.set_ylabel('Y Values') 
ax.set_title('My Analysis Plot')
ax.legend()

# Save outputs  
df.to_csv('processed_data.csv')
np.save('results.npy', array_data * 2)
plt.savefig('analysis_plot.png')
'''

    print("=== ORIGINAL CODE ===")
    print(test_code)
    
    print("\n=== TRANSLATED TO SCITEX ===")
    translated = translator.translate_to_scitex(test_code)
    print(translated)
    
    print("\n=== WITH SCITEX BOILERPLATE ===")
    with_boilerplate = template.add_boilerplate(translated, preserve_comments=True)
    print(with_boilerplate)
    
    print("\n=== VALIDATION RESULTS ===")
    validation = validator.validate(with_boilerplate, strict=False)
    print(f"Errors: {len(validation['errors'])}")
    print(f"Warnings: {len(validation['warnings'])}")
    print(f"Suggestions: {len(validation['suggestions'])}")
    
    if validation['errors']:
        print("Errors found:")
        for error in validation['errors']:
            print(f"  - {error}")
    
    if validation['warnings']:
        print("Warnings:")
        for warning in validation['warnings']:
            print(f"  - {warning}")
    
    if validation['suggestions']:
        print("Suggestions:")
        for suggestion in validation['suggestions']:
            print(f"  - {suggestion}")

if __name__ == "__main__":
    test_enhanced_translation()