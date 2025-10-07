<!-- ---
!-- Timestamp: 2025-08-22 02:32:47
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/browser/suggestions.md
!-- --- -->

# SciTeX JavaScript Module Structure

## Complete Directory Structure

```
js/
├── config/
│   ├── index.js
│   ├── constants.js
│   └── selectors.js
├── core/
│   ├── index.js
│   ├── browser_context.js
│   ├── page_manager.js
│   └── script_injector.js
├── index.js
├── integrations/
│   ├── crawl4ai/
│   │   ├── index.js
│   │   └── crawler.js
│   ├── puppeteer/
│   │   ├── index.js
│   │   └── page_utils.js
│   └── zotero/
│       ├── index.js
│       ├── zotero_environment.js
│       └── zotero_translator_executor.js
├── utils/
│   ├── auth/
│   │   ├── index.js
│   │   ├── cookie_manager.js
│   │   └── session_handler.js
│   ├── dom/
│   │   ├── index.js
│   │   ├── element_selector.js
│   │   ├── element_highlighter.js
│   │   ├── click_handler.js
│   │   ├── fill_handler.js
│   │   ├── scroll_manager.js
│   │   └── wait_for_element.js
│   ├── network/
│   │   ├── index.js
│   │   ├── request_interceptor.js
│   │   ├── redirect_monitor.js
│   │   └── download_monitor.js
│   └── popup/
│       ├── index.js
│       ├── popup_detector.js
│       ├── popup_blocker.js
│       └── message_display.js
└── vendor/
    ├── pdf.js
    └── mathpix.js
```

## 1. Root Index (`js/index.js`)

```javascript
/**
 * SciTeX Browser JavaScript Library
 * Main entry point for all browser automation scripts
 */

// Core modules
export * as core from './core/index.js';
export * as config from './config/index.js';

// Utilities
export * as utils from './utils/index.js';

// Integrations
export * as integrations from './integrations/index.js';

// Version info
export const VERSION = '1.0.0';
export const BUILD_DATE = new Date().toISOString();

// Initialize global namespace if needed
if (typeof window !== 'undefined' && !window.SciTeX) {
    window.SciTeX = {
        version: VERSION,
        loaded: true,
        modules: {}
    };
}
```

## 2. Config (`js/config/`)

### `config/index.js`
```javascript
export { CONSTANTS } from './constants.js';
export { SELECTORS } from './selectors.js';

export const CONFIG = {
    debug: false,
    timeout: 30000,
    retryAttempts: 3,
    animation: {
        duration: 300,
        easing: 'ease-in-out'
    }
};
```

### `config/constants.js`
```javascript
export const CONSTANTS = {
    // PDF detection patterns
    PDF_PATTERNS: {
        URL: /\.pdf($|\?|#)/i,
        CONTENT_TYPE: 'application/pdf',
        VIEWERS: ['chrome-pdf-viewer', 'pdf.js', 'adobe']
    },
    
    // Scholar sites
    SCHOLAR_DOMAINS: [
        'scholar.google.com',
        'arxiv.org',
        'pubmed.ncbi.nlm.nih.gov',
        'ieeexplore.ieee.org',
        'dl.acm.org'
    ],
    
    // Popup patterns
    POPUP_INDICATORS: [
        'modal',
        'overlay',
        'popup',
        'dialog',
        'lightbox'
    ],
    
    // Network
    REDIRECT_CODES: [301, 302, 303, 307, 308],
    MAX_REDIRECTS: 10
};
```

### `config/selectors.js`
```javascript
export const SELECTORS = {
    // PDF viewers
    PDF: {
        CHROME_VIEWER: 'embed[type="application/pdf"]',
        PDFJS_VIEWER: '#viewer.pdfViewer',
        IFRAME_PDF: 'iframe[src*=".pdf"]',
        OBJECT_PDF: 'object[type="application/pdf"]'
    },
    
    // Scholar sites
    SCHOLAR: {
        GOOGLE: {
            RESULT: '.gs_r.gs_or.gs_scl',
            TITLE: '.gs_rt a',
            PDF_LINK: '.gs_or_ggsm a',
            CITE_BUTTON: '.gs_or_cit'
        },
        ARXIV: {
            PDF_LINK: '.download-pdf',
            ABSTRACT: '.abstract'
        }
    },
    
    // Common UI elements
    UI: {
        MODAL: '[role="dialog"], .modal, .popup',
        CLOSE_BUTTON: '[aria-label="Close"], .close, .modal-close',
        OVERLAY: '.overlay, .backdrop, .modal-backdrop'
    }
};
```

