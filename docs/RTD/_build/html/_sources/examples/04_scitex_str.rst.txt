04 SciTeX Str
=============

.. note::
   This page is generated from the Jupyter notebook `04_scitex_str.ipynb <https://github.com/scitex/scitex/blob/main/examples/04_scitex_str.ipynb>`_
   
   To run this notebook interactively:
   
   .. code-block:: bash
   
      cd examples/
      jupyter notebook 04_scitex_str.ipynb


This comprehensive notebook demonstrates the SciTeX str module
capabilities, covering string processing, formatting, and text
manipulation utilities.

Features Covered
----------------

Text Processing
~~~~~~~~~~~~~~~

-  String cleaning and path sanitization
-  Text search and replacement
-  String parsing and extraction
-  Space normalization

Formatting and Display
~~~~~~~~~~~~~~~~~~~~~~

-  Colored text output
-  Debug printing utilities
-  Block text formatting
-  Readable byte formatting

Scientific Text
~~~~~~~~~~~~~~~

-  LaTeX formatting and fallbacks
-  Scientific notation
-  Mathematical text formatting
-  Plot text optimization

Security and Privacy
~~~~~~~~~~~~~~~~~~~~

-  API key masking
-  ANSI escape code removal
-  Safe text handling

.. code:: ipython3

    import sys
    sys.path.insert(0, '../src')
    import scitex
    import numpy as np
    import pandas as pd
    from pathlib import Path
    import matplotlib.pyplot as plt
    import re
    import os
    
    # Set up example data directory
    data_dir = Path("./str_examples")
    data_dir.mkdir(exist_ok=True)
    
    print("SciTeX String Processing Tutorial - Ready to begin!")
    print(f"Available str functions: {len(scitex.str.__all__)}")
    print(f"First 10 functions: {scitex.str.__all__[:10]}")

Part 1: Basic String Processing
-------------------------------

1.1 String Cleaning and Sanitization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Path cleaning examples
    problematic_paths = [
        "/home/user/data with spaces/file.txt",
        "C:\\Users\\Name\\Documents\\file.txt",
        "~/data/file with special chars!@#.txt",
        "./data//double//slashes///file.txt",
        "data/./current/./directory/file.txt"
    ]
    
    print("Path Cleaning Examples:")
    print("=" * 30)
    
    for path in problematic_paths:
        try:
            cleaned = scitex.str.clean_path(path)
            print(f"Original: {path}")
            print(f"Cleaned:  {cleaned}")
            print()
        except Exception as e:
            print(f"Error cleaning '{path}': {e}")
            print()
    
    # String capitalization
    test_strings = [
        "Hello World",
        "MACHINE LEARNING",
        "DataScience",
        "python_programming",
        "AI-Research"
    ]
    
    print("String Decapitalization:")
    print("=" * 25)
    
    for text in test_strings:
        decapitalized = scitex.str.decapitalize(text)
        print(f"'{text}' -> '{decapitalized}'")

1.2 Space Normalization and Text Cleanup
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Space normalization
    messy_texts = [
        "This    has     multiple   spaces",
        "\t\nTabs and newlines\t\n everywhere\t\n",
        "   Leading and trailing spaces   ",
        "Mixed\t\n\r\n   whitespace   characters",
        "Normal text with single spaces"
    ]
    
    print("Space Normalization:")
    print("=" * 25)
    
    for text in messy_texts:
        normalized = scitex.str.squeeze_spaces(text)
        print(f"Original: '{text}'")
        print(f"Squeezed: '{normalized}'")
        print()
    
    # ANSI escape code removal
    colored_texts = [
        "\033[31mRed text\033[0m",
        "\033[1;32mBold green text\033[0m",
        "\033[4;34mUnderlined blue text\033[0m",
        "Normal text without ANSI codes",
        "\033[91mBright red\033[0m mixed with \033[92mgreen\033[0m"
    ]
    
    print("ANSI Code Removal:")
    print("=" * 20)
    
    for text in colored_texts:
        clean_text = scitex.str.remove_ansi(text)
        print(f"With ANSI: '{text}'")
        print(f"Cleaned:   '{clean_text}'")
        print()

