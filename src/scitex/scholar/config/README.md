<!-- ---
!-- Timestamp: 2025-10-13 09:47:44
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/config/README.md
!-- --- -->

## Cascading Config Environment Variables
Configurations has precedence of:
1. Direct Specification
2. Configuration
3. Environmental Varibales
Example can be seen at `./config/default.yaml`

## Usage
```python
config = ScholarConfig()
api_key = config.cascade.resolve("semantic_scholar_api_key")
is_debug = config.cascade.resolve("debug_mode", type=bool)
download_dir = config.path_manager.get_library_downloads_dir()
```

## Modules
1. `CascadeConfig` - Universal config resolver with precedence hierarchy
2. `ScholarConfig` - Scholar-specific wrapper using CascadeConfig
3. `PathManager` - Directory structure management
4. Flattened YAML - No unnecessary nesting

## TODO
- [ ] Migrate to separated files

<!-- EOF -->