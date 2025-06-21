Core Concepts
=============

Understanding these core concepts will help you use MNGS effectively.

Philosophy
----------

MNGS (monogusa - "lazy" in Japanese) embodies the principle of making scientific computing as effortless as possible while maintaining rigor and reproducibility.

Key Principles
--------------

1. Automatic Everything
~~~~~~~~~~~~~~~~~~~~~~

MNGS automates common tasks that researchers often forget:

- **Logging**: All output is automatically logged with timestamps
- **Data Export**: Plots automatically save their underlying data
- **Path Management**: Output directories are created with timestamps
- **Format Detection**: File I/O automatically detects formats

2. Consistent Interface
~~~~~~~~~~~~~~~~~~~~~~~

All MNGS modules follow similar patterns:

.. code-block:: python

    # Loading any file type
    data = scitex.io.load("file.ext")  # Works for .pkl, .npy, .csv, .mat, etc.
    
    # Saving any data
    scitex.io.save(data, "output.ext")  # Format inferred from extension
    
    # Creating directories
    path = scitex.gen.mk_spath("./results")  # Always creates timestamped subdirs

3. Session Management
~~~~~~~~~~~~~~~~~~~~~

The session pattern ensures proper initialization and cleanup:

.. code-block:: python

    # Start session
    CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(sys, plt)
    
    # Your work here
    
    # Clean up - ensures logs are saved
    scitex.gen.close(CONFIG)

This pattern:
- Redirects stdout/stderr to log files
- Loads configuration
- Sets up matplotlib
- Ensures cleanup even if errors occur

4. Data Preservation
~~~~~~~~~~~~~~~~~~~~

MNGS prioritizes data preservation:

- **Plots**: Every plot saves its data to CSV
- **Logs**: All console output is preserved
- **Configs**: Settings are saved with results
- **Timestamps**: Everything is timestamped

Example with plotting:

.. code-block:: python

    fig, ax = scitex.plt.subplots()
    ax.plot(x, y)
    plt.savefig("plot.png")
    # Automatically creates plot.csv with the data

5. Scientific Workflow Integration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

MNGS is designed for typical scientific workflows:

.. code-block:: python

    # 1. Load experimental data
    raw_data = scitex.io.load("experiment_001.mat")
    
    # 2. Process signals
    filtered = scitex.dsp.filt.bandpass(raw_data['signal'], fs=1000, low=1, high=50)
    
    # 3. Statistical analysis
    results = scitex.stats.corr_test(filtered, raw_data['behavior'])
    
    # 4. Visualization
    fig, axes = scitex.plt.subplots(2, 1)
    axes[0].plot(raw_data['time'], filtered)
    axes[1].plot(results['correlation'])
    
    # 5. Save everything
    spath = scitex.gen.mk_spath("./results")
    scitex.io.save(results, spath + "analysis.pkl")
    plt.savefig(spath + "figures.png")

Architecture
------------

Module Organization
~~~~~~~~~~~~~~~~~~~

MNGS is organized into focused modules:

- **Core**: ``gen``, ``io`` - Essential functionality
- **Analysis**: ``stats``, ``pd`` - Data analysis tools
- **Visualization**: ``plt`` - Enhanced plotting
- **Signal Processing**: ``dsp``, ``nn`` - DSP and neural networks
- **Machine Learning**: ``ai`` - ML utilities
- **Utilities**: ``path``, ``str``, ``dict``, ``decorators``

Dependency Management
~~~~~~~~~~~~~~~~~~~~~

- Core modules (``gen``, ``io``) have minimal dependencies
- Specialized modules load dependencies on demand
- GPU operations fall back to CPU if CUDA unavailable

Error Handling
~~~~~~~~~~~~~~

MNGS uses defensive programming:

.. code-block:: python

    # Automatic format detection with fallbacks
    data = scitex.io.load("file.unknown")  # Tries multiple loaders
    
    # Graceful degradation
    filtered = scitex.dsp.filt.bandpass(signal)  # Uses GPU if available, else CPU
    
    # Robust statistics
    result = scitex.stats.describe(data)  # Handles NaN, inf gracefully

Best Practices
--------------

1. **Use Configuration Files**

   .. code-block:: yaml

       # config.yaml
       PROJECT: "MyExperiment"
       DATA_DIR: "./data"
       RESULTS_DIR: "./results"
       
       PROCESSING:
         SAMPLE_RATE: 1000
         FILTER_CUTOFF: [1, 50]

2. **Leverage Timestamps**

   .. code-block:: python

       # Creates: ./results/20250530-141523-12345/
       spath = scitex.gen.mk_spath("./results")
       
       # Organize by experiment
       for trial in trials:
           trial_path = scitex.gen.mk_spath(f"{spath}/trial_{trial}/")

3. **Chain Operations**

   .. code-block:: python

       # Process pipeline
       (scitex.io.load("raw.pkl")
        |> lambda d: scitex.dsp.filt.bandpass(d['signal'], fs=1000)
        |> lambda s: scitex.dsp.hilbert(s)
        |> lambda h: scitex.stats.describe(np.abs(h))
        |> lambda r: scitex.io.save(r, "results.pkl"))

4. **Use Context Managers**

   .. code-block:: python

       # Some modules provide context managers
       with scitex.gen.timed("Processing"):
           results = heavy_computation()

Common Patterns
---------------

Experiment Template
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import scitex
    import sys
    import matplotlib.pyplot as plt
    
    def main():
        # Initialize
        CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(
            sys, plt, 
            CONFIG="./config/experiment.yaml",
            seed=42
        )
        
        try:
            # Setup
            spath = scitex.gen.mk_spath(CONFIG['RESULTS_DIR'])
            
            # Load data
            data = scitex.io.load(CONFIG['DATA_FILE'])
            
            # Process
            results = analyze(data, CONFIG['PARAMS'])
            
            # Save
            scitex.io.save(results, spath + "results.pkl")
            scitex.io.save(CONFIG, spath + "config.yaml")
            
            # Visualize
            plot_results(results, spath)
            
        finally:
            scitex.gen.close(CONFIG)
    
    if __name__ == "__main__":
        main()

Batch Processing
~~~~~~~~~~~~~~~~

.. code-block:: python

    # Process multiple subjects
    for subject_id in scitex.io.glob("./data/sub-*"):
        with scitex.gen.timed(f"Processing {subject_id}"):
            data = scitex.io.load(f"{subject_id}/data.pkl")
            results = process_subject(data)
            
            spath = scitex.gen.mk_spath(f"./results/{subject_id}/")
            scitex.io.save(results, spath + "processed.pkl")