Part 2: Text Search and Manipulation
------------------------------------

2.1 Search and Grep Functionality
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Create sample text for searching
    sample_text = """
    This is a sample text for demonstrating search functionality.
    The text contains multiple lines and various patterns.
    We have numbers like 123, 456, and 789.
    Email addresses: john@example.com, jane.doe@university.edu
    Phone numbers: (555) 123-4567, 555-987-6543
    URLs: https://www.example.com, http://test.org
    Some special characters: !@#$%^&*()
    And finally, this text ends here.
    """
    
    # Write to file for grep demonstration
    test_file = data_dir / "sample_text.txt"
    with open(test_file, 'w') as f:
        f.write(sample_text)
    
    print("Text Search and Grep:")
    print("=" * 25)
    
    # Search for patterns in text
    search_patterns = [
        "sample",
        "[0-9]+",  # Numbers
        "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",  # Email
        "https?://[^\s]+",  # URLs
        "\([0-9]{3}\) [0-9]{3}-[0-9]{4}",  # Phone numbers
    ]
    
    for pattern in search_patterns:
        print(f"\nSearching for pattern: '{pattern}'")
        try:
            results = scitex.str.search(sample_text, pattern)
            if results:
                print(f"Found {len(results)} matches: {results}")
            else:
                print("No matches found")
        except Exception as e:
            print(f"Search error: {e}")
    
    # Grep in file
    print(f"\nGrep in file '{test_file}':")
    try:
        grep_results = scitex.str.grep(str(test_file), "numbers")
        if grep_results:
            print(f"Grep results: {grep_results}")
        else:
            print("No grep results")
    except Exception as e:
        print(f"Grep error: {e}")

2.2 Text Replacement and Parsing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Text replacement examples
    replacement_examples = [
        ("Hello World", "World", "Python"),
        ("The quick brown fox", "brown", "red"),
        ("Machine Learning AI", "AI", "Artificial Intelligence"),
        ("Data Science 2024", "2024", "2025"),
        ("test@example.com", "@example.com", "@newdomain.org")
    ]
    
    print("Text Replacement:")
    print("=" * 20)
    
    for original, old, new in replacement_examples:
        try:
            replaced = scitex.str.replace(original, old, new)
            print(f"Original: '{original}'")
            print(f"Replace '{old}' with '{new}': '{replaced}'")
            print()
        except Exception as e:
            print(f"Replacement error: {e}")
            print()
    
    # Text parsing
    parse_examples = [
        "name=John age=30 city=NYC",
        "temperature=25.5 humidity=60% pressure=1013.25",
        "model=LinearRegression accuracy=0.95 loss=0.05",
        "date=2024-01-01 time=12:30:00 timezone=UTC"
    ]
    
    print("Text Parsing:")
    print("=" * 15)
    
    for text in parse_examples:
        try:
            parsed = scitex.str.parse(text)
            print(f"Original: '{text}'")
            print(f"Parsed: {parsed}")
            print()
        except Exception as e:
            print(f"Parse error for '{text}': {e}")
            print()

Part 3: Colored Text and Debug Output
-------------------------------------

3.1 Colored Text Output
~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Colored text examples
    colors = ['red', 'green', 'blue', 'yellow', 'magenta', 'cyan', 'white']
    text_styles = ['normal', 'bold', 'underline']
    
    print("Colored Text Output:")
    print("=" * 25)
    
    # Basic colors
    for color in colors:
        try:
            colored = scitex.str.color_text(f"This is {color} text", color)
            print(colored)
        except Exception as e:
            print(f"Color error for {color}: {e}")
    
    # Using shorthand ct function
    print("\nUsing ct() shorthand:")
    try:
        print(scitex.str.ct("Success!", "green"))
        print(scitex.str.ct("Warning!", "yellow"))
        print(scitex.str.ct("Error!", "red"))
        print(scitex.str.ct("Info", "blue"))
    except Exception as e:
        print(f"ct() error: {e}")
    
    # Demonstration of different message types
    messages = [
        ("Operation completed successfully", "green"),
        ("Warning: Low disk space", "yellow"),
        ("Error: File not found", "red"),
        ("Info: Processing data", "blue"),
        ("Debug: Variable x = 42", "magenta")
    ]
    
    print("\nMessage Types:")
    for message, color in messages:
        try:
            colored_msg = scitex.str.color_text(message, color)
            print(colored_msg)
        except Exception as e:
            print(f"Message coloring error: {e}")

