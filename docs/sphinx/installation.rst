Installation
============

Requirements
------------

- Python 3.8 or higher
- pip package manager

Installing MNGS
---------------

From PyPI (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    pip install mngs

From Source
~~~~~~~~~~~

Clone the repository and install in development mode:

.. code-block:: bash

    git clone https://github.com/ywatanabe1989/mngs.git
    cd mngs
    pip install -e .

Dependencies
------------

MNGS has several optional dependencies for specific functionalities:

Core Dependencies
~~~~~~~~~~~~~~~~~

These are installed automatically:

- numpy
- pandas
- matplotlib
- scipy
- scikit-learn

Optional Dependencies
~~~~~~~~~~~~~~~~~~~~~

For deep learning features:

.. code-block:: bash

    pip install torch torchvision torchaudio

For advanced signal processing:

.. code-block:: bash

    pip install mne tensorpac ripple_detection

For database operations:

.. code-block:: bash

    pip install psycopg2-binary sqlalchemy

For all optional dependencies:

.. code-block:: bash

    pip install mngs[all]

Verifying Installation
----------------------

To verify your installation:

.. code-block:: python

    import mngs
    print(mngs.__version__)
    
    # Test basic functionality
    CONFIG, sys, _, plt, _ = mngs.gen.start()
    print("MNGS successfully initialized!")
    mngs.gen.close(CONFIG)

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

1. **Import Error**: If you encounter import errors, ensure all dependencies are installed:

   .. code-block:: bash

       pip install -r requirements.txt

2. **GPU Support**: For GPU acceleration, ensure PyTorch is installed with CUDA support:

   .. code-block:: bash

       pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

3. **Missing Optional Dependencies**: Some modules require additional packages. Install them as needed or use:

   .. code-block:: bash

       pip install mngs[all]

Getting Help
~~~~~~~~~~~~

If you encounter issues:

1. Check the :doc:`troubleshooting guide <troubleshooting>`
2. Search existing `GitHub issues <https://github.com/ywatanabe1989/mngs/issues>`_
3. Create a new issue with a minimal reproducible example