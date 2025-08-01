<!-- ---
!-- Timestamp: 2025-08-01 11:09:00
!-- Author: d833c9e2-6e28-11f0-8201-00155dff963d
!-- File: ./docs/from_agents/import_issues_analysis_20250801.md
!-- --- -->

# Import Issues Analysis Report

## Overview
Analysis of import issues in the SciTeX codebase revealed several missing optional dependencies. These are primarily for specialized features and do not affect core functionality.

## Import Issues Found

### 1. Machine Learning Dependencies
- **imblearn** (imbalanced-learn): Used in `ai/sampling/undersample.py`
  - Purpose: Undersampling techniques for imbalanced datasets
  - Solution: Add to optional dependencies or implement fallback

- **pytorch_optimizer**: Used in `ai/optim/_optimizers.py`
  - Purpose: Additional optimizers beyond standard PyTorch
  - Solution: Make optional with graceful fallback to standard optimizers

### 2. Signal Processing
- **wavelets_pytorch**: Used in `nn/_Spectrogram.py`
  - Purpose: Wavelet transforms for spectrograms
  - Solution: Implement conditional import with feature flag

### 3. PDF Processing
- **PyPDF2**: Used in multiple locations
  - `io/_load_modules/_pdf.py`
  - `scholar/validation/_PDFValidator.py`
  - Purpose: PDF reading and validation
  - Solution: Already handles with try-except, could improve error messages

- **pdfplumber**: Used in `scholar/validation/_PDFValidator.py`
  - Purpose: Advanced PDF text extraction
  - Solution: Optional dependency for enhanced PDF processing

- **python-magic**: Used in legacy code
  - Location: `scholar/.old/` directories
  - Purpose: File type detection
  - Solution: Not critical - in old/deprecated code

### 4. Vector Database
- **faiss**: Successfully loads but shows GPU warning
  - Warning is informational only
  - CPU version works correctly
  - No action needed

## Recommendations

### Immediate Actions
1. **Update requirements.txt** with optional dependencies section:
   ```
   # Optional dependencies for specialized features
   # pip install scitex[ml]  # For ML features
   imblearn>=0.10.0
   pytorch-optimizer>=2.0.0
   
   # pip install scitex[pdf]  # For PDF processing
   PyPDF2>=3.0.0
   pdfplumber>=0.9.0
   
   # pip install scitex[signal]  # For advanced signal processing
   wavelets-pytorch>=1.0.0
   ```

2. **Improve Import Error Handling**
   - Add informative error messages when optional dependencies are missing
   - Suggest installation commands for missing features

3. **Create Feature Flags**
   - Implement feature detection for optional modules
   - Gracefully disable features when dependencies are missing

### Long-term Improvements
1. **Modularize Optional Features**
   - Create separate pip extras for different feature sets
   - Allow users to install only what they need

2. **Documentation Updates**
   - Document which features require which dependencies
   - Add installation guide for optional features

3. **CI/CD Enhancement**
   - Test with minimal dependencies
   - Test with full dependencies
   - Ensure graceful degradation

## Impact Assessment
- **Core Functionality**: ✅ Not affected
- **Optional Features**: ⚠️ May fail without proper dependencies
- **User Experience**: Could be improved with better error messages

## Code Quality Notes
- Most modules already handle import errors gracefully
- Legacy code in `.old/` directories can be ignored
- Main codebase follows good practices for optional imports

---
These import issues are typical for a scientific computing library with optional features. The core library remains functional, and the issues only affect specialized use cases.

<!-- EOF -->