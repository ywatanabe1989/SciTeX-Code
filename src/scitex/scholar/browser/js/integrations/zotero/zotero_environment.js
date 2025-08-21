// Zotero translator environment setup
// This file provides a complete mock Zotero environment for running translators in the browser

async function setupZoteroEnvironment() {
    const items = [];
    const urls = new Set();
    
    // Complete Zotero mock environment
    window.Zotero = {
        Item: function(type) {
            this.itemType = type;
            this.attachments = [];
            this.url = null;
            this.DOI = null;
            this.title = null;
            this.creators = [];
            this.date = null;
            this.publicationTitle = null;
            this.volume = null;
            this.issue = null;
            this.pages = null;
            this.abstractNote = null;
            
            this.complete = function() {
                console.log(`Item complete: ${this.itemType}`, {
                    title: this.title,
                    url: this.url,
                    DOI: this.DOI,
                    attachments: this.attachments.length
                });
                
                // Collect URLs from the item
                if (this.url) urls.add(this.url);
                if (this.DOI) urls.add('https://doi.org/' + this.DOI);
                
                // Collect PDF URLs from attachments
                this.attachments.forEach(att => {
                    if (att.url && (att.mimeType === 'application/pdf' || 
                                   att.url.includes('.pdf') || 
                                   att.url.includes('/pdf'))) {
                        console.log('Adding PDF attachment:', att.url);
                        urls.add(att.url);
                    }
                });
                
                items.push(this);
            };
        },
        
        // RIS translator support
        loadTranslator: function(type) {
            console.log('Loading translator type:', type);
            
            const translator = {
                _handlers: {},
                _items: [],
                
                setTranslator: function(id) {
                    console.log('Setting translator ID:', id);
                    // RIS translator ID: 32d59d2d-b65a-4da4-b0a3-bdd3cfb979e7
                },
                
                setString: function(str) {
                    console.log('Setting string for translation, length:', str?.length);
                    this._string = str;
                },
                
                setHandler: function(event, handler) {
                    console.log('Setting handler for event:', event);
                    this._handlers[event] = handler;
                },
                
                translate: async function() {
                    console.log('Starting translation...');
                    
                    // Use setTimeout to make it async and avoid blocking
                    setTimeout(() => {
                        // Parse RIS format if we have a string
                        if (this._string && this._handlers.itemDone) {
                            const lines = this._string.split('\n');
                            let currentItem = null;
                            
                            for (const line of lines) {
                                const match = line.match(/^([A-Z][A-Z0-9])\s+-\s+(.*)$/);
                                if (match) {
                                    const [, tag, value] = match;
                                    
                                    // Start new item on TY tag
                                    if (tag === 'TY') {
                                        if (currentItem) {
                                            this._handlers.itemDone(translator, currentItem);
                                        }
                                        currentItem = new Zotero.Item('journalArticle');
                                    }
                                    
                                    if (currentItem) {
                                        // Map RIS tags to Zotero fields
                                        switch(tag) {
                                            case 'TI':
                                            case 'T1':
                                                currentItem.title = value;
                                                break;
                                            case 'AU':
                                                currentItem.creators.push({
                                                    firstName: '',
                                                    lastName: value,
                                                    creatorType: 'author'
                                                });
                                                break;
                                            case 'PY':
                                            case 'Y1':
                                                currentItem.date = value;
                                                break;
                                            case 'JO':
                                            case 'JF':
                                                currentItem.publicationTitle = value;
                                                break;
                                            case 'VL':
                                                currentItem.volume = value;
                                                break;
                                            case 'IS':
                                                currentItem.issue = value;
                                                break;
                                            case 'SP':
                                                currentItem.pages = value;
                                                break;
                                            case 'AB':
                                                currentItem.abstractNote = value;
                                                break;
                                            case 'DO':
                                                currentItem.DOI = value;
                                                break;
                                            case 'UR':
                                            case 'L1': // PDF URL in RIS
                                                if (value.includes('.pdf') || value.includes('/pdf')) {
                                                    currentItem.attachments.push({
                                                        url: value,
                                                        mimeType: 'application/pdf',
                                                        title: 'Full Text PDF'
                                                    });
                                                } else {
                                                    currentItem.url = value;
                                                }
                                                break;
                                        }
                                    }
                                }
                            }
                            
                            // Complete last item
                            if (currentItem) {
                                this._handlers.itemDone(translator, currentItem);
                            }
                        }
                        
                        // Call done handler
                        if (this._handlers.done) {
                            this._handlers.done(translator, this._items);
                        }
                    }, 100);
                },
                
                getTranslators: function() {
                    return [];
                }
            };
            
            return translator;
        },
        
        // Utilities
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
            
            cleanAuthor: function(author, type) {
                return author;
            },
            
            strToISO: function(str) {
                return str;
            },
            
            cleanISBN: function(isbn) {
                // Remove hyphens and spaces from ISBN
                return isbn ? isbn.replace(/[-\s]/g, '') : '';
            },
            
            cleanISSN: function(issn) {
                // Clean ISSN format
                return issn ? issn.replace(/[-\s]/g, '') : '';
            },
            
            processDocuments: function(urls, processor) {
                console.log('processDocuments called with:', urls);
            },
            
            doGet: async function(url) {
                console.log('doGet called with:', url);
                return '';
            },
            
            HTTP: {
                request: function() {}
            }
        },
        
        debug: function(msg) {
            console.log('[Zotero Debug]', msg);
        },
        
        done: function() {
            console.log('Zotero done');
        },
        
        selectItems: async function(items) {
            // In automated context, select all items
            return items;
        },
        
        getHiddenPref: function(pref) {
            // Return sensible defaults for preferences
            if (pref === 'attachSupplementary') return false;
            return null;
        }
    };
    
    // Shortcuts
    window.ZU = window.Zotero.Utilities;
    window.Z = window.Zotero;
    
    // Helper functions used by translators
    window.attr = function(doc, selector, attribute) {
        const element = doc.querySelector(selector);
        return element ? element.getAttribute(attribute) : null;
    };
    
    window.text = function(doc, selector) {
        const element = doc.querySelector(selector);
        return element ? element.textContent.trim() : null;
    };
    
    // The parseIntermediatePDFPage function used by ScienceDirect translator
    window.parseIntermediatePDFPage = async function(url) {
        console.log('parseIntermediatePDFPage called with:', url);
        
        // If already a PDF URL, return it
        if (url && url.includes('.pdf')) {
            return url;
        }
        
        try {
            // Fetch the intermediate page to find the redirect
            const response = await fetch(url, {
                credentials: 'include',
                redirect: 'manual'  // Don't follow redirects automatically
            });
            
            const text = await response.text();
            
            // Look for meta refresh
            const metaMatch = text.match(/<meta[^>]*http-equiv="refresh"[^>]*content="[^"]*;URL=([^"]+)"/i);
            if (metaMatch) {
                return metaMatch[1];
            }
            
            // Look for redirect link
            const linkMatch = text.match(/<a[^>]*id="redirect-message"[^>]*href="([^"]+)"/i);
            if (linkMatch) {
                return linkMatch[1];
            }
            
            // If response has Location header (redirect), use that
            const location = response.headers.get('Location');
            if (location) {
                return location;
            }
        } catch (e) {
            console.error('Error parsing intermediate page:', e);
        }
        
        // Fallback to original URL
        return url;
    };
    
    // Network request functions
    window.requestDocument = async function(url) {
        console.log('requestDocument:', url);
        // In ScienceDirect context, we're already on the page
        return document;
    };
    
    window.requestText = async function(url, options) {
        // Handle both old style (url, callback, method, body, headers) 
        // and new style (url, {body, method, headers})
        let callback, method, body, headers;
        
        if (typeof options === 'function') {
            // Old style: requestText(url, callback, method, body, headers)
            callback = options;
            method = arguments[2];
            body = arguments[3];
            headers = arguments[4];
        } else if (typeof options === 'object') {
            // New style: requestText(url, {body, method, headers})
            ({ body, method, headers } = options);
        }
        
        console.log('requestText called for URL:', url);
        
        // Make URL absolute
        if (url.startsWith('/')) {
            url = window.location.origin + url;
        }
        
        try {
            const fetchOptions = {
                method: method || 'GET',
                credentials: 'include',
                headers: headers || {
                    'Accept': 'application/x-research-info-systems, text/plain, */*'
                }
            };
            
            if (body) {
                fetchOptions.body = body;
                // Add content-type for POST requests if not set
                if (!fetchOptions.headers['Content-Type']) {
                    fetchOptions.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                }
            }
            
            const response = await fetch(url, fetchOptions);
            const contentType = response.headers.get('content-type');
            const text = await response.text();
            
            console.log(`requestText response status: ${response.status}`);
            console.log(`requestText response Content-Type: ${contentType}`);
            
            // Check if the response is HTML, which indicates an error or redirect
            if (contentType && contentType.includes('text/html')) {
                console.error('Error: Expected RIS data but received HTML. This is likely a login or error page.');
                console.log('HTML response preview:', text.substring(0, 500));
                
                // Check if it's a redirect or login page
                if (text.includes('login') || text.includes('Login') || 
                    text.includes('sign in') || text.includes('Sign In') ||
                    text.includes('access denied') || text.includes('Access Denied')) {
                    console.error('Authentication issue detected in response');
                }
                
                // Return empty string to maintain compatibility but log the issue
                if (callback) {
                    callback('', {status: response.status});
                }
                return '';
            }
            
            // Check if we got valid RIS data
            if (text.includes('TY  -') || text.includes('TY-')) {
                console.log('Successfully received RIS data, length:', text.length);
            } else if (text.trim().length === 0) {
                console.warn('Received empty response');
            } else {
                console.warn('Received non-RIS text data, first 100 chars:', text.substring(0, 100));
            }
            
            if (callback) {
                callback(text, {status: response.status});
            }
            return text;
        } catch (error) {
            console.error('requestText fetch error:', error);
            if (callback) {
                callback('', {status: 500});
            }
            return '';
        }
    };
    
    window.requestJSON = async function(url, callback) {
        const text = await requestText(url);
        try {
            const json = JSON.parse(text);
            if (callback) callback(json);
            return json;
        } catch (e) {
            if (callback) callback(null);
            return null;
        }
    };
    
    return { items, urls };
}