## 3. Core (`js/core/`)

### `core/index.js`
```javascript
export { BrowserContext } from './browser_context.js';
export { PageManager } from './page_manager.js';
export { ScriptInjector } from './script_injector.js';
```

### `core/browser_context.js`
```javascript
/**
 * Manages browser context and environment detection
 */
export class BrowserContext {
    constructor() {
        this.info = this._detectBrowser();
        this.features = this._detectFeatures();
    }
    
    _detectBrowser() {
        const ua = navigator.userAgent;
        return {
            isChrome: /Chrome/.test(ua) && !/Chromium/.test(ua),
            isFirefox: /Firefox/.test(ua),
            isSafari: /Safari/.test(ua) && !/Chrome/.test(ua),
            isEdge: /Edg/.test(ua),
            version: this._getBrowserVersion(ua),
            platform: navigator.platform,
            isMobile: /Mobile|Android|iPhone/.test(ua)
        };
    }
    
    _detectFeatures() {
        return {
            hasServiceWorker: 'serviceWorker' in navigator,
            hasWebGL: this._checkWebGL(),
            hasPDF: navigator.mimeTypes['application/pdf'] !== undefined,
            hasLocalStorage: this._checkLocalStorage(),
            hasIndexedDB: 'indexedDB' in window
        };
    }
    
    _getBrowserVersion(ua) {
        const match = ua.match(/(Chrome|Firefox|Safari|Edg)\/(\d+)/);
        return match ? parseInt(match[2]) : null;
    }
    
    _checkWebGL() {
        try {
            const canvas = document.createElement('canvas');
            return !!(canvas.getContext('webgl') || canvas.getContext('experimental-webgl'));
        } catch (e) {
            return false;
        }
    }
    
    _checkLocalStorage() {
        try {
            const test = '__test__';
            localStorage.setItem(test, test);
            localStorage.removeItem(test);
            return true;
        } catch (e) {
            return false;
        }
    }
    
    isPDFViewerAvailable() {
        return this.features.hasPDF || this.info.isChrome || this.info.isFirefox;
    }
}
```

### `core/page_manager.js`
```javascript
/**
 * Manages page state and lifecycle
 */
export class PageManager {
    constructor() {
        this.state = {
            url: window.location.href,
            title: document.title,
            readyState: document.readyState,
            visibility: document.visibilityState
        };
        
        this._setupListeners();
    }
    
    _setupListeners() {
        // Track page state changes
        document.addEventListener('readystatechange', () => {
            this.state.readyState = document.readyState;
            this._onStateChange();
        });
        
        document.addEventListener('visibilitychange', () => {
            this.state.visibility = document.visibilityState;
        });
        
        // Track navigation
        window.addEventListener('popstate', () => {
            this.state.url = window.location.href;
            this._onNavigation();
        });
    }
    
    _onStateChange() {
        if (window.SciTeX?.debug) {
            console.log('[PageManager] State changed:', this.state.readyState);
        }
    }
    
    _onNavigation() {
        if (window.SciTeX?.debug) {
            console.log('[PageManager] Navigation:', this.state.url);
        }
    }
    
    waitForReady() {
        return new Promise(resolve => {
            if (document.readyState === 'complete') {
                resolve();
            } else {
                window.addEventListener('load', resolve, { once: true });
            }
        });
    }
    
    getMetadata() {
        const meta = {};
        document.querySelectorAll('meta').forEach(tag => {
            const name = tag.getAttribute('name') || tag.getAttribute('property');
            if (name) {
                meta[name] = tag.getAttribute('content');
            }
        });
        return meta;
    }
}
```

