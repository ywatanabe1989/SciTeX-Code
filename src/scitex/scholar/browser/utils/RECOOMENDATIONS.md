<!-- ---
!-- Timestamp: 2025-08-22 01:43:08
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/browser/utils/RECOOMENDATIONS.md
!-- --- -->

# Browser JavaScript Utilities for Playwright

## Directory Structure
```
src/scitex/scholar/browser/js/
├── ui/
│   ├── popup_message.js
│   ├── highlight_element.js
│   ├── show_grid.js
│   └── progress_indicator.js
├── pdf/
│   ├── detect_pdf_viewer.js
│   ├── extract_pdf_metadata.js
│   └── monitor_pdf_download.js
├── navigation/
│   ├── scroll_utilities.js
│   ├── wait_for_element.js
│   └── detect_redirects.js
├── interaction/
│   ├── click_fallbacks.js
│   ├── fill_fallbacks.js
│   └── element_visibility.js
├── data/
│   ├── extract_links.js
│   ├── extract_tables.js
│   └── extract_metadata.js
└── debug/
    ├── console_logger.js
    ├── performance_monitor.js
    └── network_monitor.js
```

## 1. UI Utilities

### `ui/popup_message.js`
```javascript
// Show customizable popup message
function showPopupMessage(message, options = {}) {
    const defaults = {
        duration: 5000,
        position: 'top',
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        textColor: 'white',
        fontSize: '20px',
        zIndex: 10000
    };
    
    const config = { ...defaults, ...options };
    
    // Remove existing popups
    document.querySelectorAll('.scitex-popup').forEach(el => el.remove());
    
    const popup = document.createElement('div');
    popup.className = 'scitex-popup';
    popup.innerHTML = message;
    popup.style.cssText = `
        position: fixed;
        ${config.position === 'top' ? 'top: 20px;' : 'bottom: 20px;'}
        left: 50%;
        transform: translateX(-50%);
        background: ${config.backgroundColor};
        color: ${config.textColor};
        padding: 15px 25px;
        border-radius: 8px;
        font-size: ${config.fontSize};
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        z-index: ${config.zIndex};
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        animation: slideIn 0.3s ease-out;
    `;
    
    // Add animation styles
    if (!document.querySelector('#scitex-animations')) {
        const style = document.createElement('style');
        style.id = 'scitex-animations';
        style.textContent = `
            @keyframes slideIn {
                from { transform: translate(-50%, -20px); opacity: 0; }
                to { transform: translate(-50%, 0); opacity: 1; }
            }
        `;
        document.head.appendChild(style);
    }
    
    document.body.appendChild(popup);
    
    if (config.duration > 0) {
        setTimeout(() => {
            if (popup.parentNode) {
                popup.style.animation = 'slideOut 0.3s ease-in';
                setTimeout(() => popup.remove(), 300);
            }
        }, config.duration);
    }
    
    return popup;
}
```

### `ui/highlight_element.js`
```javascript
// Highlight element with customizable overlay
function highlightElement(element, options = {}) {
    const defaults = {
        duration: 1000,
        borderColor: 'red',
        borderWidth: 5,
        backgroundColor: 'rgba(255, 0, 0, 0.2)',
        scrollIntoView: true,
        pulse: true
    };
    
    const config = { ...defaults, ...options };
    
    if (!element) return null;
    
    const rect = element.getBoundingClientRect();
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;
    
    const overlay = document.createElement('div');
    overlay.className = 'scitex-highlight';
    overlay.style.cssText = `
        position: absolute;
        top: ${rect.top + scrollTop}px;
        left: ${rect.left + scrollLeft}px;
        width: ${rect.width}px;
        height: ${rect.height}px;
        border: ${config.borderWidth}px solid ${config.borderColor};
        background-color: ${config.backgroundColor};
        pointer-events: none;
        z-index: 999999;
        box-shadow: 0 0 20px ${config.borderColor};
        ${config.pulse ? 'animation: pulse 1s infinite;' : ''}
    `;
    
    // Add pulse animation
    if (config.pulse && !document.querySelector('#scitex-pulse')) {
        const style = document.createElement('style');
        style.id = 'scitex-pulse';
        style.textContent = `
            @keyframes pulse {
                0% { opacity: 1; }
                50% { opacity: 0.5; }
                100% { opacity: 1; }
            }
        `;
        document.head.appendChild(style);
    }
    
    document.body.appendChild(overlay);
    
    if (config.scrollIntoView) {
        element.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
    
    if (config.duration > 0) {
        setTimeout(() => overlay.remove(), config.duration);
    }
    
    return overlay;
}
```

