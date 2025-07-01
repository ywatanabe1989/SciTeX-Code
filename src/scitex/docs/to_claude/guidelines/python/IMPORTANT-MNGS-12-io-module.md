<!-- ---
!-- Timestamp: 2025-05-29 20:33:18
!-- Author: ywatanabe
!-- File: /ssh:ywatanabe@sp:/home/ywatanabe/.dotfiles/.claude/to_claude/guidelines/python/MNGS-12-mngs-io-module.md
!-- --- -->

## `mngs.io`

- `mngs.io` is a module for saving/loading data

### Input/Output Operations
**!!! IMPORTANT !!!**
**DO NOT MKDIR IN PYTHON SCRITPS. `mngs.io.save` MKDIR AUTOMATICALLY**
**PATH MUST BE ALWAYS RELATIVE FROM THE SCRIPT ITSELF**

### `mngs.io.load_configs`
```python
# Load all YAML files from ./config as a combined, dot-accessible dictionary
CONFIG = mngs.io.load_configs()

# Access configuration values
print(CONFIG.PATH.DATA)  # Access path defined in PATH.yaml

# Resolve f-strings in config
patient_id = "001"
data_path = eval(CONFIG.PATH.PATIENT_DATA)  # f"./data/patient_{patient_id}/data.csv"
```

#### `mngs.io.load`
```python
# Load data with automatic format detection based on extension
data = mngs.io.load('./data/results.csv')  # CSV file, using pandas
config = mngs.io.load('./config/params.yaml')  # YAML file
array = mngs.io.load('./data/features.npy')  # NumPy array
```

Supported File Extensions for `mngs.io.load` are:

| Category | Extensions |
|----------|------------|
| **Numeric Data** | `.npy`, `.npz`, `.mat`, `.h5`, `.hdf5` |
| **Tabular Data** | `.csv`, `.xlsx`, `.xls`, `.tsv` |
| **Text & Config** | `.json`, `.yaml`, `.yml`, `.xml`, `.txt` |
| **Python Objects** | `.pkl`, `.pickle`, `.joblib` |
| **Media** | `.jpg`, `.png`, `.gif`, `.tiff`, `.pdf`, `.mp3`, `.wav` |
| **Documents** | `.docx`, `.pdf` |
| **Special** | `.db`, `.sqlite3`, `.edf` (EEG data) |

#### `mngs.io.save`

Basic Usage:

``` python
# /path/to/script.py
obj = ...

# Saves to `/path/to/script_out/aab.ext`
mngs.io.save(obj, "./aab.ext", symlink_from_cwd=False)

# Saves to `/path/to/script_out/aab.ext` and create symlink to `$(pwd)/aab.ext`
mngs.io.save(obj, "./aab.ext", symlink_from_cwd=True) 

# Saves to `/path/to/script_out/aab/bbb.ext`
mngs.io.save(obj, "./aab/bbb.ext", symlink_from_cwd=False) 

# Saves to `/path/to/script_out/aab/bbb.ext` and create symlink to `$(pwd)/aab/bbb.ext`
mngs.io.save(obj, "./aab/bbb.ext", symlink_from_cwd=True) 
```

Supported File Extensions for `mngs.io.save` are:

| Category | Extensions |
|----------|------------|
| **Numeric Data** | `.npy`, `.npz`, `.mat`, `.h5`, `.hdf5` |
| **Tabular Data** | `.csv`, `.xlsx`, `.tsv` |
| **Text & Config** | `.json`, `.yaml`, `.yml`, `.txt` |
| **Python Objects** | `.pkl`, `.pickle`, `.joblib` |
| **Media** | `.jpg`, `.png`, `.gif`, `.tiff`, `.mp4`, `.html` |
| **Visualizations** | `.png`, `.jpg`, `.svg`, `.pdf`, `.html` |


Rules:
- `mngs.io.save` saves data in a unified manner with respecting extension
- `mngs.io.save` ensures the target directory exits
  - It calls `os.makedir("/path/to/target/directory", exists_ok=True)` internally
  - ENSURE NOT TO CREATE ANY DIRECTORY BY YOURSELF
- `mngs.io.save` creates symlink
  - ALWAYS explicitly specify `symlink_from_cwd=True` or `symlink_from_cwd=False`
- Relative path MUST start from dot (e.g., `./path/to/target` or `../../path/to/target`
- By combining `mngs.plt.subplots`, **PLOTTED DATA IS TRACKED AND SAVED AS CSV AS WELL AS THE IMAGE THEMSELVES**
  - Use `.jpg` for images to reduce size

#### Reversibility of `mngs.io.save` and `mngs.io.load`

Objects saved with `mngs.io.save()` can be loaded with `mngs.io.load()` while maintaining their original structure:

```python
# Save any Python object in a extension-aware manner
data = {"name": "example", "values": np.array([1, 2, 3])}
mngs.io.save(data, './data/example.pkl', symlink_from_cwd=True)

# Load it back with identical structure
loaded_data = mngs.io.load('./data/example.pkl')

# data and loaded_data are identical
```

## Your Understanding Check
Did you understand the guideline? If yes, please say:
`CLAUDE UNDERSTOOD: <THIS FILE PATH HERE>`

<!-- EOF -->