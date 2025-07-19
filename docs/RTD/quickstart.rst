Quick Start Guide
=================

This guide will help you get started with MNGS in just a few minutes.

Basic Usage
-----------

1. **Import and Initialize**

   .. code-block:: python

       import scitex
       import sys
       import matplotlib.pyplot as plt
       
       # Start a managed session
       CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(sys, plt)

2. **Load and Save Data**

   .. code-block:: python

       # Load data (auto-detects format)
       data = scitex.io.load("data.pkl")
       
       # Save data (auto-detects format from extension)
       scitex.io.save(data, "results.npy")

3. **Create Enhanced Plots**

   .. code-block:: python

       # Create plots with automatic data export
       fig, ax = scitex.plt.subplots()
       ax.plot([1, 2, 3], [1, 4, 9])
       ax.set_xlabel("X")
       ax.set_ylabel("Y²")
       plt.show()
       # Data automatically saved to CSV alongside plot

4. **Clean Up**

   .. code-block:: python

       # Always close to save logs
       scitex.gen.close(CONFIG)

Complete Example
----------------

Here's a complete example of a typical MNGS workflow:

.. code-block:: python

    import scitex
    import numpy as np
    import sys
    import matplotlib.pyplot as plt
    
    # Initialize MNGS
    CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(sys, plt)
    
    try:
        # Generate sample data
        x = np.linspace(0, 10, 100)
        y = np.sin(x) + np.random.normal(0, 0.1, 100)
        
        # Save data
        data = {"x": x, "y": y}
        scitex.io.save(data, "sample_data.pkl")
        
        # Create visualization
        fig, ax = scitex.plt.subplots(figsize=(8, 6))
        ax.plot(x, y, 'o', alpha=0.5, label='Noisy data')
        ax.plot(x, np.sin(x), 'r-', linewidth=2, label='True signal')
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Amplitude")
        ax.legend()
        ax.set_title("Sample Signal with Noise")
        
        # Signal processing
        from scitex.dsp import filt
        filtered = filt.lowpass(y, fs=10, cutoff=1)
        ax.plot(x, filtered, 'g--', linewidth=2, label='Filtered')
        ax.legend()
        
        # Save figure with auto-exported data
        plt.savefig("signal_analysis.png")
        
        # Statistical analysis
        correlation = scitex.stats.corr_test(x, y)
        print(f"Correlation: {correlation}")
        
    finally:
        # Clean up - saves all logs
        scitex.gen.close(CONFIG)

Key Concepts
------------

1. **Session Management**: Always use ``start()`` and ``close()``
2. **Automatic Logging**: All stdout/stderr is logged to timestamped files
3. **Format Detection**: I/O functions automatically detect file formats
4. **Data Preservation**: Plots automatically export underlying data
5. **Consistent API**: Similar patterns across all modules

Next Steps
----------

- Explore :doc:`modules/index` for detailed module documentation
- Check out :doc:`examples/index` for more examples
- Read :doc:`best_practices` for tips and recommendations

Common Patterns
---------------

**Loading Multiple Files**

.. code-block:: python

    import scitex
    from pathlib import Path
    
    # Load all CSV files in a directory
    data_files = scitex.io.glob("./data/*.csv")
    datasets = {f: scitex.io.load(f) for f in data_files}

**Batch Processing**

.. code-block:: python

    # Process multiple datasets
    results = {}
    for name, data in datasets.items():
        # Create output directory
        out_dir = scitex.gen.mk_spath(f"./results/{name}/")
        
        # Process
        processed = process_data(data)
        
        # Save results
        scitex.io.save(processed, out_dir + "processed.pkl")
        results[name] = processed

**Configuration Files**

.. code-block:: python

    # Load project configuration
    config = scitex.io.load("./config/experiment.yaml")
    
    # Start with custom config
    CONFIG, *_ = scitex.gen.start(CONFIG=config)

Tips
----

- Use ``scitex.io.load()`` for any file type - it auto-detects the format
- Take advantage of ``scitex.plt`` for publication-ready figures
- Use ``scitex.gen.mk_spath()`` to organize outputs with timestamps
- Leverage GPU acceleration in ``scitex.dsp`` for signal processing
- Check logs in ``[script_name]_out/`` directory for debugging