### `core/script_injector.js`
```javascript
/**
 * Handles dynamic script injection and execution
 */
export class ScriptInjector {
    constructor() {
        this.injected = new Set();
    }
    
    inject(code, options = {}) {
        const defaults = {
            async: false,
            defer: false,
            type: 'text/javascript',
            id: null
        };
        
        const config = { ...defaults, ...options };
        
        // Check if already injected
        if (config.id && this.injected.has(config.id)) {
            return Promise.resolve(false);
        }
        
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            
            if (config.id) {
                script.id = config.id;
                this.injected.add(config.id);
            }
            
            script.type = config.type;
            script.async = config.async;
            script.defer = config.defer;
            
            script.onload = () => resolve(true);
            script.onerror = reject;
            
            if (config.src) {
                script.src = config.src;
            } else {
                script.textContent = code;
            }
            
            (document.head || document.documentElement).appendChild(script);
            
            // For inline scripts, resolve immediately
            if (!config.src) {
                resolve(true);
            }
        });
    }
    
    injectCSS(styles, id = null) {
        if (id && document.getElementById(id)) {
            return false;
        }
        
        const style = document.createElement('style');
        if (id) style.id = id;
        style.textContent = styles;
        (document.head || document.documentElement).appendChild(style);
        
        return true;
    }
}
```

## 4. Utils - DOM (`js/utils/dom/`)

### `utils/dom/index.js`
```javascript
export { ElementSelector } from './element_selector.js';
export { ElementHighlighter } from './element_highlighter.js';
export { ClickHandler } from './click_handler.js';
export { FillHandler } from './fill_handler.js';
export { ScrollManager } from './scroll_manager.js';
export { waitForElement } from './wait_for_element.js';
```

### `utils/dom/element_highlighter.js`
```javascript
/**
 * Advanced element highlighting with animations
 */
export class ElementHighlighter {
    constructor() {
        this.highlights = new Map();
        this._injectStyles();
    }
    
    _injectStyles() {
        const styles = `
            .scitex-highlight {
                position: absolute;
                pointer-events: none;
                z-index: 999999;
                transition: all 0.3s ease-in-out;
            }
            
            .scitex-highlight-pulse {
                animation: scitex-pulse 1s infinite;
            }
            
            @keyframes scitex-pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }
            
            .scitex-highlight-fade-out {
                animation: scitex-fade-out 0.3s forwards;
            }
            
            @keyframes scitex-fade-out {
                to { opacity: 0; transform: scale(1.1); }
            }
        `;
        
        if (!document.getElementById('scitex-highlight-styles')) {
            const style = document.createElement('style');
            style.id = 'scitex-highlight-styles';
            style.textContent = styles;
            document.head.appendChild(style);
        }
    }
    
    highlight(element, options = {}) {
        const defaults = {
            color: 'red',
            width: 3,
            padding: 5,
            duration: 2000,
            pulse: true,
            scrollIntoView: true,
            backgroundColor: 'rgba(255, 0, 0, 0.1)'
        };
        
        const config = { ...defaults, ...options };
        
        if (!element) return null;
        
        // Remove existing highlight for this element
        this.remove(element);
        
        const rect = element.getBoundingClientRect();
        const scrollTop = window.pageYOffset;
        const scrollLeft = window.pageXOffset;
        
        const overlay = document.createElement('div');
        overlay.className = 'scitex-highlight';
        if (config.pulse) {
            overlay.classList.add('scitex-highlight-pulse');
        }
        
        overlay.style.cssText = `
            top: ${rect.top + scrollTop - config.padding}px;
            left: ${rect.left + scrollLeft - config.padding}px;
            width: ${rect.width + config.padding * 2}px;
            height: ${rect.height + config.padding * 2}px;
            border: ${config.width}px solid ${config.color};
            background-color: ${config.backgroundColor};
            box-shadow: 0 0 20px ${config.color};
        `;
        
        document.body.appendChild(overlay);
        this.highlights.set(element, overlay);
        
        if (config.scrollIntoView) {
            element.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
        
        if (config.duration > 0) {
            setTimeout(() => this.remove(element), config.duration);
        }
        
        return overlay;
    }
    
    remove(element) {
        const overlay = this.highlights.get(element);
        if (overlay) {
            overlay.classList.add('scitex-highlight-fade-out');
            setTimeout(() => {
                overlay.remove();
                this.highlights.delete(element);
            }, 300);
        }
    }
    
    removeAll() {
        this.highlights.forEach((overlay, element) => this.remove(element));
    }
}
```

