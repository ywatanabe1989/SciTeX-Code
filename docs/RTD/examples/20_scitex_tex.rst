20 SciTeX Tex
=============

.. note::
   This page is generated from the Jupyter notebook `20_scitex_tex.ipynb <https://github.com/scitex/scitex/blob/main/examples/20_scitex_tex.ipynb>`_
   
   To run this notebook interactively:
   
   .. code-block:: bash
   
      cd examples/
      jupyter notebook 20_scitex_tex.ipynb


This notebook demonstrates the complete functionality of the
``scitex.tex`` module, which provides LaTeX/TeX utilities for scientific
document preparation and mathematical notation.

Module Overview
---------------

The ``scitex.tex`` module includes: - LaTeX preview functionality with
fallback mechanisms - Vector notation utilities with robust error
handling - Mathematical formatting tools for scientific publications

Import Setup
------------

.. code:: ipython3

    import sys
    sys.path.insert(0, '../src')
    
    import matplotlib.pyplot as plt
    import numpy as np
    
    # Import scitex tex module
    import scitex.tex as stex
    
    # Set random seed for reproducibility
    np.random.seed(42)
    
    print("Available functions in scitex.tex:")
    tex_attrs = [attr for attr in dir(stex) if not attr.startswith('_')]
    for i, attr in enumerate(tex_attrs):
        print(f"{i+1:2d}. {attr}")

1. LaTeX Preview Functionality
------------------------------

Basic LaTeX Preview
~~~~~~~~~~~~~~~~~~~

The ``preview`` function generates visual previews of LaTeX mathematical
expressions.

