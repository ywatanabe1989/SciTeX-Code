# Getting Started with SciTeX MCP Servers

Welcome to the SciTeX MCP (Model Context Protocol) servers! This guide will help you get up and running quickly.

## 🚀 Quick Start (5 minutes)

### 1. Install All Servers
```bash
cd ~/proj/SciTeX-Code/mcp_servers
./install_all.sh
```

### 2. Configure Your MCP Client
Copy the example configuration to your MCP client config:
```bash
cp mcp_config_example.json ~/.config/your-mcp-client/config.json
```

### 3. Start Using!
The servers are now available in your MCP-compatible tools.

## 📚 What Can You Do?

### Create a New SciTeX Project
Ask your AI assistant:
> "Create a new SciTeX research project for analyzing neural data"

### Convert Existing Code
Share your Python script and ask:
> "Convert this to SciTeX format"

### Validate Your Code
> "Check if my script follows SciTeX guidelines"

### Generate Analysis Pipelines
> "Create a data cleaning pipeline for my DataFrame"
> "Generate a statistical analysis for these variables"
> "Create a signal filtering pipeline for EEG data"

## 🛠️ Available Servers

### Essential Servers
1. **scitex-io** - File I/O operations
   - Load/save any format with `stx.io.load()` and `stx.io.save()`
   - Automatic path management
   - 30+ formats supported

2. **scitex-plt** - Enhanced plotting
   - Matplotlib improvements
   - Combined axis labeling
   - Automatic data export

3. **scitex-framework** - Project templates
   - Generate complete projects
   - Create compliant scripts
   - Manage configurations

### Data Science Servers
4. **scitex-stats** - Statistical analysis
   - Test translations (t-test, ANOVA, etc.)
   - P-value formatting
   - Report generation

5. **scitex-pd** - Pandas enhancements
   - DataFrame operations
   - Data cleaning pipelines
   - EDA generation

6. **scitex-dsp** - Signal processing
   - Filter design
   - Frequency analysis
   - Spectral analysis

### Infrastructure Servers
7. **scitex-config** - Configuration management
8. **scitex-orchestrator** - Project coordination
9. **scitex-validator** - Compliance checking

## 💡 Example Workflows

### 1. Starting a New Project
```
You: Create a SciTeX project for EEG analysis
AI: [Uses scitex-framework to generate complete project structure]
    [Creates config files, main script, examples]
    [Sets up proper directory structure]
```

### 2. Converting Existing Analysis
```
You: Here's my data analysis script [paste code]
AI: [Uses translation servers to convert to SciTeX]
    [Validates against guidelines]
    [Suggests improvements]
```

### 3. Building Analysis Pipeline
```
You: I need to clean this dataset and run statistical tests
AI: [Generates data cleaning pipeline with scitex-pd]
    [Creates statistical analysis with scitex-stats]
    [Adds visualizations with scitex-plt]
```

## 🔧 Manual Server Usage

### Launch Individual Servers
```bash
cd scitex-io
python -m server
```

### Launch All Servers
```bash
./launch_all.sh
```

### Test Servers
```bash
./test_all.sh
```

## 📖 Learning Resources

### Examples Directory
Check `examples/` for:
- `demo_translation.py` - See translations in action
- `quickstart.md` - More detailed guide

### Pattern Explanations
Ask your AI:
> "Explain the SciTeX pattern for file saving"
> "Why does SciTeX use script-relative paths?"

### Best Practices
The servers automatically guide you toward:
- Reproducible file paths
- Proper configuration management
- Statistical best practices
- Clean code patterns

## 🐛 Troubleshooting

### Server Not Found
Make sure you've run `./install_all.sh`

### Import Errors
Ensure scitex is installed:
```bash
pip install -e ~/proj/scitex_repo
```

### Configuration Issues
Check that config files exist in `./config/` directory

## 🎯 Next Steps

1. **Try the Examples** - Run the demo scripts
2. **Convert Your Code** - Start with a simple script
3. **Create a Project** - Use the framework generator
4. **Explore Features** - Try different servers

## 💬 Getting Help

Ask your AI assistant:
- "How do I use SciTeX for [specific task]?"
- "Show me SciTeX best practices for [topic]"
- "Debug this SciTeX error: [error message]"

## 🌟 Pro Tips

1. **Start Small** - Convert one script at a time
2. **Use Templates** - Let the framework generator create boilerplate
3. **Check Compliance** - Run validation frequently
4. **Learn Patterns** - Ask for explanations of SciTeX patterns
5. **Automate Workflows** - Use pipeline generation tools

---

Welcome to the SciTeX ecosystem! These MCP servers are your development partners, helping you write better, more reproducible scientific code. 🚀

<!-- EOF -->