### `utils/dom/click_handler.js`
```javascript
/**
 * Robust click handling with multiple fallback strategies
 */
export class ClickHandler {
    static async click(element, options = {}) {
        const defaults = {
            retryAttempts: 3,
            retryDelay: 100,
            highlight: true,
            force: false
        };
        
        const config = { ...defaults, ...options };
        
        if (!element) {
            throw new Error('Element not found');
        }
        
        // Highlight before clicking
        if (config.highlight && window.SciTeX?.highlighter) {
            window.SciTeX.highlighter.highlight(element, { duration: 1000 });
        }
        
        const strategies = [
            this._standardClick,
            this._mouseEventClick,
            this._focusClick,
            this._jqueryClick,
            this._forceClick
        ];
        
        for (let attempt = 0; attempt < config.retryAttempts; attempt++) {
            for (const strategy of strategies) {
                try {
                    const result = await strategy(element, config);
                    if (result) {
                        return { success: true, method: strategy.name, attempt };
                    }
                } catch (e) {
                    console.debug(`Click strategy ${strategy.name} failed:`, e);
                }
            }
            
            if (attempt < config.retryAttempts - 1) {
                await this._delay(config.retryDelay);
            }
        }
        
        throw new Error('All click methods failed');
    }
    
    static _standardClick(element) {
        element.click();
        return true;
    }
    
    static _mouseEventClick(element) {
        const events = ['mousedown', 'mouseup', 'click'];
        events.forEach(type => {
            const event = new MouseEvent(type, {
                view: window,
                bubbles: true,
                cancelable: true,
                buttons: 1
            });
            element.dispatchEvent(event);
        });
        return true;
    }
    
    static _focusClick(element) {
        element.focus();
        element.click();
        return true;
    }
    
    static _jqueryClick(element) {
        if (window.jQuery) {
            jQuery(element).trigger('click');
            return true;
        }
        return false;
    }
    
    static _forceClick(element) {
        const rect = element.getBoundingClientRect();
        const x = rect.left + rect.width / 2;
        const y = rect.top + rect.height / 2;
        
        const clickEvent = new MouseEvent('click', {
            view: window,
            bubbles: true,
            cancelable: true,
            clientX: x,
            clientY: y
        });
        
        element.dispatchEvent(clickEvent);
        return true;
    }
    
    static _delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}
```

### `utils/dom/scroll_manager.js`
```javascript
/**
 * Advanced scrolling utilities
 */
export class ScrollManager {
    constructor() {
        this.isScrolling = false;
        this.scrollEndTimer = null;
    }
    
    scrollToElement(element, options = {}) {
        const defaults = {
            behavior: 'smooth',
            block: 'center',
            inline: 'nearest',
            offsetY: 0,
            duration: 500
        };
        
        const config = { ...defaults, ...options };
        
        if (config.offsetY !== 0) {
            const y = element.getBoundingClientRect().top + window.pageYOffset + config.offsetY;
            this._smoothScrollTo(y, config.duration);
        } else {
            element.scrollIntoView({
                behavior: config.behavior,
                block: config.block,
                inline: config.inline
            });
        }
    }
    
    _smoothScrollTo(targetY, duration) {
        const startY = window.pageYOffset;
        const difference = targetY - startY;
        const startTime = performance.now();
        
        const step = (currentTime) => {
            const progress = Math.min((currentTime - startTime) / duration, 1);
            const easeProgress = this._easeInOutCubic(progress);
            
            window.scrollTo(0, startY + difference * easeProgress);
            
            if (progress < 1) {
                requestAnimationFrame(step);
            }
        };
        
        requestAnimationFrame(step);
    }
    
    _easeInOutCubic(t) {
        return t < 0.5 
            ? 4 * t * t * t 
            : 1 - Math.pow(-2 * t + 2, 3) / 2;
    }
    
    scrollByPages(pages) {
        const viewportHeight = window.innerHeight;
        window.scrollBy({
            top: viewportHeight * pages,
            behavior: 'smooth'
        });
    }
    
    getScrollPercentage() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const scrollHeight = document.documentElement.scrollHeight;
        const clientHeight = document.documentElement.clientHeight;
        
        if (scrollHeight === clientHeight) return 100;
        
        return Math.round((scrollTop / (scrollHeight - clientHeight)) * 100);
    }
    
    isElementInViewport(element, threshold = 0) {
        const rect = element.getBoundingClientRect();
        const windowHeight = window.innerHeight || document.documentElement.clientHeight;
        const windowWidth = window.innerWidth || document.documentElement.clientWidth;
        
        return (
            rect.top >= -threshold &&
            rect.left >= -threshold &&
            rect.bottom <= windowHeight + threshold &&
            rect.right <= windowWidth + threshold
        );
    }
    
    waitForScrollEnd() {
        return new Promise(resolve => {
            let scrollTimer;
            
            const handleScroll = () => {
                clearTimeout(scrollTimer);
                scrollTimer = setTimeout(() => {
                    window.removeEventListener('scroll', handleScroll);
                    resolve();
                }, 150);
            };
            
            window.addEventListener('scroll', handleScroll);
            handleScroll(); // Start timer immediately
        });
    }
}
```

