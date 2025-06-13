Quick Start Guide
=================

This guide will help you get started with MNGS in just a few minutes.

Basic Usage
-----------

1. **Import and Initialize**

   .. code-block:: python

       import mngs
       import sys
       import matplotlib.pyplot as plt
       
       # Start a managed session
       CONFIG, sys.stdout, sys.stderr, plt, CC = mngs.gen.start(sys, plt)

2. **Load and Save Data**

   .. code-block:: python

       # Load data (auto-detects format)
       data = mngs.io.load("data.pkl")
       
       # Save data (auto-detects format from extension)
       mngs.io.save(data, "results.npy")

3. **Create Enhanced Plots**

   .. code-block:: python

       # Create plots with automatic data export
       fig, ax = mngs.plt.subplots()
       ax.plot([1, 2, 3], [1, 4, 9])
       ax.set_xlabel("X")
       ax.set_ylabel("Y²")
       plt.show()
       # Data automatically saved to CSV alongside plot

4. **Clean Up**

   .. code-block:: python

       # Always close to save logs
       mngs.gen.close(CONFIG)

Complete Example
----------------

Here's a complete example of a typical MNGS workflow:

.. code-block:: python

    import mngs
    import numpy as np
    import sys
    import matplotlib.pyplot as plt
    
    # Initialize MNGS
    CONFIG, sys.stdout, sys.stderr, plt, CC = mngs.gen.start(sys, plt)
    
    try:
        # Generate sample data
        x = np.linspace(0, 10, 100)
        y = np.sin(x) + np.random.normal(0, 0.1, 100)
        
        # Save data
        data = {"x": x, "y": y}
        mngs.io.save(data, "sample_data.pkl")
        
        # Create visualization
        fig, ax = mngs.plt.subplots(figsize=(8, 6))
        ax.plot(x, y, 'o', alpha=0.5, label='Noisy data')
        ax.plot(x, np.sin(x), 'r-', linewidth=2, label='True signal')
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Amplitude")
        ax.legend()
        ax.set_title("Sample Signal with Noise")
        
        # Signal processing
        from mngs.dsp import filt
        filtered = filt.lowpass(y, fs=10, cutoff=1)
        ax.plot(x, filtered, 'g--', linewidth=2, label='Filtered')
        ax.legend()
        
        # Save figure with auto-exported data
        plt.savefig("signal_analysis.png")
        
        # Statistical analysis
        correlation = mngs.stats.corr_test(x, y)
        print(f"Correlation: {correlation}")
        
    finally:
        # Clean up - saves all logs
        mngs.gen.close(CONFIG)

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

    import mngs
    from pathlib import Path
    
    # Load all CSV files in a directory
    data_files = mngs.io.glob("./data/*.csv")
    datasets = {f: mngs.io.load(f) for f in data_files}

**Batch Processing**

.. code-block:: python

    # Process multiple datasets
    results = {}
    for name, data in datasets.items():
        # Create output directory
        out_dir = mngs.gen.mk_spath(f"./results/{name}/")
        
        # Process
        processed = process_data(data)
        
        # Save results
        mngs.io.save(processed, out_dir + "processed.pkl")
        results[name] = processed

**Configuration Files**

.. code-block:: python

    # Load project configuration
    config = mngs.io.load("./config/experiment.yaml")
    
    # Start with custom config
    CONFIG, *_ = mngs.gen.start(CONFIG=config)

Tips
----

- Use ``mngs.io.load()`` for any file type - it auto-detects the format
- Take advantage of ``mngs.plt`` for publication-ready figures
- Use ``mngs.gen.mk_spath()`` to organize outputs with timestamps
- Leverage GPU acceleration in ``mngs.dsp`` for signal processing
- Check logs in ``[script_name]_out/`` directory for debugging