### `ui/progress_indicator.js`
```javascript
// Create progress indicator for long operations
function createProgressIndicator(options = {}) {
    const defaults = {
        message: 'Processing...',
        showPercentage: true,
        showSpinner: true,
        position: 'center'
    };
    
    const config = { ...defaults, ...options };
    
    const indicator = document.createElement('div');
    indicator.className = 'scitex-progress';
    indicator.style.cssText = `
        position: fixed;
        ${config.position === 'center' ? `
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
        ` : `
            top: 20px;
            right: 20px;
        `}
        background: white;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        z-index: 10000;
        min-width: 200px;
    `;
    
    indicator.innerHTML = `
        <div style="display: flex; align-items: center; gap: 10px;">
            ${config.showSpinner ? `
                <div class="spinner" style="
                    width: 20px;
                    height: 20px;
                    border: 3px solid #f3f3f3;
                    border-top: 3px solid #3498db;
                    border-radius: 50%;
                    animation: spin 1s linear infinite;
                "></div>
            ` : ''}
            <div>
                <div class="message" style="font-weight: 500;">${config.message}</div>
                ${config.showPercentage ? `
                    <div class="percentage" style="color: #666; font-size: 14px; margin-top: 5px;">0%</div>
                ` : ''}
            </div>
        </div>
    `;
    
    // Add spinner animation
    if (config.showSpinner && !document.querySelector('#scitex-spinner')) {
        const style = document.createElement('style');
        style.id = 'scitex-spinner';
        style.textContent = `
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        `;
        document.head.appendChild(style);
    }
    
    document.body.appendChild(indicator);
    
    return {
        element: indicator,
        updateMessage: (msg) => {
            indicator.querySelector('.message').textContent = msg;
        },
        updatePercentage: (pct) => {
            const pctElement = indicator.querySelector('.percentage');
            if (pctElement) pctElement.textContent = `${pct}%`;
        },
        remove: () => indicator.remove()
    };
}
```

## 2. PDF Utilities

### `pdf/detect_pdf_viewer.js`
```javascript
// Comprehensive PDF viewer detection
function detectPDFViewer() {
    const checks = {
        // Chrome PDF viewer
        chromeEmbed: !!document.querySelector('embed[type="application/pdf"]'),
        chromePlugin: !!document.querySelector('embed[name="plugin"]'),
        
        // PDF.js viewer
        pdfjs: !!(window.PDFViewerApplication || window.pdfjsLib),
        pdfjsViewer: !!document.querySelector('#viewer.pdfViewer'),
        
        // Generic iframe
        iframe: !!document.querySelector('iframe[src*=".pdf"]'),
        
        // Object embed
        object: !!document.querySelector('object[type="application/pdf"]'),
        
        // Various viewer UI elements
        viewerUI: !!(
            document.querySelector('[data-testid="pdf-viewer"]') ||
            document.querySelector('.pdf-viewer') ||
            document.querySelector('#pdf-viewer')
        ),
        
        // Check content type
        isPDFUrl: window.location.href.toLowerCase().includes('.pdf'),
        
        // Check for PDF-specific controls
        hasControls: !!(
            document.querySelector('[aria-label*="PDF"]') ||
            document.querySelector('[title*="PDF"]')
        )
    };
    
    const detected = Object.values(checks).some(v => v);
    
    return {
        detected,
        type: detected ? Object.keys(checks).find(k => checks[k]) : null,
        details: checks
    };
}
```

### `pdf/extract_pdf_metadata.js`
```javascript
// Extract PDF metadata if available
function extractPDFMetadata() {
    const metadata = {
        title: null,
        author: null,
        subject: null,
        keywords: null,
        creator: null,
        producer: null,
        creationDate: null,
        modDate: null,
        pageCount: null,
        fileSize: null
    };
    
    // Try to get from PDF.js
    if (window.PDFViewerApplication) {
        const app = window.PDFViewerApplication;
        if (app.documentInfo) {
            Object.assign(metadata, app.documentInfo);
        }
        if (app.pdfDocument) {
            metadata.pageCount = app.pdfDocument.numPages;
        }
    }
    
    // Try to extract from page title
    if (!metadata.title) {
        metadata.title = document.title.replace(/\.pdf$/i, '').trim();
    }
    
    // Try to get file size from network
    const perf = performance.getEntriesByType('resource')
        .find(r => r.name.includes('.pdf'));
    if (perf) {
        metadata.fileSize = perf.transferSize;
    }
    
    return metadata;
}
```