## 5. Utils - Network (`js/utils/network/`)

### `utils/network/redirect_monitor.js`
```javascript
/**
 * Monitor and track redirect chains
 */
export class RedirectMonitor {
    constructor() {
        this.redirectChain = [];
        this.isMonitoring = false;
        this.maxRedirects = 10;
    }
    
    start(options = {}) {
        if (this.isMonitoring) return;
        
        this.isMonitoring = true;
        this.redirectChain = [{
            url: window.location.href,
            timestamp: Date.now(),
            type: 'initial'
        }];
        
        // Monitor navigation timing
        if (performance.navigation) {
            this._checkNavigationType();
        }
        
        // Monitor URL changes
        this._monitorUrlChanges();
        
        return this;
    }
    
    _checkNavigationType() {
        const navType = performance.navigation.type;
        const types = ['navigate', 'reload', 'back_forward', 'reserved'];
        
        this.redirectChain[0].navigationType = types[navType] || 'unknown';
        this.redirectChain[0].redirectCount = performance.navigation.redirectCount;
    }
    
    _monitorUrlChanges() {
        // Store original pushState and replaceState
        const originalPushState = history.pushState;
        const originalReplaceState = history.replaceState;
        
        // Override pushState
        history.pushState = (...args) => {
            originalPushState.apply(history, args);
            this._recordRedirect('pushState');
        };
        
        // Override replaceState
        history.replaceState = (...args) => {
            originalReplaceState.apply(history, args);
            this._recordRedirect('replaceState');
        };
        
        // Listen for popstate
        window.addEventListener('popstate', () => {
            this._recordRedirect('popstate');
        });
    }
    
    _recordRedirect(type) {
        this.redirectChain.push({
            url: window.location.href,
            timestamp: Date.now(),
            type: type
        });
        
        if (this.redirectChain.length > this.maxRedirects) {
            console.warn('Max redirects reached');
        }
    }
    
    getChain() {
        return this.redirectChain.map((item, index) => ({
            ...item,
            step: index,
            duration: index > 0 
                ? item.timestamp - this.redirectChain[index - 1].timestamp 
                : 0
        }));
    }
    
    stop() {
        this.isMonitoring = false;
        // Note: Can't restore original functions without keeping references
        return this.getChain();
    }
}
```

