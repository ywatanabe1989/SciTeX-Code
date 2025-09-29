// Zotero translator wrapper code
// This file contains the JavaScript code that sets up the Zotero environment
// and executes the translator code

async function executeZoteroTranslator(translatorCode, translatorLabel) {
    const urls = new Set();
    const items = [];

    console.log(`Starting translator: ${translatorLabel}`);

    // Setup minimal Zotero environment
    window.Zotero = {
        Item: function(type) {
            console.log(`Creating Zotero Item of type: ${type}`);
            this.itemType = type;
            this.attachments = [];
            this.url = null;
            this.DOI = null;
            this.complete = function() {
                console.log('Item completing with', this.attachments.length, 'attachments');
                console.log('Item URL:', this.url);
                console.log('Item DOI:', this.DOI);
                if (this.url) urls.add(this.url);
                if (this.DOI) urls.add('https://doi.org/' + this.DOI);
                // Extract URLs from attachments
                this.attachments.forEach(att => {
                    console.log('Attachment:', JSON.stringify(att));
                    if (att.url) {
                        // Only add PDF attachments (not HTML snapshots)
                        if (att.mimeType === 'application/pdf' || 
                            att.url.includes('.pdf') || 
                            att.url.includes('/pdf')) {
                            console.log('Adding PDF URL:', att.url);
                            urls.add(att.url);
                        }
                    }
                });
                items.push(this);
            };
        },
        loadTranslator: function(type) {
            console.log('Loading translator:', type);
            return {
                setTranslator: function(id) { 
                    console.log('Setting translator:', id);
                },
                setDocument: function(doc) {},
                setHandler: function(event, handler) {
                    console.log('Setting handler for:', event);
                    // If it's itemDone, we need to call it with mock items
                    if (event === 'done') {
                        // Call done handler immediately with mock items
                        setTimeout(() => handler([]), 10);
                    }
                },
                setString: function(str) {
                    console.log('Setting string for translation, length:', str?.length);
                },
                translate: function() {
                    console.log('Translating...');
                },
                getTranslators: function() { return []; }
            };
        },
        Utilities: {
            xpath: function(element, xpath) {
                const doc = element.ownerDocument || element;
                const result = doc.evaluate(xpath, element, null, XPathResult.ANY_TYPE, null);
                const nodes = [];
                let node;
                while (node = result.iterateNext()) {
                    nodes.push(node);
                }
                return nodes;
            },
            xpathText: function(element, xpath) {
                const nodes = this.xpath(element, xpath);
                return nodes.length ? nodes[0].textContent.trim() : null;
            },
            trimInternal: function(str) {
                return str ? str.trim().replace(/\s+/g, ' ') : '';
            },
            cleanAuthor: function() { return {}; },
            strToISO: function(str) { return str; },
            processDocuments: function() {},
            doGet: async function(url) {
                // Mock doGet - just return empty response
                return '';
            },
            // attr is commonly used in translators
            HTTP: {
                request: function() {}
            }
        },
        debug: function() {},
        done: function() {}
    };

    window.ZU = window.Zotero.Utilities;
    window.Z = window.Zotero;
    
    // Add requestDocument function that ScienceDirect translator needs
    window.requestDocument = async function(url) {
        // For ScienceDirect, just return the current document
        // In a real Zotero context, this would fetch a new page
        return document;
    };
    
    // Add requestText function that ScienceDirect translator needs for fetching RIS data
    window.requestText = async function(url, callback, method, body, headers) {
        console.log('requestText called with:', url);
        
        // Make the URL absolute if it's relative
        if (url.startsWith('/')) {
            url = window.location.origin + url;
        }
        
        try {
            // Use fetch to actually get the RIS data from ScienceDirect
            const response = await fetch(url, {
                method: method || 'GET',
                body: body,
                headers: headers || {},
                credentials: 'include'  // Include cookies for authentication
            });
            
            const text = await response.text();
            console.log('requestText got response, length:', text.length);
            
            if (callback) {
                callback(text, {status: response.status});
            }
            return text;
        } catch (error) {
            console.error('requestText error:', error);
            if (callback) {
                callback('', {status: 500});
            }
            return '';
        }
    };
    
    // Add attr helper function used by many translators
    window.attr = function(doc, selector, attribute) {
        const element = doc.querySelector(selector);
        return element ? element.getAttribute(attribute) : null;
    };
    
    // Add text helper function
    window.text = function(doc, selector) {
        const element = doc.querySelector(selector);
        return element ? element.textContent.trim() : null;
    };

    let translatorError = null;
    
    try {
        // Execute the translator code
        eval(translatorCode);
        
        // Try to run detectWeb and doWeb if they exist
        if (typeof detectWeb === 'function') {
            console.log('Running detectWeb...');
            const itemType = detectWeb(document, window.location.href);
            console.log('detectWeb returned:', itemType);
            
            if (itemType && typeof doWeb === 'function') {
                console.log('Running doWeb...');
                // doWeb is async, so we need to await it
                await doWeb(document, window.location.href);
                console.log('doWeb completed');
                // Give it more time for async operations
                await new Promise(resolve => setTimeout(resolve, 500));
            } else if (!itemType) {
                console.log('detectWeb returned null/false - page type not recognized');
            }
        } else {
            console.log('detectWeb function not found in translator');
        }
    } catch (e) {
        translatorError = e.message;
        console.error('Translator execution error:', e);
    }
    
    const pdfUrls = Array.from(urls).filter(url_item =>
        url_item && (
            url_item.includes('.pdf') ||
            url_item.includes('/pdf/') ||
            url_item.includes('type=printable')
        )
    );

    return {
        success: !translatorError && pdfUrls.length > 0,
        translator: translatorLabel,
        urls: pdfUrls,
        itemCount: items.length,
        error: translatorError
    };
}