3.2 Debug Printing and Block Formatting
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Debug printing examples
    debug_data = {
        'variables': {'x': 42, 'y': 3.14, 'name': 'test'},
        'array': np.array([1, 2, 3, 4, 5]),
        'dataframe': pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]}),
        'list': [1, 2, 3, 4, 5],
        'nested': {'level1': {'level2': {'value': 100}}}
    }
    
    print("Debug Printing:")
    print("=" * 18)
    
    for name, data in debug_data.items():
        try:
            print(f"\nDebugging {name}:")
            scitex.str.print_debug(data, name)
        except Exception as e:
            print(f"Debug print error for {name}: {e}")
    
    # Block text formatting
    block_texts = [
        "This is a simple message",
        "This is a longer message that demonstrates block formatting capabilities",
        "Multi-line\nblock text\nexample",
        "Important: This is a critical message that needs attention!"
    ]
    
    print("\nBlock Text Formatting:")
    print("=" * 25)
    
    for text in block_texts:
        try:
            print(f"\nOriginal: '{text}'")
            scitex.str.printc(text)  # Print colored/formatted block
        except Exception as e:
            print(f"Block formatting error: {e}")

Part 4: Scientific Text and LaTeX Formatting
--------------------------------------------

4.1 LaTeX Style Formatting
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # LaTeX style formatting examples
    scientific_texts = [
        "alpha",
        "beta",
        "gamma",
        "theta",
        "lambda",
        "mu",
        "sigma",
        "phi",
        "x_hat",
        "y_bar",
        "z_prime"
    ]
    
    print("LaTeX Style Formatting:")
    print("=" * 25)
    
    for text in scientific_texts:
        try:
            latex_formatted = scitex.str.to_latex_style(text)
            print(f"'{text}' -> '{latex_formatted}'")
        except Exception as e:
            print(f"LaTeX formatting error for '{text}': {e}")
    
    # Safe LaTeX formatting with fallback
    print("\nSafe LaTeX Formatting:")
    print("=" * 25)
    
    for text in scientific_texts:
        try:
            safe_latex = scitex.str.safe_to_latex_style(text)
            print(f"'{text}' -> '{safe_latex}'")
        except Exception as e:
            print(f"Safe LaTeX error for '{text}': {e}")
    
    # Hat notation in LaTeX
    hat_examples = ['x', 'y', 'z', 'theta', 'phi', 'mu']
    print("\nHat Notation:")
    print("=" * 15)
    
    for var in hat_examples:
        try:
            hat_formatted = scitex.str.add_hat_in_latex_style(var)
            print(f"'{var}' -> '{hat_formatted}'")
        except Exception as e:
            print(f"Hat formatting error for '{var}': {e}")