### `utils/network/download_monitor.js`
```javascript
/**
 * Monitor file downloads
 */
export class DownloadMonitor {
    constructor() {
        this.downloads = new Map();
        this.listeners = new Map();
    }
    
    monitor(linkElement, options = {}) {
        const defaults = {
            onStart: null,
            onProgress: null,
            onComplete: null,
            onError: null,
            timeout: 120000
        };
        
        const config = { ...defaults, ...options };
        const downloadId = Date.now().toString();
        
        // Store download info
        this.downloads.set(downloadId, {
            url: linkElement.href,
            fileName: this._extractFileName(linkElement),
            startTime: null,
            endTime: null,
            status: 'pending'
        });
        
        // Add click listener
        const clickHandler = (e) => {
            this._handleDownloadStart(downloadId, config);
            
            // For PDF links, monitor via fetch
            if (linkElement.href.toLowerCase().includes('.pdf')) {
                e.preventDefault();
                this._fetchDownload(linkElement.href, downloadId, config);
            }
        };
        
        linkElement.addEventListener('click', clickHandler);
        this.listeners.set(downloadId, { element: linkElement, handler: clickHandler });
        
        return downloadId;
    }
    
    _extractFileName(element) {
        // Try download attribute
        if (element.download) return element.download;
        
        // Extract from URL
        const url = new URL(element.href);
        const pathname = url.pathname;
        const fileName = pathname.substring(pathname.lastIndexOf('/') + 1);
        
        return fileName || 'download';
    }
    
    _handleDownloadStart(downloadId, config) {
        const download = this.downloads.get(downloadId);
        download.startTime = Date.now();
        download.status = 'downloading';
        
        if (config.onStart) {
            config.onStart(download);
        }
    }
    
    async _fetchDownload(url, downloadId, config) {
        const download = this.downloads.get(downloadId);
        
        try {
            const response = await fetch(url);
            const reader = response.body.getReader();
            const contentLength = +response.headers.get('Content-Length');
            
            let receivedLength = 0;
            const chunks = [];
            
            while(true) {
                const {done, value} = await reader.read();
                
                if (done) break;
                
                chunks.push(value);
                receivedLength += value.length;
                
                if (config.onProgress && contentLength) {
                    const progress = (receivedLength / contentLength) * 100;
                    config.onProgress({
                        ...download,
                        progress: Math.round(progress),
                        received: receivedLength,
                        total: contentLength
                    });
                }
            }
            
            // Create blob and download
            const blob = new Blob(chunks);
            const blobUrl = URL.createObjectURL(blob);
            
            const a = document.createElement('a');
            a.href = blobUrl;
            a.download = download.fileName;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(blobUrl);
            
            // Update status
            download.endTime = Date.now();
            download.status = 'complete';
            download.size = receivedLength;
            
            if (config.onComplete) {
                config.onComplete(download);
            }
            
        } catch (error) {
            download.status = 'error';
            download.error = error.message;
            
            if (config.onError) {
                config.onError(download);
            }
        }
    }
    
    cleanup(downloadId) {
        const listener = this.listeners.get(downloadId);
        if (listener) {
            listener.element.removeEventListener('click', listener.handler);
            this.listeners.delete(downloadId);
        }
        this.downloads.delete(downloadId);
    }
}
```

## 6. Utils - Popup (`js/utils/popup/`)

