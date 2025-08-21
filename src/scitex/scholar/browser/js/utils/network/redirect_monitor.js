/**
 * Monitor and track redirect chains in the browser
 * Handles both HTTP redirects and client-side navigation
 */

class RedirectMonitor {
    constructor() {
        this.redirectChain = [];
        this.isMonitoring = false;
        this.maxRedirects = 30;
        this.callbacks = {
            onRedirect: null,
            onComplete: null,
            onError: null
        };
        this.startUrl = null;
        this.finalUrl = null;
    }
    
    start(options = {}) {
        if (this.isMonitoring) return;
        
        this.isMonitoring = true;
        this.maxRedirects = options.maxRedirects || 30;
        this.callbacks = { ...this.callbacks, ...options };
        
        this.redirectChain = [{
            url: window.location.href,
            timestamp: Date.now(),
            type: 'initial',
            method: 'start'
        }];
        
        this.startUrl = window.location.href;
        
        // Monitor navigation timing API
        if (performance.navigation) {
            this._checkNavigationType();
        }
        
        // Monitor URL changes
        this._monitorUrlChanges();
        
        // Monitor fetch/XHR for meta redirects
        this._monitorNetworkRedirects();
        
        return this;
    }
    
    _checkNavigationType() {
        const navType = performance.navigation.type;
        const types = ['navigate', 'reload', 'back_forward', 'reserved'];
        
        this.redirectChain[0].navigationType = types[navType] || 'unknown';
        this.redirectChain[0].redirectCount = performance.navigation.redirectCount;
        
        // Check for server-side redirects
        if (performance.navigation.redirectCount > 0) {
            console.log(`Detected ${performance.navigation.redirectCount} server-side redirects`);
        }
    }
    
    _monitorUrlChanges() {
        // Store original functions
        const originalPushState = history.pushState;
        const originalReplaceState = history.replaceState;
        
        // Override pushState
        history.pushState = (...args) => {
            originalPushState.apply(history, args);
            this._recordRedirect('pushState', window.location.href);
        };
        
        // Override replaceState  
        history.replaceState = (...args) => {
            originalReplaceState.apply(history, args);
            this._recordRedirect('replaceState', window.location.href);
        };
        
        // Listen for popstate
        window.addEventListener('popstate', () => {
            this._recordRedirect('popstate', window.location.href);
        });
        
        // Monitor hash changes
        window.addEventListener('hashchange', () => {
            this._recordRedirect('hashchange', window.location.href);
        });
        
        // Use MutationObserver for meta refresh detection
        this._observeMetaRefresh();
    }
    