.. code:: ipython3

    # Example 1: Basic LaTeX preview
    print("Basic LaTeX Preview:")
    print("=" * 20)
    
    # Define some mathematical expressions
    basic_expressions = [
        "x^2 + y^2 = z^2",
        "\\frac{a}{b} = \\frac{c}{d}",
        "\\sqrt{x + y}",
        "\\alpha + \\beta = \\gamma"
    ]
    
    print(f"Previewing {len(basic_expressions)} basic expressions:")
    for i, expr in enumerate(basic_expressions):
        print(f"{i+1}. {expr}")
    
    try:
        # Generate preview
        fig = stex.preview(basic_expressions)
        fig.suptitle('Basic LaTeX Expressions Preview', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.show()
        print("✓ Basic preview generated successfully")
        
    except Exception as e:
        print(f"Error generating basic preview: {e}")
        print("This might require LaTeX installation or fallback mechanisms.")

Advanced Mathematical Expressions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let’s preview more complex mathematical expressions commonly used in
scientific papers.

.. code:: ipython3

    # Example 2: Advanced mathematical expressions
    print("Advanced Mathematical Expressions:")
    print("=" * 35)
    
    # Complex mathematical expressions
    advanced_expressions = [
        "\\sum_{i=1}^{n} x_i = \\mu",
        "\\int_{-\\infty}^{\\infty} e^{-x^2} dx = \\sqrt{\\pi}",
        "\\frac{\\partial^2 f}{\\partial x^2} + \\frac{\\partial^2 f}{\\partial y^2} = 0",
        "\\lim_{n \\to \\infty} \\frac{1}{n} \\sum_{i=1}^{n} X_i = E[X]",
        "\\hat{\\theta} = \\arg\\max_{\\theta} \\mathcal{L}(\\theta)"
    ]
    
    print(f"Previewing {len(advanced_expressions)} advanced expressions:")
    for i, expr in enumerate(advanced_expressions):
        print(f"{i+1}. {expr}")
    
    try:
        # Generate preview with advanced expressions
        fig = stex.preview(advanced_expressions)
        fig.suptitle('Advanced Mathematical Expressions', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.show()
        print("✓ Advanced preview generated successfully")
        
    except Exception as e:
        print(f"Error generating advanced preview: {e}")
        print("Fallback mechanisms may be in use.")

Scientific Formulas and Equations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let’s preview some common scientific formulas and equations.

.. code:: ipython3

    # Example 3: Scientific formulas and equations
    print("Scientific Formulas and Equations:")
    print("=" * 35)
    
    # Common scientific formulas
    scientific_formulas = [
        "E = mc^2",  # Einstein's mass-energy equivalence
        "F = ma",    # Newton's second law
        "\\nabla \\cdot \\vec{E} = \\frac{\\rho}{\\epsilon_0}",  # Gauss's law
        "H(X) = -\\sum_{i} p_i \\log_2 p_i",  # Shannon entropy
        "\\sigma^2 = \\frac{1}{n-1} \\sum_{i=1}^{n} (x_i - \\bar{x})^2"  # Sample variance
    ]
    
    print(f"Previewing {len(scientific_formulas)} scientific formulas:")
    for i, formula in enumerate(scientific_formulas):
        print(f"{i+1}. {formula}")
    
    try:
        # Generate preview with scientific formulas
        fig = stex.preview(scientific_formulas)
        fig.suptitle('Common Scientific Formulas', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.show()
        print("✓ Scientific formulas preview generated successfully")
        
    except Exception as e:
        print(f"Error generating scientific formulas preview: {e}")
        print("This might require LaTeX installation or use fallback rendering.")

Single Expression Preview
~~~~~~~~~~~~~~~~~~~~~~~~~

The preview function also works with single expressions.

.. code:: ipython3

    # Example 4: Single expression preview
    print("Single Expression Preview:")
    print("=" * 25)
    
    # Single complex expression
    single_expression = "\\mathbf{A}\\mathbf{x} = \\lambda \\mathbf{x}"
    
    print(f"Previewing single expression: {single_expression}")
    
    try:
        # Generate preview for single expression
        fig = stex.preview(single_expression)  # Can pass string directly
        fig.suptitle('Eigenvalue Equation', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.show()
        print("✓ Single expression preview generated successfully")
        
    except Exception as e:
        print(f"Error generating single expression preview: {e}")

2. Vector Notation Utilities
----------------------------

Basic Vector Notation
~~~~~~~~~~~~~~~~~~~~~

The ``to_vec`` function converts strings to LaTeX vector notation with
fallback support.

.. code:: ipython3

    # Example 5: Basic vector notation
    print("Basic Vector Notation:")
    print("=" * 20)
    
    # Test vector names
    vector_names = ['A', 'B', 'v', 'F', 'AB', 'velocity', 'position']
    
    print("Converting strings to vector notation:")
    print("Original\t→ Vector Notation")
    print("-" * 40)
    
    vector_results = []
    for name in vector_names:
        try:
            vector_notation = stex.to_vec(name)
            vector_results.append((name, vector_notation))
            print(f"{name:10s}\t→ {vector_notation}")
        except Exception as e:
            print(f"{name:10s}\t→ Error: {e}")
    
    print(f"\n✓ Converted {len(vector_results)} vector names successfully")

Vector Notation with Fallback Strategies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let’s explore different fallback strategies for vector notation.

.. code:: ipython3

    # Example 6: Vector notation with different fallback strategies
    print("Vector Notation with Fallback Strategies:")
    print("=" * 40)
    
    # Test vector with different fallback strategies
    test_vector = "velocity"
    fallback_strategies = ["auto", "unicode", "plain"]
    
    print(f"Converting '{test_vector}' with different fallback strategies:")
    print("Strategy\t→ Result")
    print("-" * 30)
    
    for strategy in fallback_strategies:
        try:
            # Test different fallback strategies
            if hasattr(stex, 'safe_to_vec'):
                result = stex.safe_to_vec(test_vector, fallback_strategy=strategy)
            else:
                # Fallback to regular to_vec
                result = stex.to_vec(test_vector)
            print(f"{strategy:10s}\t→ {result}")
        except Exception as e:
            print(f"{strategy:10s}\t→ Error: {e}")
    
    # Test with different vector names
    print("\nTesting different vector names with unicode fallback:")
    test_vectors = ['x', 'F', 'acceleration', 'AB', 'r']
    
    for vec_name in test_vectors:
        try:
            if hasattr(stex, 'safe_to_vec'):
                unicode_result = stex.safe_to_vec(vec_name, fallback_strategy="unicode")
            else:
                unicode_result = stex.to_vec(vec_name)
            print(f"{vec_name:12s} → {unicode_result}")
        except Exception as e:
            print(f"{vec_name:12s} → Error: {e}")

Vector Notation in Mathematical Context
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let’s create mathematical expressions using vector notation.

.. code:: ipython3

    # Example 7: Vector notation in mathematical context
    print("Vector Notation in Mathematical Context:")
    print("=" * 40)
    
    # Create mathematical expressions with vectors
    vector_expressions = []
    
    try:
        # Generate vector notations
        vec_F = stex.to_vec('F')
        vec_a = stex.to_vec('a')
        vec_v = stex.to_vec('v')
        vec_r = stex.to_vec('r')
        
        # Create physics equations with vectors
        physics_equations = [
            f"{vec_F} = m{vec_a}",  # Newton's second law
            f"{vec_v} = \\frac{{d{vec_r}}}{{dt}}",  # Velocity definition
            f"{vec_a} = \\frac{{d{vec_v}}}{{dt}}",  # Acceleration definition
            f"\\vec{{A}} \\cdot \\vec{{B}} = |\\vec{{A}}||\\vec{{B}}|\\cos\\theta",  # Dot product
            f"\\vec{{A}} \\times \\vec{{B}} = |\\vec{{A}}||\\vec{{B}}|\\sin\\theta \\hat{{n}}",  # Cross product
        ]
        
        print("Physics equations with vector notation:")
        for i, eq in enumerate(physics_equations):
            print(f"{i+1}. {eq}")
        
        # Preview the vector equations
        print("\nGenerating preview of vector equations...")
        fig = stex.preview(physics_equations)
        fig.suptitle('Physics Equations with Vector Notation', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.show()
        print("✓ Vector equations preview generated successfully")
        
    except Exception as e:
        print(f"Error creating vector equations: {e}")
        print("This might require LaTeX installation or use fallback rendering.")

3. LaTeX Fallback Mechanisms
----------------------------

Testing Fallback Behavior
~~~~~~~~~~~~~~~~~~~~~~~~~

Let’s test how the module handles LaTeX rendering failures.

.. code:: ipython3

    # Example 8: Testing fallback behavior
    print("Testing LaTeX Fallback Mechanisms:")
    print("=" * 35)
    
    # Test with potentially problematic expressions
    problematic_expressions = [
        "x^2",  # Simple expression (should work)
        "\\nonexistentcommand{x}",  # Invalid LaTeX command
        "\\sum_{i=1}^{n} x_i",  # Complex but valid
        "\\undefinedfunction{a, b}",  # Another invalid command
        "\\alpha + \\beta",  # Greek letters (should work)
    ]
    
    print("Testing expressions with potential rendering issues:")
    print("Expression\t\t\t→ Status")
    print("-" * 50)
    
    successful_expressions = []
    failed_expressions = []
    
    for expr in problematic_expressions:
        try:
            # Test with fallback enabled
            result = stex.preview([expr], enable_fallback=True)
            successful_expressions.append(expr)
            print(f"{expr[:25]:25s}\t→ ✓ Success")
            plt.close(result)  # Close figure to save memory
        except Exception as e:
            failed_expressions.append((expr, str(e)))
            print(f"{expr[:25]:25s}\t→ ✗ Failed: {str(e)[:20]}...")
    
    print(f"\nSummary:")
    print(f"Successful renders: {len(successful_expressions)}")
    print(f"Failed renders: {len(failed_expressions)}")
    
    if successful_expressions:
        print(f"\nSuccessful expressions will use appropriate fallbacks.")
        
    if failed_expressions:
        print(f"\nFailed expressions:")
        for expr, error in failed_expressions:
            print(f"  - {expr}: {error[:50]}...")

Comparing Rendering with and without Fallback
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let’s compare rendering behavior with fallback enabled vs disabled.

.. code:: ipython3

    # Example 9: Comparing rendering with and without fallback
    print("Comparing Rendering: Fallback vs No Fallback:")
    print("=" * 45)
    
    # Test expression
    test_expression = "\\sum_{i=1}^{n} x_i^2"
    
    print(f"Test expression: {test_expression}")
    print("\nTesting with different fallback settings:")
    
    # Test with fallback enabled
    try:
        print("\n1. With fallback enabled:")
        fig_with_fallback = stex.preview([test_expression], enable_fallback=True)
        fig_with_fallback.suptitle('With Fallback Enabled', fontsize=14)
        plt.tight_layout()
        plt.show()
        print("✓ Fallback-enabled rendering successful")
    except Exception as e:
        print(f"✗ Fallback-enabled rendering failed: {e}")
    
    # Test with fallback disabled
    try:
        print("\n2. With fallback disabled:")
        fig_no_fallback = stex.preview([test_expression], enable_fallback=False)
        fig_no_fallback.suptitle('With Fallback Disabled', fontsize=14)
        plt.tight_layout()
        plt.show()
        print("✓ No-fallback rendering successful")
    except Exception as e:
        print(f"✗ No-fallback rendering failed: {e}")
        print("This is expected if LaTeX is not properly installed.")
    
    print("\nNote: Differences in rendering indicate fallback mechanisms in action.")

4. Practical Applications
-------------------------

Scientific Paper Equations
~~~~~~~~~~~~~~~~~~~~~~~~~~

Let’s create a collection of equations commonly found in scientific
papers.

.. code:: ipython3

    # Example 10: Scientific paper equations
    print("Scientific Paper Equations:")
    print("=" * 30)
    
    # Collection of equations from different scientific fields
    paper_equations = {
        "Statistics": [
            "t = \\frac{\\bar{x} - \\mu}{s/\\sqrt{n}}",  # t-test
            "\\chi^2 = \\sum_{i=1}^{k} \\frac{(O_i - E_i)^2}{E_i}",  # Chi-square test
            "r = \\frac{\\sum(x_i - \\bar{x})(y_i - \\bar{y})}{\\sqrt{\\sum(x_i - \\bar{x})^2 \\sum(y_i - \\bar{y})^2}}",  # Correlation
        ],
        "Physics": [
            "\\nabla^2 \\psi + \\frac{2m}{\\hbar^2}(E - V)\\psi = 0",  # Schrödinger equation
            "G_{\\mu\\nu} = \\frac{8\\pi G}{c^4} T_{\\mu\\nu}",  # Einstein field equations
            "\\frac{\\partial \\rho}{\\partial t} + \\nabla \\cdot (\\rho \\vec{v}) = 0",  # Continuity equation
        ],
        "Machine Learning": [
            "J(\\theta) = \\frac{1}{2m} \\sum_{i=1}^{m} (h_\\theta(x^{(i)}) - y^{(i)})^2",  # Cost function
            "\\sigma(z) = \\frac{1}{1 + e^{-z}}",  # Sigmoid function
            "\\text{softmax}(z_i) = \\frac{e^{z_i}}{\\sum_{j=1}^{K} e^{z_j}}",  # Softmax
        ]
    }
    
    # Generate previews for each field
    for field, equations in paper_equations.items():
        print(f"\n{field} Equations:")
        print("-" * (len(field) + 11))
        
        for i, eq in enumerate(equations):
            print(f"{i+1}. {eq}")
        
        try:
            fig = stex.preview(equations)
            fig.suptitle(f'{field} Equations', fontsize=16, fontweight='bold')
            plt.tight_layout()
            plt.show()
            print(f"✓ {field} equations preview generated")
        except Exception as e:
            print(f"✗ Error generating {field} preview: {e}")
    
    print("\n" + "=" * 50)
    print("Scientific paper equations demonstration complete.")

Vector Analysis in 3D Space
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let’s demonstrate vector notation for 3D mathematical analysis.

.. code:: ipython3

    # Example 11: Vector analysis in 3D space
    print("Vector Analysis in 3D Space:")
    print("=" * 30)
    
    # 3D vector operations and analysis
    vector_3d_operations = []
    
    try:
        # Generate vector notations for 3D analysis
        vec_r = stex.to_vec('r')
        vec_v = stex.to_vec('v')
        vec_a = stex.to_vec('a')
        vec_F = stex.to_vec('F')
        vec_E = stex.to_vec('E')
        vec_B = stex.to_vec('B')
        
        # Create 3D vector analysis equations
        vector_3d_equations = [
            f"{vec_r}(t) = x(t)\\hat{{i}} + y(t)\\hat{{j}} + z(t)\\hat{{k}}",  # Position vector
            f"{vec_v} = \\frac{{d{vec_r}}}{{dt}} = \\dot{{x}}\\hat{{i}} + \\dot{{y}}\\hat{{j}} + \\dot{{z}}\\hat{{k}}",  # Velocity
            f"\\nabla f = \\frac{{\\partial f}}{{\\partial x}}\\hat{{i}} + \\frac{{\\partial f}}{{\\partial y}}\\hat{{j}} + \\frac{{\\partial f}}{{\\partial z}}\\hat{{k}}",  # Gradient
            f"\\nabla \\cdot {vec_F} = \\frac{{\\partial F_x}}{{\\partial x}} + \\frac{{\\partial F_y}}{{\\partial y}} + \\frac{{\\partial F_z}}{{\\partial z}}",  # Divergence
            f"\\nabla \\times {vec_E} = -\\frac{{\\partial {vec_B}}}{{\\partial t}}",  # Curl (Faraday's law)
        ]
        
        print("3D Vector Analysis Equations:")
        for i, eq in enumerate(vector_3d_equations):
            print(f"{i+1}. {eq}")
        
        # Generate preview
        print("\nGenerating 3D vector analysis preview...")
        fig = stex.preview(vector_3d_equations)
        fig.suptitle('3D Vector Analysis', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.show()
        print("✓ 3D vector analysis preview generated successfully")
        
    except Exception as e:
        print(f"Error creating 3D vector analysis: {e}")
        print("This might require LaTeX installation or use fallback rendering.")
    
    # Demonstrate vector notation with different naming conventions
    print("\nVector Naming Conventions:")
    vector_names_3d = ['r', 'v', 'a', 'F', 'E', 'B', 'p', 'L', 'omega']
    
    print("Name\t→ Vector Notation")
    print("-" * 25)
    for name in vector_names_3d:
        try:
            notation = stex.to_vec(name)
            print(f"{name:8s}\t→ {notation}")
        except Exception as e:
            print(f"{name:8s}\t→ Error: {e}")

LaTeX for Publication-Ready Figures
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let’s demonstrate how to use the tex module for creating
publication-ready mathematical content.

.. code:: ipython3

    # Example 12: Publication-ready mathematical content
    print("Publication-Ready Mathematical Content:")
    print("=" * 40)
    
    # Create a comprehensive mathematical demonstration
    publication_equations = [
        # Fundamental equations in physics and mathematics
        "\\text{Euler's Identity: } e^{i\\pi} + 1 = 0",
        "\\text{Gaussian Integral: } \\int_{-\\infty}^{\\infty} e^{-x^2} dx = \\sqrt{\\pi}",
        "\\text{Fourier Transform: } \\hat{f}(\\xi) = \\int_{-\\infty}^{\\infty} f(x) e^{-2\\pi i x \\xi} dx",
        "\\text{Bayes' Theorem: } P(A|B) = \\frac{P(B|A)P(A)}{P(B)}",
        "\\text{Schrödinger Equation: } i\\hbar\\frac{\\partial}{\\partial t}\\Psi = \\hat{H}\\Psi"
    ]
    
    print("Fundamental equations for publication:")
    for i, eq in enumerate(publication_equations):
        print(f"{i+1}. {eq}")
    
    try:
        # Create publication-style preview
        fig = stex.preview(publication_equations)
        fig.suptitle('Fundamental Mathematical and Physical Equations', 
                    fontsize=18, fontweight='bold', y=0.98)
        
        # Customize for publication appearance
        fig.patch.set_facecolor('white')
        plt.tight_layout()
        plt.subplots_adjust(top=0.95)
        
        # Show the figure
        plt.show()
        print("✓ Publication-ready equations preview generated")
        
        # Demonstrate saving for publication
        print("\nFor publication, you could save this as:")
        print("  - fig.savefig('equations.png', dpi=300, bbox_inches='tight')")
        print("  - fig.savefig('equations.pdf', bbox_inches='tight')")
        print("  - fig.savefig('equations.svg', bbox_inches='tight')")
        
    except Exception as e:
        print(f"Error creating publication preview: {e}")
        print("This might require LaTeX installation for best results.")
    
    # Demonstrate vector notation in publication context
    print("\nVector notation for physics publications:")
    physics_vectors = ['E', 'B', 'F', 'p', 'L', 'r', 'v', 'a']
    physics_descriptions = [
        'Electric field', 'Magnetic field', 'Force', 'Momentum', 
        'Angular momentum', 'Position', 'Velocity', 'Acceleration'
    ]
    
    print("Vector\tNotation\t\tDescription")
    print("-" * 45)
    for vec, desc in zip(physics_vectors, physics_descriptions):
        try:
            notation = stex.to_vec(vec)
            print(f"{vec}\t{notation:15s}\t{desc}")
        except Exception as e:
            print(f"{vec}\tError: {e}\t{desc}")

Summary
-------

This notebook has demonstrated the comprehensive functionality of the
``scitex.tex`` module:

LaTeX Preview Functionality
~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  **``preview``**: Generate visual previews of LaTeX mathematical
   expressions

   -  Support for single expressions or lists of expressions
   -  Automatic fallback mechanisms for robust rendering
   -  Customizable figure layout and styling
   -  Error handling for invalid LaTeX syntax

Vector Notation Utilities
~~~~~~~~~~~~~~~~~~~~~~~~~

-  **``to_vec``**: Convert strings to LaTeX vector notation

   -  Automatic fallback to Unicode symbols when LaTeX fails
   -  Multiple fallback strategies (auto, mathtext, unicode, plain)
   -  Support for various vector naming conventions

-  **``safe_to_vec``**: Explicit fallback control for vector notation

   -  Fine-grained control over rendering behavior
   -  Predictable fallback strategies

Key Features
~~~~~~~~~~~~

1. **Robustness**: Comprehensive fallback mechanisms ensure rendering
   always succeeds
2. **Scientific Focus**: Designed specifically for mathematical and
   scientific notation
3. **Publication Ready**: Suitable for creating publication-quality
   mathematical content
4. **Error Tolerance**: Graceful handling of LaTeX rendering failures
5. **Flexibility**: Support for various mathematical expression types

Fallback Mechanisms
~~~~~~~~~~~~~~~~~~~

-  **LaTeX → MathText**: Falls back to matplotlib’s built-in math
   rendering
-  **LaTeX → Unicode**: Uses Unicode mathematical symbols
-  **LaTeX → Plain Text**: Simple text representation as last resort
-  **Automatic Detection**: Intelligent selection of best available
   renderer

Practical Applications
~~~~~~~~~~~~~~~~~~~~~~

-  **Scientific Papers**: Generate equations for academic publications
-  **Educational Materials**: Create mathematical content for teaching
-  **Presentations**: Mathematical slides and figures
-  **Documentation**: Technical documentation with mathematical notation
-  **Research Notebooks**: Interactive mathematical exploration

Use Cases
~~~~~~~~~

-  Physics equation previews and documentation
-  Statistical formula visualization
-  Machine learning mathematical foundations
-  Vector calculus and 3D mathematics
-  Publication-ready figure generation
-  Cross-platform mathematical notation (with fallbacks)

The ``scitex.tex`` module provides essential tools for scientific
mathematical notation with an emphasis on reliability and cross-platform
compatibility through intelligent fallback mechanisms.