4.2 Scientific Text and Plot Formatting
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Scientific text formatting for plots
    plot_labels = [
        ("Temperature (C)", "°C"),
        ("Pressure (Pa)", "Pa"),
        ("Voltage (V)", "V"),
        ("Current (A)", "A"),
        ("Frequency (Hz)", "Hz"),
        ("Energy (J)", "J"),
        ("Power (W)", "W")
    ]
    
    print("Scientific Text Formatting:")
    print("=" * 30)
    
    for label, unit in plot_labels:
        try:
            formatted = scitex.str.scientific_text(label)
            print(f"'{label}' -> '{formatted}'")
        except Exception as e:
            print(f"Scientific text error for '{label}': {e}")
    
    # Plot text formatting
    print("\nPlot Text Formatting:")
    print("=" * 25)
    
    plot_texts = [
        "x-axis label",
        "y-axis label",
        "Main Title",
        "Subplot Title",
        "Legend Entry"
    ]
    
    for text in plot_texts:
        try:
            formatted = scitex.str.format_plot_text(text)
            print(f"'{text}' -> '{formatted}'")
        except Exception as e:
            print(f"Plot text formatting error for '{text}': {e}")
    
    # Axis labels and titles
    print("\nAxis Labels and Titles:")
    print("=" * 25)
    
    axis_examples = [
        ("time", "seconds"),
        ("amplitude", "volts"),
        ("frequency", "hertz"),
        ("temperature", "celsius"),
        ("pressure", "pascals")
    ]
    
    for var, unit in axis_examples:
        try:
            axis_label = scitex.str.axis_label(var, unit)
            title_formatted = scitex.str.title(f"{var} vs time")
            print(f"Variable: {var}, Unit: {unit}")
            print(f"  Axis label: '{axis_label}'")
            print(f"  Title: '{title_formatted}'")
            print()
        except Exception as e:
            print(f"Axis formatting error for {var}: {e}")

4.3 Digit Factoring and Smart Formatting
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Digit factoring for better readability
    large_numbers = [
        [1000, 2000, 3000, 4000, 5000],
        [1500000, 2500000, 3500000, 4500000],
        [0.001, 0.002, 0.003, 0.004, 0.005],
        [12345, 23456, 34567, 45678, 56789],
        [1.2e6, 2.3e6, 3.4e6, 4.5e6, 5.6e6]
    ]
    
    print("Digit Factoring:")
    print("=" * 20)
    
    for numbers in large_numbers:
        try:
            factored = scitex.str.factor_out_digits(numbers)
            print(f"Original: {numbers}")
            print(f"Factored: {factored}")
            print()
        except Exception as e:
            print(f"Digit factoring error: {e}")
            print()
    
    # Smart tick formatting
    tick_examples = [
        np.array([0, 1000, 2000, 3000, 4000, 5000]),
        np.array([0.001, 0.002, 0.003, 0.004, 0.005]),
        np.array([1e6, 2e6, 3e6, 4e6, 5e6]),
        np.array([0.0001, 0.0002, 0.0003, 0.0004, 0.0005])
    ]
    
    print("Smart Tick Formatting:")
    print("=" * 25)
    
    for ticks in tick_examples:
        try:
            formatted = scitex.str.smart_tick_formatter(ticks)
            print(f"Original ticks: {ticks}")
            print(f"Formatted: {formatted}")
            print()
        except Exception as e:
            print(f"Smart tick formatting error: {e}")
            print()

Part 5: Security and Privacy Features
-------------------------------------

5.1 API Key Masking
~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # API key masking examples
    sensitive_data = [
        "API_KEY=sk-1234567890abcdef1234567890abcdef",
        "SECRET_TOKEN=ghp_1234567890abcdef1234567890abcdef123456",
        "DATABASE_URL=postgresql://user:password@localhost:5432/db",
        "OPENAI_API_KEY=sk-proj-abcdef1234567890abcdef1234567890abcdef",
        "AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE",
        "This is normal text without sensitive data"
    ]
    
    print("API Key Masking:")
    print("=" * 20)
    
    for data in sensitive_data:
        try:
            masked = scitex.str.mask_api(data)
            print(f"Original: '{data}'")
            print(f"Masked:   '{masked}'")
            print()
        except Exception as e:
            print(f"Masking error for '{data}': {e}")
            print()
    
    # Demonstration of different API key formats
    api_formats = [
        "sk-1234567890abcdef",  # OpenAI style
        "ghp_1234567890abcdef",  # GitHub style
        "xoxb-1234567890",  # Slack style
        "ya29.1234567890",  # Google style
        "EAACEdEose0cBA1234567890"  # Facebook style
    ]
    
    print("Different API Key Formats:")
    print("=" * 30)
    
    for api_key in api_formats:
        try:
            masked = scitex.str.mask_api(api_key)
            print(f"API Key: '{api_key}' -> '{masked}'")
        except Exception as e:
            print(f"Error masking '{api_key}': {e}")

Part 6: Utility Functions
-------------------------