## 3. Navigation Utilities

### `navigation/scroll_utilities.js`
```javascript
// Advanced scrolling utilities
const scrollUtils = {
    // Smooth scroll to element
    scrollToElement(element, options = {}) {
        const defaults = {
            behavior: 'smooth',
            block: 'center',
            inline: 'nearest',
            offsetTop: 0
        };
        
        const config = { ...defaults, ...options };
        
        if (config.offsetTop) {
            const y = element.getBoundingClientRect().top + window.pageYOffset + config.offsetTop;
            window.scrollTo({ top: y, behavior: config.behavior });
        } else {
            element.scrollIntoView(config);
        }
    },
    
    // Scroll page by percentage
    scrollByPercentage(percentage, smooth = true) {
        const maxScroll = document.documentElement.scrollHeight - window.innerHeight;
        const targetScroll = (maxScroll * percentage) / 100;
        
        window.scrollTo({
            top: targetScroll,
            behavior: smooth ? 'smooth' : 'auto'
        });
    },
    
    // Check if element is in viewport
    isInViewport(element) {
        const rect = element.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    },
    
    // Get scroll percentage
    getScrollPercentage() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const scrollHeight = document.documentElement.scrollHeight;
        const clientHeight = document.documentElement.clientHeight;
        
        if (scrollHeight === clientHeight) return 100;
        
        return Math.round((scrollTop / (scrollHeight - clientHeight)) * 100);
    }
};
```

### `navigation/wait_for_element.js`
```javascript
// Wait for element with timeout
function waitForElement(selector, options = {}) {
    const defaults = {
        timeout: 30000,
        interval: 100,
        visible: false,
        parent: document
    };
    
    const config = { ...defaults, ...options };
    
    return new Promise((resolve, reject) => {
        const startTime = Date.now();
        
        const check = () => {
            const element = config.parent.querySelector(selector);
            
            if (element) {
                if (!config.visible || (element.offsetWidth > 0 && element.offsetHeight > 0)) {
                    resolve(element);
                    return;
                }
            }
            
            if (Date.now() - startTime > config.timeout) {
                reject(new Error(`Timeout waiting for element: ${selector}`));
                return;
            }
            
            setTimeout(check, config.interval);
        };
        
        check();
    });
}
```

## 4. Interaction Utilities

### `interaction/click_fallbacks.js`
```javascript
// Click with multiple fallback methods
function clickWithFallbacks(selector) {
    const element = typeof selector === 'string' 
        ? document.querySelector(selector) 
        : selector;
    
    if (!element) {
        return { success: false, method: null, error: 'Element not found' };
    }
    
    const methods = [
        // Method 1: Standard click
        () => {
            element.click();
            return 'standard';
        },
        
        // Method 2: Dispatch mouse events
        () => {
            const events = ['mousedown', 'mouseup', 'click'];
            events.forEach(eventType => {
                const event = new MouseEvent(eventType, {
                    view: window,
                    bubbles: true,
                    cancelable: true
                });
                element.dispatchEvent(event);
            });
            return 'mouseEvents';
        },
        
        // Method 3: Focus and trigger
        () => {
            element.focus();
            element.click();
            return 'focusClick';
        },
        
        // Method 4: jQuery if available
        () => {
            if (window.jQuery) {
                jQuery(element).trigger('click');
                return 'jquery';
            }
            throw new Error('jQuery not available');
        }
    ];
    
    for (const method of methods) {
        try {
            const methodName = method();
            return { success: true, method: methodName, element };
        } catch (e) {
            continue;
        }
    }
    
    return { success: false, method: null, error: 'All methods failed' };
}
```

