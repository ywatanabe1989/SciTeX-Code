# How Zotero JavaScript Translators Are Executed

## Current Implementation

The JavaScript translators are NOT running "as-is" in the Zotero environment. Instead:

### 1. Execution Environment
- **Browser**: Playwright (Chromium) browser instance
- **Page Context**: Real webpage loaded with actual content
- **Injection Method**: 
  ```javascript
  eval(translatorCode);  // Direct eval of the translator JS file
  ```

### 2. Zotero API Shim
A minimal "shim" is injected to provide basic Zotero APIs:

```javascript
window.Zotero = {
    itemTypes: { journalArticle: "journalArticle", ... },
    debug: function(msg) { console.log("[Zotero]", msg); },
    Item: function(type) { ... },
    Utilities: {
        requestDocument: async function(url, callback) { ... },
        // ... other utilities
    }
}
```

### 3. Execution Flow
1. **Load translator JS file** from disk
2. **Inject Zotero shim** into browser page
3. **Navigate to target URL**
4. **eval() the translator code** directly
5. **Call detectWeb()** to check if page matches
6. **Call doWeb()** to extract data
7. **Collect results** from `window._zoteroItems`

## Problems with This Approach

### 1. Incomplete Zotero API
The shim only provides basic functions. Many translators expect:
- `Zotero.loadTranslator()` - for calling other translators
- `ZU` utilities object with many helper functions
- `Zotero.HTTP` methods
- `Zotero.selectItems()` for multiple item selection
- And many more...

### 2. Syntax Errors
As seen in the test: `SyntaxError: Unexpected token ':'`
This happens because:
- Translators expect a specific JavaScript environment
- Some use ES6+ features that need transpilation
- Others rely on Zotero's specific JavaScript engine quirks

### 3. Missing Dependencies
Many translators load other translators:
```javascript
var translator = Zotero.loadTranslator("web");
translator.setTranslator("951c027d-74ac-47d4-a107-9c3069ab7b48");
```
This fails because the shim doesn't implement translator loading.

## Why Direct Patterns Work Better

1. **Simpler**: Just URL manipulation, no JS execution
2. **Faster**: No browser automation needed
3. **More Reliable**: No dependency on complex JS environment
4. **Maintainable**: Easy to update when publishers change

## The User's Point

The user is correct that "we should not use house-made function but it is better to use the JS package as is."

To truly use Zotero translators as-is, we would need:
1. The full Zotero translation framework
2. All supporting libraries and utilities
3. Proper JavaScript environment setup
4. Translator dependency resolution

## Current Status

The system currently:
- ✅ Loads all 675 translator files
- ✅ Matches URLs to appropriate translators
- ⚠️ Tries to execute them with minimal shim
- ❌ Often fails due to missing APIs
- ✅ Falls back to direct patterns (which work well)

## Recommendation

The hybrid approach is actually good:
1. Try direct patterns first (fast, reliable)
2. Use Zotero translators for complex sites
3. Both benefit from OpenAthens authentication

To fully support Zotero translators "as-is" would require embedding the entire Zotero translation framework, which is a major undertaking.