6.1 Readable Bytes and File Sizes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Readable byte formatting
    byte_sizes = [
        1024,  # 1 KB
        1024**2,  # 1 MB
        1024**3,  # 1 GB
        1024**4,  # 1 TB
        1500000,  # 1.5 MB
        2500000000,  # 2.5 GB
        512,  # 512 bytes
        1023,  # Just under 1 KB
        1048576 + 524288  # 1.5 MB
    ]
    
    print("Readable Byte Formatting:")
    print("=" * 30)
    
    for size in byte_sizes:
        try:
            readable = scitex.str.readable_bytes(size)
            print(f"{size:>12} bytes -> {readable}")
        except Exception as e:
            print(f"Error formatting {size}: {e}")
    
    # File size examples with actual files
    print("\nFile Size Examples:")
    print("=" * 20)
    
    # Create test files of different sizes
    test_files = [
        ("small.txt", "Small file content"),
        ("medium.txt", "Medium file content\n" * 1000),
        ("large.txt", "Large file content with lots of text\n" * 10000)
    ]
    
    for filename, content in test_files:
        filepath = data_dir / filename
        with open(filepath, 'w') as f:
            f.write(content)
        
        file_size = filepath.stat().st_size
        readable_size = scitex.str.readable_bytes(file_size)
        print(f"{filename}: {file_size} bytes -> {readable_size}")

Part 7: LaTeX Fallback System
-----------------------------

7.1 LaTeX Capability Detection and Fallbacks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # LaTeX capability detection
    print("LaTeX Capability Detection:")
    print("=" * 30)
    
    try:
        latex_available = scitex.str.check_latex_capability()
        print(f"LaTeX available: {latex_available}")
        
        latex_status = scitex.str.get_latex_status()
        print(f"LaTeX status: {latex_status}")
        
        fallback_mode = scitex.str.get_fallback_mode()
        print(f"Fallback mode: {fallback_mode}")
        
    except Exception as e:
        print(f"LaTeX detection error: {e}")
    
    # LaTeX fallback examples
    latex_expressions = [
        r"$\alpha + \beta = \gamma$",
        r"$\frac{x^2}{y^2} = z$",
        r"$\sum_{i=1}^{n} x_i$",
        r"$\int_{0}^{\infty} e^{-x} dx$",
        r"$\sqrt{\frac{a}{b}}$"
    ]
    
    print("\nLaTeX Fallback Examples:")
    print("=" * 28)
    
    for expr in latex_expressions:
        try:
            # Try safe rendering
            safe_rendered = scitex.str.safe_latex_render(expr)
            print(f"LaTeX: '{expr}'")
            print(f"Safe:  '{safe_rendered}'")
            
            # Try conversion to unicode
            unicode_version = scitex.str.latex_to_unicode(expr)
            print(f"Unicode: '{unicode_version}'")
            
            # Try conversion to mathtext
            mathtext_version = scitex.str.latex_to_mathtext(expr)
            print(f"MathText: '{mathtext_version}'")
            print()
            
        except Exception as e:
            print(f"LaTeX processing error for '{expr}': {e}")
            print()
    
    # Fallback mode management
    print("Fallback Mode Management:")
    print("=" * 28)
    
    try:
        # Enable fallback
        scitex.str.enable_latex_fallback()
        print("LaTeX fallback enabled")
        
        # Set fallback mode
        scitex.str.set_fallback_mode('unicode')
        print("Fallback mode set to 'unicode'")
        
        # Test with fallback
        test_expr = r"$\alpha + \beta$"
        result = scitex.str.safe_latex_render(test_expr)
        print(f"Test expression: '{test_expr}' -> '{result}'")
        
    except Exception as e:
        print(f"Fallback management error: {e}")

Part 8: Practical Applications
------------------------------