### `utils/popup/message_display.js`
```javascript
/**
 * Display popup messages with queue management
 */
export class MessageDisplay {
    constructor() {
        this.queue = [];
        this.currentMessage = null;
        this.container = null;
        this._initContainer();
    }
    
    _initContainer() {
        this.container = document.createElement('div');
        this.container.id = 'scitex-message-container';
        this.container.style.cssText = `
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 10000;
            pointer-events: none;
        `;
        document.body.appendChild(this.container);
    }
    
    show(message, options = {}) {
        const defaults = {
            duration: 3000,
            type: 'info', // info, success, warning, error
            position: 'top',
            animate: true,
            queue: true
        };
        
        const config = { ...defaults, ...options };
        
        const messageObj = {
            id: Date.now().toString(),
            message,
            config
        };
        
        if (config.queue && this.currentMessage) {
            this.queue.push(messageObj);
        } else {
            this._displayMessage(messageObj);
        }
        
        return messageObj.id;
    }
    
    _displayMessage(messageObj) {
        this.currentMessage = messageObj;
        
        const element = document.createElement('div');
        element.className = 'scitex-message';
        element.dataset.id = messageObj.id;
        
        const colors = {
            info: '#2196F3',
            success: '#4CAF50',
            warning: '#FF9800',
            error: '#F44336'
        };
        
        element.style.cssText = `
            background: ${colors[messageObj.config.type]};
            color: white;
            padding: 12px 20px;
            border-radius: 6px;
            margin-bottom: 10px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: 14px;
            box-shadow: 0 3px 10px rgba(0,0,0,0.2);
            pointer-events: auto;
            cursor: pointer;
            ${messageObj.config.animate ? `
                animation: slideInDown 0.3s ease-out;
            ` : ''}
        `;
        
        element.textContent = messageObj.message;
        
        // Click to dismiss
        element.addEventListener('click', () => this._removeMessage(element));
        
        this.container.appendChild(element);
        
        // Auto remove
        if (messageObj.config.duration > 0) {
            setTimeout(() => this._removeMessage(element), messageObj.config.duration);
        }
    }
    
    _removeMessage(element) {
        element.style.animation = 'slideOutUp 0.3s ease-in';
        
        setTimeout(() => {
            element.remove();
            
            // Process queue
            if (this.queue.length > 0) {
                const next = this.queue.shift();
                this._displayMessage(next);
            } else {
                this.currentMessage = null;
            }
        }, 300);
    }
    
    clear() {
        this.queue = [];
        this.container.innerHTML = '';
        this.currentMessage = null;
    }
}

// Add required animations
if (!document.getElementById('scitex-message-animations')) {
    const style = document.createElement('style');
    style.id = 'scitex-message-animations';
    style.textContent = `
        @keyframes slideInDown {
            from {
                transform: translateY(-100%);
                opacity: 0;
            }
            to {
                transform: translateY(0);
                opacity: 1;
            }
        }
        
        @keyframes slideOutUp {
            to {
                transform: translateY(-100%);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
}
```

## 7. Python Integration

### `js_loader.py`
```python
"""JavaScript module loader for SciTeX"""

from pathlib import Path
import json
from typing import Dict, Any, Optional
import hashlib

class JSModuleLoader:
    """Load and manage JavaScript modules"""
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir / "js"
        self._cache = {}
        self._module_map = self._build_module_map()
    
    def _build_module_map(self) -> Dict[str, Path]:
        """Build a map of module names to file paths"""
        module_map = {}
        
        for js_file in self.base_dir.rglob("*.js"):
            # Create module name from path
            relative_path = js_file.relative_to(self.base_dir)
            module_name = str(relative_path).replace("/", ".").replace(".js", "")
            module_map[module_name] = js_file
        
        return module_map
    
    def load(self, module: str, minify: bool = False) -> str:
        """Load a JavaScript module"""
        cache_key = f"{module}:{minify}"
        
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        if module not in self._module_map:
            raise ValueError(f"Module not found: {module}")
        
        with open(self._module_map[module], 'r') as f:
            content = f.read()
        
        if minify:
            content = self._minify(content)
        
        self._cache[cache_key] = content
        return content
    
    def load_bundle(self, modules: list, minify: bool = False) -> str:
        """Load multiple modules as a bundle"""
        bundle = []
        
        for module in modules:
            bundle.append(f"// Module: {module}")
            bundle.append(self.load(module, minify))
            bundle.append("")
        
        return "\n".join(bundle)
    
    def inject(self, module: str, params: Dict[str, Any] = None) -> str:
        """Load module and inject parameters"""
        script = self.load(module)
        
        if params:
            params_json = json.dumps(params)
            script = f"""
            (function() {{
                const params = {params_json};
                {script}
            }})();
            """
        
        return script
    
    def _minify(self, content: str) -> str:
        """Basic JavaScript minification"""
        # Remove comments
        import re
        content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        
        # Remove unnecessary whitespace
        content = re.sub(r'\s+', ' ', content)
        content = re.sub(r';\s*', ';', content)
        content = re.sub(r'{\s*', '{', content)
        content = re.sub(r'\s*}', '}', content)
        
        return content.strip()
    
    def get_hash(self, module: str) -> str:
        """Get hash of module content for cache busting"""
        content = self.load(module)
        return hashlib.md5(content.encode()).hexdigest()[:8]
```

### Usage Example
```python
from pathlib import Path
from playwright.async_api import Page

class BrowserUtils:
    def __init__(self):
        self.js = JSModuleLoader(Path(__file__).parent)
    
    async def highlight_element(self, page: Page, selector: str):
        """Highlight an element on the page"""
        # Load the highlighter module
        script = self.js.load("utils.dom.element_highlighter")
        
        # Execute on page
        await page.evaluate(f"""
            {script}
            const highlighter = new ElementHighlighter();
            const element = document.querySelector('{selector}');
            if (element) {{
                highlighter.highlight(element, {{
                    duration: 2000,
                    color: 'blue'
                }});
            }}
        """)
    
    async def show_message(self, page: Page, message: str, type: str = "info"):
        """Show a popup message"""
        script = self.js.inject("utils.popup.message_display", {
            "message": message,
            "type": type,
            "duration": 3000
        })
        await page.evaluate(script)
```

This structure provides:

1. **Modular organization** matching your existing structure
2. **Clear separation** between different types of utilities
3. **Reusable components** that can work independently
4. **Integration points** for Zotero, Puppeteer, and Crawl4AI
5. **Python integration** via the JSModuleLoader class
6. **Caching and optimization** capabilities
7. **Extensibility** for adding new modules

Each module is self-contained but can work together through the global `window.SciTeX` namespace when needed. The structure supports both browser-side execution and server-side bundling/minification.

<!-- EOF -->