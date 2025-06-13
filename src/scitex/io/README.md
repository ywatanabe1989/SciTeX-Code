<!-- ---
!-- Timestamp: 2025-01-15 10:43:51
!-- Author: ywatanabe
!-- File: ./src/scitex/io/README.md
!-- --- -->

# SciTeX IO Module

The `scitex.io` module provides convenient functions for loading, saving, caching, and managing files and data in various formats. This guide will introduce some of the key functions.

## Loading Data

The `load` function allows you to read data from various file formats. It automatically detects the file type based on the extension and uses the appropriate method to load the data.

### Supported Formats

- **Tabular Data**: `.csv`, `.tsv`, `.xls`, `.xlsx`, `.xlsm`, `.xlsb`
- **Configuration Files**: `.json`, `.yaml`, `.yml`
- **Serialized Objects**: `.pkl`, `.joblib`, `.npy`, `.npz`, `.hdf5`
- **Machine Learning Models**: `.pth`, `.pt`, `.cbm`
- **Text and Documents**: `.txt`, `.md`, `.pdf`, `.docx`, `.xml`
- **Images**: `.jpg`, `.png`, `.tiff`, `.tif`
- **EEG Data**: `.vhdr`, `.vmrk`, `.edf`, `.bdf`, `.gdf`, `.cnt`, `.egi`, `.eeg`, `.set`

### Example Usage

```python
import scitex

# Load a CSV file into a pandas DataFrame
dataframe = scitex.io.load('data.csv')

# Load a JSON configuration file
config = scitex.io.load('config.json')

# Load a NumPy array from a .npy file
array = scitex.io.load('array.npy')

# Load an image file using PIL
image = scitex.io.load('image.png')

# Load a PyTorch model
model_state = scitex.io.load('model.pth')

# Load an EEG data file
eeg_data = scitex.io.load('subject1.edf')

# Load a YAML file
settings = scitex.io.load('settings.yaml')
```

## Saving Data

The `save` function lets you save various types of data to files. It determines the appropriate saving method based on the file extension you provide.

### Example Usage

```python
import scitex
import pandas as pd
import numpy as np
import torch
from PIL import Image

# Save a pandas DataFrame as a CSV file
df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
scitex.io.save(df, 'output.csv')

# Save a NumPy array to a .npy file
array = np.array([1, 2, 3])
scitex.io.save(array, 'array.npy')

# Save a PyTorch model's state dictionary
model = torch.nn.Linear(10, 1)
scitex.io.save(model.state_dict(), 'model.pth')

# Save an image using PIL
image = Image.new('RGB', (100, 100), color='red')
scitex.io.save(image, 'image.jpg')

# Save a dictionary as a JSON file
data = {'name': 'Alice', 'age': 30}
scitex.io.save(data, 'data.json')

# Save a text string to a .txt file
text = "Hello, World!"
scitex.io.save(text, 'hello.txt')
```

## Caching Data

The `cache` function provides a simple mechanism to store and retrieve Python objects using pickle files. It helps avoid recomputation by caching results.

### Example Usage

```python
from scitex

# Define variables to cache
var1 = "Hello"
var2 = 42

# Save variables to cache
var1, var2 = scitex.io.cache("my_cache_id", "var1", "var2")

# Later in your code, you can reload them
del var1, var2  # Simulate a fresh environment

# Load variables from cache
var1, var2 = scitex.io.cache("my_cache_id", "var1", "var2")

print(var1)  # Outputs: Hello
print(var2)  # Outputs: 42
```

## Working with File Patterns

The `glob` function extends the standard `glob.glob` functionality, providing natural sorting and support for curly brace expansion.

### Example Usage

```python
from scitex

# Find all .txt files in the data directory
files = scitex.io.glob('data/*.txt')
print(files)

# Use curly brace expansion to match multiple patterns
files = scitex.io.glob('data/{train,validation,test}/*.csv')
print(files)

# Parse file paths to extract variables
paths, parsed = scitex.io.glob('data/subject_{id}/session_{session}.csv', parse=True)

for path, params in zip(paths, parsed):
    print(f"File: {path}, Subject ID: {params['id']}, Session: {params['session']}")
```

## Flushing Output Streams

The `flush` function ensures that all pending write operations to `stdout` and `stderr` are completed. This can be useful when you need to make sure all outputs are written before the program continues or exits.

### Example Usage

```python
from scitex
import sys

print("This is printed to stdout.")
print("This is an error message.", file=sys.stderr)

# Flush the output streams
scitex.io.flush()
```

## Loading Configuration Files

The `load_configs` function loads YAML configuration files from the `./config` directory and merges them into a single dictionary. It also handles debug configurations if `IS_DEBUG` is set.

### Example Usage

```python
from scitex

# Load configurations (assuming YAML files are in ./config directory)
configs = scitex.io.load_configs()

# Access configuration values
db_host = configs.get('database_host')
api_key = configs.get('api_key')

# Access configuration values as DotDict
db_host = configs.database_host
api_key = configs.api_key
```

## Additional Functions

### Saving Images

You can use the `save` function to save images in various formats such as PNG, JPEG, and TIFF.

```python
from PIL import Image
import scitex

# Create or load an image
image = Image.open('input_image.png')

# Save the image in a different format
scitex.io.save(image, 'output_image.jpg')

# Save a Plotly figure
import plotly.express as px

fig = px.bar(x=['A', 'B', 'C'], y=[1, 3, 2])
scitex.io.save(fig, 'bar_chart.png')
```

## Contact
Yusuke Watanabe (ywatanabe@alumni.u-tokyo.ac.jp
