# SciTeX Docstring Template and Guidelines

## Overview
This document provides templates and guidelines for writing consistent, informative docstrings throughout the SciTeX codebase. We follow the NumPy docstring style, which is well-suited for scientific Python packages.

## General Principles
1. **Every public API must have a docstring**
2. **Be concise but complete**
3. **Include types in both docstring and type hints**
4. **Provide examples for complex functions**
5. **Document edge cases and exceptions**

## Module Docstrings

```python
#!/usr/bin/env python3
"""
Brief one-line description of module.

Longer description explaining the module's purpose, main functionality,
and any important notes. This can span multiple paragraphs if needed.

Key Functions
-------------
function_name : Brief description
another_function : Brief description

Examples
--------
>>> import scitex.module_name
>>> result = scitex.module_name.function(data)

Notes
-----
Any implementation notes, performance considerations, or other details
that users should be aware of.
"""
```

## Function Docstrings

### Basic Function Template
```python
def function_name(param1: type1, param2: type2 = default) -> return_type:
    """
    Brief one-line description ending with period.
    
    Longer description if needed, explaining what the function does,
    any algorithms used, or important behaviors.
    
    Parameters
    ----------
    param1 : type1
        Description of param1. Note that type is repeated here
        for readability in documentation.
    param2 : type2, default=default_value
        Description of param2. Always specify defaults.
        
    Returns
    -------
    return_type
        Description of what is returned.
        
    Examples
    --------
    >>> result = function_name(input1, input2)
    >>> print(result)
    expected_output
    """
```

### Complex Function Template
```python
def complex_function(
    data: np.ndarray,
    method: str = "auto",
    **kwargs: Any
) -> Tuple[np.ndarray, Dict[str, Any]]:
    """
    Brief one-line description.
    
    Detailed explanation of what the function does, including any
    mathematical formulas or algorithms used.
    
    Parameters
    ----------
    data : np.ndarray of shape (n_samples, n_features)
        Input data array. Must be 2-dimensional.
    method : {'auto', 'fast', 'accurate'}, default='auto'
        Method to use for computation:
        - 'auto': Automatically choose based on data size
        - 'fast': Use approximate algorithm for speed
        - 'accurate': Use exact algorithm for precision
    **kwargs : dict
        Additional keyword arguments:
        - tolerance : float, default=1e-6
            Convergence tolerance
        - max_iter : int, default=100
            Maximum iterations
            
    Returns
    -------
    result : np.ndarray of shape (n_samples, n_components)
        Transformed data array.
    info : dict
        Dictionary containing:
        - 'converged': bool, whether algorithm converged
        - 'n_iter': int, number of iterations used
        - 'error': float, final error value
        
    Raises
    ------
    ValueError
        If input data is not 2-dimensional.
    ConvergenceWarning
        If algorithm fails to converge within max_iter.
        
    See Also
    --------
    related_function : Brief description of related functionality.
    another_function : Another related function.
    
    Notes
    -----
    This implementation follows the algorithm described in [1]_.
    For large datasets (n_samples > 10000), consider using
    method='fast' for better performance.
    
    References
    ----------
    .. [1] Author, A. (2020). "Paper Title". Journal Name.
    
    Examples
    --------
    Basic usage:
    
    >>> data = np.random.randn(100, 10)
    >>> result, info = complex_function(data, method='fast')
    >>> result.shape
    (100, 5)
    
    With custom parameters:
    
    >>> result, info = complex_function(
    ...     data,
    ...     method='accurate',
    ...     tolerance=1e-8,
    ...     max_iter=200
    ... )
    >>> info['converged']
    True
    """
```

## Class Docstrings

```python
class DataProcessor:
    """
    Brief one-line description of the class.
    
    Longer description explaining the class purpose, main use cases,
    and any important design decisions.
    
    Parameters
    ----------
    param1 : type
        Description of initialization parameter.
    param2 : type, optional
        Optional parameter with default behavior explained.
        
    Attributes
    ----------
    attribute1 : type
        Description of public attribute.
    attribute2 : type
        Another public attribute.
        
    Methods
    -------
    process(data)
        Brief description of main method.
    transform(data, method='auto')
        Brief description of another method.
        
    Examples
    --------
    >>> processor = DataProcessor(param1=value1)
    >>> result = processor.process(data)
    
    Notes
    -----
    Implementation notes or performance considerations.
    """
    
    def __init__(self, param1: type1, param2: type2 = None):
        """Initialize DataProcessor."""  # Brief init docstring
        
    def process(self, data: np.ndarray) -> np.ndarray:
        """
        Process input data.
        
        Full docstring following function template...
        """
```

## Property Docstrings

```python
@property
def sample_rate(self) -> float:
    """
    Sample rate in Hz.
    
    Returns
    -------
    float
        The sampling frequency of the data.
    """
    return self._sample_rate
```

## Special Cases

### Generator Functions
```python
def data_generator(filepath: str, batch_size: int = 32) -> Iterator[np.ndarray]:
    """
    Generate batches of data from file.
    
    Parameters
    ----------
    filepath : str
        Path to data file.
    batch_size : int, default=32
        Number of samples per batch.
        
    Yields
    ------
    batch : np.ndarray of shape (batch_size, n_features)
        A batch of data samples.
        
    Examples
    --------
    >>> for batch in data_generator('data.csv', batch_size=64):
    ...     process_batch(batch)
    """
```