### `interaction/fill_fallbacks.js`
```javascript
// Fill input with multiple fallback methods
function fillWithFallbacks(selector, value) {
    const element = typeof selector === 'string'
        ? document.querySelector(selector)
        : selector;
    
    if (!element) {
        return { success: false, method: null, error: 'Element not found' };
    }
    
    const methods = [
        // Method 1: Direct value assignment
        () => {
            element.value = value;
            element.dispatchEvent(new Event('input', { bubbles: true }));
            element.dispatchEvent(new Event('change', { bubbles: true }));
            return 'direct';
        },
        
        // Method 2: Native setter
        () => {
            const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                window.HTMLInputElement.prototype,
                'value'
            ).set;
            nativeInputValueSetter.call(element, value);
            element.dispatchEvent(new Event('input', { bubbles: true }));
            return 'nativeSetter';
        },
        
        // Method 3: Focus, clear, and type
        () => {
            element.focus();
            element.select();
            document.execCommand('insertText', false, value);
            return 'execCommand';
        },
        
        // Method 4: React-specific
        () => {
            const lastValue = element.value;
            element.value = value;
            const event = new Event('input', { bubbles: true });
            const tracker = element._valueTracker;
            if (tracker) {
                tracker.setValue(lastValue);
            }
            element.dispatchEvent(event);
            return 'react';
        }
    ];
    
    for (const method of methods) {
        try {
            const methodName = method();
            // Verify the value was set
            if (element.value === value) {
                return { success: true, method: methodName, element };
            }
        } catch (e) {
            continue;
        }
    }
    
    return { success: false, method: null, error: 'All methods failed' };
}
```

## 5. Data Extraction Utilities

### `data/extract_links.js`
```javascript
// Extract and categorize links
function extractLinks(options = {}) {
    const defaults = {
        unique: true,
        absoluteUrls: true,
        categorize: true,
        includeMetadata: true
    };
    
    const config = { ...defaults, ...options };
    
    const links = Array.from(document.querySelectorAll('a[href]')).map(link => {
        const href = link.href;
        const text = link.textContent.trim();
        
        const data = {
            href: config.absoluteUrls ? link.href : link.getAttribute('href'),
            text: text.substring(0, 100),
            title: link.title || null
        };
        
        if (config.includeMetadata) {
            data.target = link.target || '_self';
            data.rel = link.rel || null;
            data.isExternal = link.hostname !== window.location.hostname;
            data.protocol = link.protocol;
            data.isPDF = href.toLowerCase().includes('.pdf');
            data.isDownload = link.hasAttribute('download');
        }
        
        if (config.categorize) {
            if (data.isPDF) data.category = 'pdf';
            else if (data.isDownload) data.category = 'download';
            else if (data.isExternal) data.category = 'external';
            else if (href.startsWith('mailto:')) data.category = 'email';
            else if (href.startsWith('tel:')) data.category = 'phone';
            else if (href.startsWith('#')) data.category = 'anchor';
            else data.category = 'internal';
        }
        
        return data;
    });
    
    if (config.unique) {
        const seen = new Set();
        return links.filter(link => {
            if (seen.has(link.href)) return false;
            seen.add(link.href);
            return true;
        });
    }
    
    return links;
}
```

### `data/extract_tables.js`
```javascript
// Extract table data with headers
function extractTables() {
    const tables = Array.from(document.querySelectorAll('table')).map((table, index) => {
        const headers = Array.from(table.querySelectorAll('th')).map(th => th.textContent.trim());
        
        const rows = Array.from(table.querySelectorAll('tbody tr')).map(tr => {
            const cells = Array.from(tr.querySelectorAll('td'));
            
            if (headers.length > 0) {
                // Return as object with headers as keys
                const row = {};
                cells.forEach((cell, i) => {
                    const header = headers[i] || `col_${i}`;
                    row[header] = cell.textContent.trim();
                });
                return row;
            } else {
                // Return as array
                return cells.map(cell => cell.textContent.trim());
            }
        });
        
        return {
            index,
            headers,
            rows,
            rowCount: rows.length,
            columnCount: headers.length || (rows[0] ? rows[0].length : 0),
            caption: table.querySelector('caption')?.textContent.trim() || null
        };
    });
    
    return tables;
}
```

## 6. Debug Utilities