8.1 Scientific Data Processing Pipeline
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Create a comprehensive text processing pipeline
    class TextProcessor:
        def __init__(self):
            self.processing_log = []
        
        def log_step(self, step, input_text, output_text):
            self.processing_log.append({
                'step': step,
                'input': input_text,
                'output': output_text,
                'input_length': len(input_text),
                'output_length': len(output_text)
            })
        
        def process_scientific_text(self, text):
            """Process scientific text through multiple cleaning steps."""
            original_text = text
            
            # Step 1: Normalize spaces
            text = scitex.str.squeeze_spaces(text)
            self.log_step("Space normalization", original_text, text)
            
            # Step 2: Remove ANSI codes
            text = scitex.str.remove_ansi(text)
            self.log_step("ANSI removal", self.processing_log[-1]['output'], text)
            
            # Step 3: Format for LaTeX
            text = scitex.str.safe_to_latex_style(text)
            self.log_step("LaTeX formatting", self.processing_log[-1]['output'], text)
            
            # Step 4: Mask sensitive data
            text = scitex.str.mask_api(text)
            self.log_step("API masking", self.processing_log[-1]['output'], text)
            
            return text
        
        def print_processing_log(self):
            """Print the processing log with colored output."""
            print(scitex.str.ct("=" * 50, "blue"))
            print(scitex.str.ct("TEXT PROCESSING LOG", "blue"))
            print(scitex.str.ct("=" * 50, "blue"))
            
            for i, entry in enumerate(self.processing_log, 1):
                print(f"\n{scitex.str.ct(f'Step {i}: {entry["step"]}', 'green')}")
                print(f"Input  ({entry['input_length']} chars): '{entry['input'][:50]}{'...' if len(entry['input']) > 50 else ''}'")
                print(f"Output ({entry['output_length']} chars): '{entry['output'][:50]}{'...' if len(entry['output']) > 50 else ''}'")
    
    # Test the pipeline
    processor = TextProcessor()
    
    test_scientific_texts = [
        "\033[31mTemperature    measurements\033[0m   showed   alpha = 0.05   significance with API_KEY=sk-1234567890abcdef",
        "\t\nPressure   data\t\ncontains    beta   coefficients   SECRET_TOKEN=ghp_abcdef1234567890\n",
        "The   gamma   distribution   parameters   were   DATABASE_URL=postgresql://user:pass@host:5432/db"
    ]
    
    print("Scientific Text Processing Pipeline:")
    print("=" * 40)
    
    for i, text in enumerate(test_scientific_texts, 1):
        print(f"\nProcessing text {i}:")
        processed = processor.process_scientific_text(text)
        print(f"Final result: '{processed}'")
        print()
    
    # Show processing log
    processor.print_processing_log()

