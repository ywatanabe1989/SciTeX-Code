# SciTeX MCP Servers Quick Start Guide

## What are MCP Servers?

Model Context Protocol (MCP) servers allow AI assistants (like Claude) to use specialized tools. The SciTeX MCP servers provide tools for translating between standard Python and SciTeX format.

## Quick Example

### 1. Install the servers
```bash
cd /path/to/scitex_repo/mcp_servers
./install_all.sh
```

### 2. Configure your MCP client

For Claude Desktop, add to your configuration:
```json
{
  "mcpServers": {
    "scitex-io": {
      "command": "python",
      "args": ["-m", "scitex_io.server"],
      "cwd": "/path/to/scitex_repo/mcp_servers/scitex-io"
    },
    "scitex-plt": {
      "command": "python",
      "args": ["-m", "scitex_plt.server"],
      "cwd": "/path/to/scitex_repo/mcp_servers/scitex-plt"
    }
  }
}
```

### 3. Use with Claude

Once configured, you can ask Claude to:
- "Translate this matplotlib code to SciTeX format"
- "Convert this SciTeX code back to standard Python"
- "Check if my code follows SciTeX conventions"
- "Suggest SciTeX improvements for my data analysis script"

## Translation Examples

### IO Operations
```python
# Your code:
df = pd.read_csv('data.csv')
df.to_excel('output.xlsx')

# Claude translates to:
df = stx.io.load('./data.csv')
stx.io.save(df, './output.xlsx', symlink_from_cwd=True)
```

### Plotting
```python
# Your code:
fig, ax = plt.subplots()
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_title('Plot')

# Claude translates to:
fig, ax = stx.plt.subplots()
ax.set_xyt('X', 'Y', 'Plot')
```

## Benefits

1. **Gradual Migration**: Convert your codebase piece by piece
2. **Learning Tool**: See SciTeX patterns applied to your code
3. **Bidirectional**: Share SciTeX code with non-users
4. **Validation**: Ensure you're using SciTeX correctly

## Next Steps

1. Run the demo: `python examples/demo_translation.py`
2. Test the servers: `./test_all.sh`
3. Try translating your own code with Claude
4. Check the full documentation in `README.md`