### Context Managers
```python
def managed_resource(param: type) -> ContextManager[ResourceType]:
    """
    Context manager for resource handling.
    
    Parameters
    ----------
    param : type
        Parameter description.
        
    Yields
    ------
    resource : ResourceType
        The managed resource.
        
    Examples
    --------
    >>> with managed_resource(param) as resource:
    ...     resource.do_something()
    """
```

### Decorators
```python
def validate_input(expected_type: type) -> Callable:
    """
    Decorator to validate input types.
    
    Parameters
    ----------
    expected_type : type
        Expected type for the first argument.
        
    Returns
    -------
    decorator : callable
        Decorated function with input validation.
        
    Examples
    --------
    >>> @validate_input(np.ndarray)
    ... def process(data):
    ...     return data.mean()
    """
```

## Common Sections

### Parameters Section
- List parameters in the order they appear in the signature
- Include type information even though it's in type hints
- Always document default values
- Use consistent formatting for optional parameters

### Returns Section
- Name the return value if it improves clarity
- Describe shape for arrays: `np.ndarray of shape (n, m)`
- For multiple returns, document each separately

### Examples Section
- Start with the simplest use case
- Show expected output using `>>>`
- Include more complex examples if helpful
- Test examples to ensure they work

### Notes Section
- Implementation details
- Performance considerations
- Limitations or known issues
- Algorithm explanations

### References Section
- Use standard citation format
- Include DOI or URL when available
- Reference specific equations or sections

## Module-Specific Guidelines

### Scientific Modules (dsp, stats)
- Include mathematical formulas in LaTeX format
- Reference papers for algorithms
- Explain assumptions and limitations

```python
def correlation(x: np.ndarray, y: np.ndarray) -> float:
    """
    Compute Pearson correlation coefficient.
    
    The correlation coefficient is defined as:
    
    .. math::
        r = \\frac{\\sum{(x_i - \\bar{x})(y_i - \\bar{y})}}
                 {\\sqrt{\\sum{(x_i - \\bar{x})^2}\\sum{(y_i - \\bar{y})^2}}}
    
    Parameters
    ----------
    x, y : np.ndarray of shape (n_samples,)
        Input arrays. Must have the same length.
        
    Returns
    -------
    r : float
        Correlation coefficient between -1 and 1.
    """
```

### I/O Modules
- Document supported formats
- Explain file structure expectations
- Include file format examples

```python
def save_data(data: Any, filepath: str, format: str = "auto") -> None:
    """
    Save data to file.
    
    Parameters
    ----------
    data : array-like, dict, or DataFrame
        Data to save. Type depends on format:
        - 'npy': NumPy array
        - 'json': dict or JSON-serializable object
        - 'csv': DataFrame or 2D array
    filepath : str
        Output file path.
    format : {'auto', 'npy', 'json', 'csv'}, default='auto'
        File format. If 'auto', inferred from extension.
    """
```

## Docstring Linting

### Tools
- Use `pydocstyle` for automated checking
- Configure in `pyproject.toml`:

```toml
[tool.pydocstyle]
convention = "numpy"
add-ignore = ["D105", "D107"]  # Ignore magic method docstrings
```

### Pre-commit Hook
```yaml
- repo: https://github.com/pycqa/pydocstyle
  rev: 6.1.1
  hooks:
    - id: pydocstyle
      args: [--convention=numpy]
```

## Migration Strategy

1. **New code**: Must follow these templates
2. **Modified functions**: Update docstrings when touching code
3. **Public APIs**: Prioritize for documentation updates
4. **Private functions**: Document opportunistically

## Quick Reference

### Essential Elements
- ✓ One-line summary
- ✓ Parameters with types
- ✓ Returns with types
- ✓ Basic example

### Additional Elements (when applicable)
- ○ Extended description
- ○ Raises section
- ○ See Also section
- ○ Notes section
- ○ References section
- ○ Multiple examples

## Examples of Good Docstrings

```python
def bandpass_filter(
    data: np.ndarray,
    low_freq: float,
    high_freq: float, 
    sample_rate: float,
    order: int = 4
) -> np.ndarray:
    """
    Apply zero-phase Butterworth bandpass filter to signal.
    
    Parameters
    ----------
    data : np.ndarray of shape (n_samples,) or (n_samples, n_channels)
        Input signal data.
    low_freq : float
        Lower cutoff frequency in Hz. Must be > 0.
    high_freq : float
        Upper cutoff frequency in Hz. Must be < sample_rate/2.
    sample_rate : float
        Sampling frequency in Hz.
    order : int, default=4
        Filter order.
        
    Returns
    -------
    filtered_data : np.ndarray
        Filtered signal, same shape as input.
        
    Examples
    --------
    >>> signal = np.random.randn(1000)
    >>> filtered = bandpass_filter(signal, 1.0, 50.0, 250.0)
    """
```

This docstring template will ensure consistent, high-quality documentation throughout the SciTeX codebase.