# SciTeX PLT MCP Server

MCP server for translating matplotlib plotting code to/from SciTeX plt module format.

## Features

- **Bidirectional Translation**: Convert between standard matplotlib and SciTeX plt
- **Data Tracking**: Automatic tracking of plotted data with CSV export
- **Combined Labeling**: Convert separate xlabel/ylabel/title to set_xyt()
- **Code Analysis**: Identify plotting patterns and suggest improvements
- **Validation**: Check SciTeX plt module usage compliance

## Available Tools

1. **translate_to_scitex** - Convert matplotlib code to SciTeX format
2. **translate_from_scitex** - Convert SciTeX code back to matplotlib
3. **analyze_plotting_operations** - Analyze plotting patterns in code
4. **suggest_data_tracking** - Suggest data tracking improvements
5. **convert_axis_labels_to_xyt** - Convert separate labels to set_xyt
6. **validate_code** - Validate SciTeX plt usage
7. **suggest_improvements** - Analyze improvement opportunities

## Installation

```bash
cd mcp_servers/scitex-plt
pip install -e .
```

## Usage

Start the server:
```bash
python -m scitex_plt.server
```

## Translation Examples

### To SciTeX
```python
# Input (matplotlib)
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
ax.plot(x, y)
ax.set_xlabel('X values')
ax.set_ylabel('Y values')
ax.set_title('My Plot')
plt.savefig('output.png')

# Output (scitex)
import scitex as stx

fig, ax = stx.plt.subplots()
ax.plot(x, y)
ax.set_xyt('X values', 'Y values', 'My Plot')
plt.savefig('output.png')  # Consider using stx.io.save() for data export
```

### From SciTeX
```python
# Input (scitex)
fig, ax = stx.plt.subplots()
ax.set_xyt('X', 'Y', 'Title')

# Output (matplotlib)
fig, ax = plt.subplots()
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_title('Title')
```

## Key Benefits

1. **Automatic Data Export**: When using `stx.plt.subplots()` and `stx.io.save()`, plotted data is automatically exported to CSV
2. **Concise Code**: `set_xyt()` reduces 3 lines to 1 for axis labeling
3. **Better Reproducibility**: All plot data is tracked and exportable
4. **Seamless Migration**: Bidirectional translation enables gradual adoption
ENDOFFILE < /dev/null