    _observeMetaRefresh() {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList') {
                    mutation.addedNodes.forEach((node) => {
                        if (node.nodeName === 'META' && node.httpEquiv === 'refresh') {
                            const content = node.content;
                            const urlMatch = content.match(/url=(.+)/i);
                            if (urlMatch) {
                                console.log('Meta refresh detected:', urlMatch[1]);
                                this._recordRedirect('meta-refresh', urlMatch[1]);
                            }
                        }
                    });
                }
            });
        });
        
        observer.observe(document.head, {
            childList: true,
            subtree: true
        });
    }
    
    _monitorNetworkRedirects() {
        // Override fetch to detect redirects
        const originalFetch = window.fetch;
        window.fetch = async (...args) => {
            const response = await originalFetch(...args);
            
            // Check if response URL differs from request URL
            if (response.url && response.url !== args[0]) {
                this._recordRedirect('fetch-redirect', response.url);
            }
            
            return response;
        };
        
        // Monitor XMLHttpRequest
        const originalOpen = XMLHttpRequest.prototype.open;
        XMLHttpRequest.prototype.open = function(...args) {
            this.addEventListener('load', () => {
                if (this.responseURL && this.responseURL !== args[1]) {
                    this._recordRedirect('xhr-redirect', this.responseURL);
                }
            });
            return originalOpen.apply(this, args);
        };
    }
    
    _recordRedirect(type, url) {
        // Check if URL actually changed
        const lastUrl = this.redirectChain[this.redirectChain.length - 1].url;
        if (url === lastUrl) return;
        
        const redirectInfo = {
            url: url,
            timestamp: Date.now(),
            type: type,
            method: this._detectRedirectMethod(type),
            step: this.redirectChain.length,
            fromUrl: lastUrl
        };
        
        this.redirectChain.push(redirectInfo);
        
        console.log(`Redirect #${redirectInfo.step}: ${type} to ${url}`);
        
        // Call callback if provided
        if (this.callbacks.onRedirect) {
            this.callbacks.onRedirect(redirectInfo);
        }
        
        // Check if we've hit max redirects
        if (this.redirectChain.length > this.maxRedirects) {
            console.warn('Max redirects reached');
            if (this.callbacks.onError) {
                this.callbacks.onError({
                    error: 'MAX_REDIRECTS',
                    chain: this.getChain()
                });
            }
            this.stop();
        }
        
        // Check if we've reached a final article URL
        if (this._isFinalUrl(url)) {
            this.finalUrl = url;
            console.log('Final URL reached:', url);
            if (this.callbacks.onComplete) {
                setTimeout(() => {
                    this.callbacks.onComplete({
                        finalUrl: url,
                        chain: this.getChain()
                    });
                }, 1000); // Wait a bit for any final adjustments
            }
        }
    }
    
    _detectRedirectMethod(type) {
        const methodMap = {
            'pushState': 'client-side',
            'replaceState': 'client-side',
            'popstate': 'browser-navigation',
            'hashchange': 'hash-navigation',
            'meta-refresh': 'meta-tag',
            'fetch-redirect': 'http-redirect',
            'xhr-redirect': 'http-redirect'
        };
        return methodMap[type] || 'unknown';
    }
    
    _isFinalUrl(url) {
        // Check if URL looks like a final article page
        const articlePatterns = [
            '/science/article/',
            '/articles/',
            '/content/',
            '/full/',
            '/fulltext/',
            '/doi/full/',
            '/doi/abs/',
            '/doi/pdf/',
            '.pdf'
        ];
        
        const authPatterns = [
            'auth.',
            'login.',
            'signin.',
            'shibboleth',
            'openathens',
            '/authenticate',
            '/ShibAuth/'
        ];
        
        const urlLower = url.toLowerCase();
        
        // Not final if it's an auth URL
        for (const pattern of authPatterns) {
            if (urlLower.includes(pattern)) {
                return false;
            }
        }
        
        // Check for article patterns
        for (const pattern of articlePatterns) {
            if (urlLower.includes(pattern)) {
                return true;
            }
        }
        
        return false;
    }
    
    getChain() {
        return this.redirectChain.map((item, index) => ({
            ...item,
            duration: index > 0 
                ? item.timestamp - this.redirectChain[index - 1].timestamp 
                : 0,
            isAuth: this._isAuthUrl(item.url),
            isFinal: this._isFinalUrl(item.url)
        }));
    }
    
    _isAuthUrl(url) {
        const authPatterns = [
            'auth.',
            'login.',
            'signin.',
            'shibboleth',
            'openathens'
        ];
        const urlLower = url.toLowerCase();
        return authPatterns.some(pattern => urlLower.includes(pattern));
    }
    
    getCurrentUrl() {
        return window.location.href;
    }
    
    getTotalTime() {
        if (this.redirectChain.length < 2) return 0;
        const first = this.redirectChain[0].timestamp;
        const last = this.redirectChain[this.redirectChain.length - 1].timestamp;
        return last - first;
    }
    
    stop() {
        this.isMonitoring = false;
        const chain = this.getChain();
        
        console.log('Redirect monitoring stopped');
        console.log(`Total redirects: ${chain.length - 1}`);
        console.log(`Total time: ${this.getTotalTime()}ms`);
        console.log(`Final URL: ${this.getCurrentUrl()}`);
        
        return {
            startUrl: this.startUrl,
            finalUrl: this.getCurrentUrl(),
            redirectCount: chain.length - 1,
            totalTime: this.getTotalTime(),
            chain: chain
        };
    }
    
    // Wait for stable URL (no changes for X seconds)
    async waitForStableUrl(stabilityTime = 3000, maxWait = 30000) {
        const startTime = Date.now();
        let lastUrl = window.location.href;
        let stableStart = Date.now();
        
        return new Promise((resolve) => {
            const checkInterval = setInterval(() => {
                const currentUrl = window.location.href;
                const elapsed = Date.now() - startTime;
                
                if (currentUrl !== lastUrl) {
                    // URL changed, reset stability timer
                    lastUrl = currentUrl;
                    stableStart = Date.now();
                    this._recordRedirect('url-change', currentUrl);
                } else {
                    // Check if URL has been stable long enough
                    const stableTime = Date.now() - stableStart;
                    if (stableTime >= stabilityTime || this._isFinalUrl(currentUrl)) {
                        clearInterval(checkInterval);
                        resolve({
                            url: currentUrl,
                            stable: true,
                            totalTime: elapsed
                        });
                    }
                }
                
                // Check for timeout
                if (elapsed >= maxWait) {
                    clearInterval(checkInterval);
                    resolve({
                        url: currentUrl,
                        stable: false,
                        timedOut: true,
                        totalTime: elapsed
                    });
                }
            }, 500);
        });
    }
}

// Export for use in page.evaluate()
if (typeof module !== 'undefined' && module.exports) {
    module.exports = RedirectMonitor;
}