8.2 Report Generation with Formatted Text
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Generate a formatted scientific report
    def generate_scientific_report(experiment_data):
        """Generate a formatted scientific report."""
        
        # Report header
        report = []
        report.append(scitex.str.ct("=" * 60, "blue"))
        report.append(scitex.str.ct("SCIENTIFIC EXPERIMENT REPORT", "blue"))
        report.append(scitex.str.ct("=" * 60, "blue"))
        report.append("")
        
        # Experiment info
        report.append(scitex.str.ct("EXPERIMENT INFORMATION", "green"))
        report.append("-" * 30)
        report.append(f"Name: {experiment_data['name']}")
        report.append(f"Date: {experiment_data['date']}")
        report.append(f"Researcher: {experiment_data['researcher']}")
        report.append("")
        
        # Parameters
        report.append(scitex.str.ct("PARAMETERS", "green"))
        report.append("-" * 15)
        for param, value in experiment_data['parameters'].items():
            formatted_param = scitex.str.to_latex_style(param)
            report.append(f"{formatted_param}: {value}")
        report.append("")
        
        # Results
        report.append(scitex.str.ct("RESULTS", "green"))
        report.append("-" * 10)
        for metric, value in experiment_data['results'].items():
            if isinstance(value, float):
                formatted_value = f"{value:.4f}"
            else:
                formatted_value = str(value)
            report.append(f"{metric}: {formatted_value}")
        report.append("")
        
        # File sizes
        if 'file_sizes' in experiment_data:
            report.append(scitex.str.ct("FILE SIZES", "green"))
            report.append("-" * 12)
            for filename, size in experiment_data['file_sizes'].items():
                readable_size = scitex.str.readable_bytes(size)
                report.append(f"{filename}: {readable_size}")
            report.append("")
        
        # Status
        status = experiment_data.get('status', 'unknown')
        if status == 'success':
            status_line = scitex.str.ct(f"Status: {status.upper()}", "green")
        elif status == 'warning':
            status_line = scitex.str.ct(f"Status: {status.upper()}", "yellow")
        else:
            status_line = scitex.str.ct(f"Status: {status.upper()}", "red")
        
        report.append(status_line)
        report.append("")
        report.append(scitex.str.ct("=" * 60, "blue"))
        
        return "\n".join(report)
    
    # Sample experiment data
    experiment_data = {
        'name': 'Neural Network Performance Analysis',
        'date': '2024-01-15',
        'researcher': 'Dr. Jane Smith',
        'parameters': {
            'alpha': 0.001,
            'beta': 0.9,
            'gamma': 0.999,
            'lambda': 0.01,
            'epochs': 100,
            'batch_size': 32
        },
        'results': {
            'accuracy': 0.9542,
            'precision': 0.9123,
            'recall': 0.8876,
            'f1_score': 0.8998,
            'training_time': '2h 45m'
        },
        'file_sizes': {
            'model.pkl': 15728640,  # 15 MB
            'training_data.csv': 104857600,  # 100 MB
            'results.json': 2048,  # 2 KB
            'logs.txt': 524288  # 512 KB
        },
        'status': 'success'
    }
    
    # Generate and print the report
    report = generate_scientific_report(experiment_data)
    print(report)
    
    # Save report to file
    report_file = data_dir / "experiment_report.txt"
    with open(report_file, 'w') as f:
        # Remove color codes for file output
        clean_report = scitex.str.remove_ansi(report)
        f.write(clean_report)
    
    print(f"\nReport saved to: {report_file}")
    print(f"Report file size: {scitex.str.readable_bytes(report_file.stat().st_size)}")

Summary and Best Practices
--------------------------

This tutorial demonstrated the comprehensive string processing
capabilities of the SciTeX str module:

Key Features Covered:
~~~~~~~~~~~~~~~~~~~~~

1.  **Text Cleaning**: ``clean_path()``, ``squeeze_spaces()``,
    ``remove_ansi()``
2.  **Search and Replace**: ``search()``, ``grep()``, ``replace()``
3.  **Colored Output**: ``color_text()``, ``ct()`` for enhanced
    readability
4.  **Debug Tools**: ``print_debug()``, ``printc()`` for development
5.  **LaTeX Support**: ``to_latex_style()``, ``safe_latex_render()``
    with fallbacks
6.  **Scientific Formatting**: ``scientific_text()``,
    ``format_plot_text()``
7.  **Security**: ``mask_api()`` for sensitive data protection
8.  **Utility Functions**: ``readable_bytes()``, ``factor_out_digits()``
9.  **Smart Formatting**: ``smart_tick_formatter()``, ``axis_label()``
10. **LaTeX Fallback System**: Robust handling of LaTeX unavailability

Best Practices:
~~~~~~~~~~~~~~~

-  Use **text cleaning** functions before processing scientific data
-  Apply **API masking** to protect sensitive information
-  Use **colored output** for better user experience
-  Implement **LaTeX fallbacks** for robust scientific text rendering
-  Use **smart formatting** for better plot readability
-  Apply **debug tools** during development
-  Use **readable byte formatting** for file size reporting
-  Implement **comprehensive text processing pipelines** for consistent
   results

.. code:: ipython3

    # Cleanup
    import shutil
    
    cleanup = input("Clean up example files? (y/n): ").lower().startswith('y')
    if cleanup:
        shutil.rmtree(data_dir)
        print("✓ Example files cleaned up")
    else:
        print(f"Example files preserved in: {data_dir}")
        print(f"Files created: {len(list(data_dir.rglob('*')))}")
        total_size = sum(f.stat().st_size for f in data_dir.rglob('*') if f.is_file())
        print(f"Total size: {scitex.str.readable_bytes(total_size)}")