### `debug/console_logger.js`
```javascript
// Enhanced console logger with styling
const logger = {
    _style: {
        info: 'color: #2196F3; font-weight: bold;',
        success: 'color: #4CAF50; font-weight: bold;',
        warning: 'color: #FF9800; font-weight: bold;',
        error: 'color: #F44336; font-weight: bold;',
        debug: 'color: #9C27B0; font-weight: bold;'
    },
    
    _log(level, message, data = null) {
        const timestamp = new Date().toISOString();
        const prefix = `[${timestamp}] [${level.toUpperCase()}]`;
        
        if (data) {
            console.log(`%c${prefix} ${message}`, this._style[level], data);
        } else {
            console.log(`%c${prefix} ${message}`, this._style[level]);
        }
        
        // Store in session storage for retrieval
        const logs = JSON.parse(sessionStorage.getItem('scitex_logs') || '[]');
        logs.push({ timestamp, level, message, data });
        if (logs.length > 100) logs.shift(); // Keep last 100 logs
        sessionStorage.setItem('scitex_logs', JSON.stringify(logs));
    },
    
    info: function(message, data) { this._log('info', message, data); },
    success: function(message, data) { this._log('success', message, data); },
    warning: function(message, data) { this._log('warning', message, data); },
    error: function(message, data) { this._log('error', message, data); },
    debug: function(message, data) { this._log('debug', message, data); },
    
    getLogs: () => JSON.parse(sessionStorage.getItem('scitex_logs') || '[]'),
    clearLogs: () => sessionStorage.removeItem('scitex_logs')
};
```

### `debug/performance_monitor.js`
```javascript
// Monitor page performance
function monitorPerformance() {
    const metrics = {
        navigation: performance.timing,
        memory: performance.memory || {},
        resources: performance.getEntriesByType('resource').map(r => ({
            name: r.name,
            type: r.initiatorType,
            duration: r.duration,
            size: r.transferSize || 0
        })),
        
        // Calculate key metrics
        pageLoadTime: performance.timing.loadEventEnd - performance.timing.navigationStart,
        domContentLoaded: performance.timing.domContentLoadedEventEnd - performance.timing.navigationStart,
        firstPaint: performance.getEntriesByType('paint')[0]?.startTime || null,
        
        // Resource summary
        resourceSummary: {
            total: performance.getEntriesByType('resource').length,
            images: performance.getEntriesByType('resource').filter(r => r.initiatorType === 'img').length,
            scripts: performance.getEntriesByType('resource').filter(r => r.initiatorType === 'script').length,
            stylesheets: performance.getEntriesByType('resource').filter(r => r.initiatorType === 'link').length,
            totalSize: performance.getEntriesByType('resource').reduce((sum, r) => sum + (r.transferSize || 0), 0)
        }
    };
    
    // Add memory info if available
    if (performance.memory) {
        metrics.memory = {
            usedJSHeapSize: (performance.memory.usedJSHeapSize / 1048576).toFixed(2) + ' MB',
            totalJSHeapSize: (performance.memory.totalJSHeapSize / 1048576).toFixed(2) + ' MB',
            jsHeapSizeLimit: (performance.memory.jsHeapSizeLimit / 1048576).toFixed(2) + ' MB'
        };
    }
    
    return metrics;
}
```

## Python Integration Example

```python
# utils/js_loader.py
from pathlib import Path
import json

class JSLoader:
    def __init__(self, js_dir: Path):
        self.js_dir = js_dir
        self._cache = {}
    
    def load(self, script_path: str) -> str:
        """Load JavaScript file with caching."""
        if script_path not in self._cache:
            full_path = self.js_dir / script_path
            with open(full_path, 'r') as f:
                self._cache[script_path] = f.read()
        return self._cache[script_path]
    
    def load_with_params(self, script_path: str, params: dict) -> str:
        """Load JS and inject parameters."""
        script = self.load(script_path)
        params_json = json.dumps(params)
        return f"(function() {{ const params = {params_json}; {script} }})()"

# Usage in your existing code
async def show_popup_message_async(page, message: str, duration_ms: int = 5000):
    js_loader = JSLoader(Path(__file__).parent / "js")
    script = js_loader.load_with_params(
        "ui/popup_message.js",
        {"message": message, "duration": duration_ms}
    )
    await page.evaluate(script)
```

## Benefits of This Approach

1. **Separation of Concerns**: JavaScript logic is separate from Python code
2. **Reusability**: Scripts can be used across different Python functions
3. **Maintainability**: Easier to update and test JavaScript independently
4. **Type Safety**: Can add TypeScript compilation if needed
5. **Performance**: Scripts can be cached and minified
6. **Debugging**: Easier to debug JavaScript in browser console
7. **Version Control**: Better diff visibility for JavaScript changes

<!-- EOF -->