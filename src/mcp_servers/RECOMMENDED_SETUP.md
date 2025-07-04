# Recommended MCP Server Setup for SciTeX

Based on the goal of "easily convert Python code to follow SciTeX conventions", here's the streamlined server setup:

## 🎯 Essential Servers (Keep These)

### 1. `scitex-unified/` ⭐ **PRIMARY ENTRY POINT**
- **Purpose**: Main interface with simple `translate_to_scitex()` and `translate_from_scitex()` functions
- **Status**: ✅ Complete and working
- **Usage**: Primary tool for Claude Code clients

### 2. `scitex-io/` ⭐ **CORE TRANSLATIONS**  
- **Purpose**: I/O operations (most common conversions)
- **Status**: ✅ Complete with educational approach
- **Usage**: Detailed I/O guidance and examples

### 3. `scitex-plt/` ⭐ **PLOTTING CONVERSIONS**
- **Purpose**: Matplotlib → SciTeX plotting conversions  
- **Status**: ✅ Complete
- **Usage**: Enhanced plotting with automatic CSV export

### 4. `scitex-stats/` ⭐ **STATISTICS CONVERSIONS**
- **Purpose**: Statistical analysis conversions
- **Status**: ✅ Complete  
- **Usage**: Robust statistical testing with SciTeX

### 5. `scitex-project-validator/` ⭐ **PROJECT VALIDATION**
- **Purpose**: Validate and create SciTeX project structures
- **Status**: ✅ Complete with template generation
- **Usage**: Ensure proper project organization

### 6. `scitex-base/` 🔧 **FOUNDATION**
- **Purpose**: Base classes for other servers
- **Status**: ✅ Complete
- **Usage**: Infrastructure support

## 🤔 Redundant/Consolidate (Consider Removing)

### `scitex-io-translator/` vs `scitex-io/`
- **Issue**: Significant overlap in functionality
- **Recommendation**: Consolidate into `scitex-io/`
- **Action**: Keep the educational approach from `scitex-io/`

### `scitex-validator/` vs `scitex-project-validator/`  
- **Issue**: Both handle validation
- **Recommendation**: Keep `scitex-project-validator/` (more comprehensive)
- **Action**: Remove `scitex-validator/`

### `scitex-orchestrator/`
- **Issue**: Unclear necessity for basic conversion goals
- **Recommendation**: Remove unless specific use case
- **Action**: Functionality can be handled by `scitex-unified/`

### `scitex-analyzer/`
- **Issue**: Analysis features could be part of `scitex-unified/`
- **Recommendation**: Merge into `scitex-unified/`
- **Action**: Consolidate analysis tools

### `scitex-config/`
- **Issue**: Very specific, limited use
- **Recommendation**: Merge into relevant servers
- **Action**: Handle config management in main servers

## 🎯 Final Recommended Structure

```
mcp_servers/
├── scitex-base/              # Foundation
├── scitex-unified/           # 🎯 Main entry point  
├── scitex-io/                # 🎯 I/O conversions
├── scitex-plt/               # 🎯 Plotting conversions
├── scitex-stats/             # 🎯 Statistics conversions
├── scitex-project-validator/ # 🎯 Project validation & templates
├── docs/                     # Documentation
├── examples/                 # Usage examples
└── README.md                 # Setup guide
```

## Benefits of This Structure

1. **Clear Purpose**: Each server has a specific, non-overlapping role
2. **Simple Entry**: `scitex-unified/` provides the main interface
3. **Detailed Help**: Module-specific servers for deep guidance  
4. **Complete Workflow**: From code conversion to project setup
5. **Maintainable**: Fewer servers = easier maintenance

## Implementation Priority

1. ✅ Keep essential servers (already working)
2. 🔄 Merge redundant functionality 
3. 🗑️ Remove unnecessary servers
4. 📚 Update documentation and examples
5. 🚀 Create simple installation guide

This setup perfectly meets your requirement: **easy conversion to SciTeX conventions with Claude Code integration**.