# Zotero Translator Execution Challenges

## User Request
> "use the zotero_translators javascript for our framework"

## Current Status
We have 675 Zotero translator JavaScript files loaded, but executing them properly is challenging.

## Technical Challenges

### 1. JavaScript Environment Mismatch
**Problem**: Zotero translators expect the full Zotero JavaScript environment
**Current**: We provide a minimal shim with basic APIs
**Result**: `SyntaxError: Unexpected token ':'` and other errors

### 2. Modern JavaScript Features
The translators use:
- `async/await` syntax
- Template literals with `${}`
- `for...of` loops with `const/let`
- Spread operators `...`
- Arrow functions `=>`

### 3. Complex Dependencies
Translators call other translators:
```javascript
const translate = Zotero.loadTranslator("search");
translate.setTranslator("b28d0d42-8549-4c6d-83fc-8382874a5cb9"); // CrossRef
```

### 4. API Requirements
Translators expect these Zotero APIs:
- `Zotero.loadTranslator()` - Load other translators
- `Zotero.selectItems()` - User selection dialog
- `Zotero.Utilities.*` - Dozens of utility functions
- `Zotero.HTTP` - Advanced HTTP handling
- `ZU` shorthand for utilities

## Solutions Attempted

### 1. Enhanced Shim ✅
Created comprehensive Zotero API shim with:
- Item types and constructors
- Basic utilities (xpath, text manipulation)
- HTTP request functions
- Translator loading stub

### 2. Code Injection Methods
Tried multiple approaches:
- Direct `eval()` - Syntax errors
- `new Function()` - Scope issues
- `AsyncFunction` constructor - Still syntax errors

### 3. Code Cleaning
- Remove test cases section
- Handle modern JS syntax
- Escape special characters

## Why Direct URL Patterns Currently Work Better

1. **Simplicity**: Just URL string manipulation
2. **Reliability**: No JavaScript execution needed
3. **Speed**: Instant results
4. **Compatibility**: Works with all browsers

Example:
```python
# Direct pattern for Nature
"nature.com/articles/X" → "nature.com/sci-hub.se/articles/X"
```

## The Fundamental Issue

The user wants to use Zotero translators "as is", but:

1. **Zotero's Environment**: Translators are designed for Zotero's specific JavaScript environment
2. **Our Environment**: Playwright browser with injected shim
3. **Gap**: Missing APIs, different JS engine, no translator dependencies

## Recommendations

### Option 1: Full Zotero Environment (User's Preference)
To truly use translators "as is":
1. Embed complete Zotero translation framework
2. Implement all Zotero APIs
3. Handle translator dependencies
4. Support all JS features

**Pros**: Use community-maintained translators
**Cons**: Major engineering effort

### Option 2: Hybrid Approach (Current)
1. Use direct patterns for known publishers
2. Fall back to Zotero translators when needed
3. Both benefit from OpenAthens authentication

**Pros**: Works today, fast, reliable
**Cons**: Not using translators "as is"

### Option 3: External Zotero Service
1. Run Zotero translation-server
2. Send URLs to service
3. Receive extracted metadata

**Pros**: Real Zotero environment
**Cons**: External dependency

## Conclusion

The user's request to use Zotero translators directly is valid - they're well-maintained by the community. However, running them outside Zotero's environment is technically challenging due to:

1. Complex JavaScript dependencies
2. Missing Zotero-specific APIs
3. Modern JS syntax issues
4. Translator interdependencies

The current hybrid approach provides good results while we work toward a more complete solution.