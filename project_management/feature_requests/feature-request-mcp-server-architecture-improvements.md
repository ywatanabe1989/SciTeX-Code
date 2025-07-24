# Feature Request: MCP Server Architecture Improvements

**Date**: 2025-06-29  
**Requester**: CLAUDE-2efbf2a1-4606-4429-9550-df79cd2273b6  
**Priority**: Medium  
**Status**: ✅ COMPLETED (2025-01-25) - Unified MCP Architecture Phase 1 & 2

## Summary

Refactor the current MCP server architecture to adopt a more modular, maintainable design based on the suggestions in `/home/ywatanabe/proj/scitex_repo/mcp_servers/suggestions.md`.

## Current State

- Separate MCP servers for each module (scitex-io, scitex-plt)
- Self-contained servers with embedded translation logic
- Some code duplication between servers
- Works well but could be more maintainable

## Proposed Improvements

### 1. Unified Server Architecture
- Single MCP server with pluggable module translators
- Shared base classes and utilities
- Better separation of concerns

### 2. Base Translator Pattern
```python
class BaseTranslator(ABC):
    async def to_scitex(self, code: str, context: Dict = None)
    async def from_scitex(self, code: str, target_style: str = "standard")
```

### 3. Context-Aware Translation
- Add context analyzer to understand code structure
- Enable smarter, context-dependent transformations
- Handle module dependencies correctly

### 4. Improved Organization
```
scitex_translators/
├── server.py              # Unified MCP server
├── core/                  # Shared infrastructure
├── modules/               # One translator per scitex module
├── config/                # Configuration extraction
└── validators/            # Module-specific validation
```

## Benefits

1. **Maintainability**: Easier to add new modules
2. **Code Reuse**: Shared base classes reduce duplication
3. **Testability**: Each component can be tested independently
4. **Flexibility**: Can apply multiple translators in order
5. **Extensibility**: Pluggable architecture for future modules

## Implementation Plan

### Phase 1: Core Infrastructure
- [ ] Create base translator abstract class
- [ ] Implement context analyzer
- [ ] Set up shared validation utilities

### Phase 2: Module Migration
- [ ] Migrate IO translator to new architecture
- [ ] Migrate PLT translator to new architecture
- [ ] Add module ordering logic

### Phase 3: Enhanced Features
- [ ] Add configuration extraction modules
- [ ] Implement module-specific validators
- [ ] Create comprehensive test suite

### Phase 4: Deployment
- [ ] Update documentation
- [ ] Maintain backward compatibility
- [ ] Deprecate old servers gracefully

## Backward Compatibility

- Keep existing servers operational during transition
- Provide migration guide for users
- Support both architectures temporarily

## Notes

- Current implementation is functional and meets immediate needs
- This refactoring is for long-term maintainability
- Should be implemented after initial user feedback

# EOF