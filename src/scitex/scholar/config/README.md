<!-- ---
!-- Timestamp: 2025-08-02 19:55:21
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/config/README.md
!-- --- -->

1. `CascadeConfig` - Universal config resolver with precedence hierarchy
2. `ScholarConfig` - Scholar-specific wrapper using CascadeConfig
3. `PathManager` - Directory structure management
4. Flattened YAML - No unnecessary nesting

## Usage
```python
config = ScholarConfig()
api_key = config.cascade.resolve("semantic_scholar_api_key")
is_debug = config.cascade.resolve("debug_mode", type=bool)
download_dir = config.path_manager.get_downloads_dir()
```

<!-- EOF -->