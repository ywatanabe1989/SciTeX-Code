/**
 * Zotero Environment Enhancements
 * 
 * Additional mock functions to support more Zotero translators,
 * especially those that use advanced features like DOM monitoring
 * and field validation.
 */

(function() {
    'use strict';
    
    // Ensure Zotero exists
    if (!window.Zotero) {
        console.error('Zotero environment not initialized. Load zotero_environment.js first.');
        return;
    }
    
    // Add field validation function (needed by HighWire 2.0 and others)
    if (!window.ZU.fieldIsValidForType) {
        window.ZU.fieldIsValidForType = function(field, type) {
            console.log(`[Zotero] Checking if field '${field}' is valid for type '${type}'`);
            
            // Comprehensive list of valid fields
            const validFields = [
                // Basic fields
                'title', 'url', 'DOI', 'date', 'abstractNote', 
                'publicationTitle', 'volume', 'issue', 'pages',
                'creators', 'attachments', 'tags', 'notes', 'itemType',
                
                // Additional metadata fields
                'accessDate', 'libraryCatalog', 'callNumber', 'rights',
                'extra', 'journalAbbreviation', 'ISSN', 'ISBN',
                'language', 'shortTitle', 'archive', 'archiveLocation',
                
                // Article-specific fields
                'seriesTitle', 'seriesText', 'seriesNumber',
                'edition', 'place', 'publisher', 'numPages',
                
                // Author/creator fields
                'firstName', 'lastName', 'creatorType',
                
                // Conference fields
                'conferenceName', 'proceedingsTitle',
                
                // Thesis fields
                'university', 'thesisType',
                
                // Report fields
                'reportNumber', 'reportType', 'institution',
                
                // Patent fields
                'patentNumber', 'assignee', 'country',
                
                // Media fields
                'websiteTitle', 'blogTitle', 'forumTitle',
                'audioRecordingFormat', 'videoRecordingFormat',
                'interviewMedium', 'artworkMedium'
            ];
            
            return validFields.includes(field);
        };
    }
    
    // Add DOM monitoring function (needed by IEEE Xplore and others)
    if (!window.Zotero.monitorDOMChanges) {
        window.Zotero.monitorDOMChanges = function(target, callback) {
            console.log('[Zotero] DOM monitoring requested for:', target);
            
            // Mock implementation using MutationObserver for better simulation
            let observer = null;
            
            try {
                if (window.MutationObserver) {
                    observer = new MutationObserver(function(mutations) {
                        console.log('[Zotero] DOM changes detected:', mutations.length, 'mutations');
                        if (callback && typeof callback === 'function') {
                            callback(mutations);
                        }
                    });
                    
                    // Observe the target with comprehensive options
                    const targetElement = typeof target === 'string' 
                        ? document.querySelector(target) 
                        : target;
                        
                    if (targetElement) {
                        observer.observe(targetElement, {
                            childList: true,
                            attributes: true,
                            subtree: true,
                            characterData: true
                        });
                        console.log('[Zotero] DOM monitoring started');
                    }
                }
                
                // Also trigger callback after a delay (fallback for static content)
                setTimeout(function() {
                    if (callback && typeof callback === 'function') {
                        console.log('[Zotero] Triggering DOM callback after delay');
                        callback([]);
                    }
                }, 500);
                
            } catch (e) {
                console.error('[Zotero] Error setting up DOM monitoring:', e);
                // Fallback: just call the callback
                if (callback && typeof callback === 'function') {
                    setTimeout(callback, 100);
                }
            }
            
            // Return object with stop method
            return {
                stop: function() {
                    if (observer) {
                        observer.disconnect();
                    }
                    console.log('[Zotero] DOM monitoring stopped');
                }
            };
        };
    }
    
    // Add selectItems function (for interactive item selection)
    if (!window.Zotero.selectItems) {
        window.Zotero.selectItems = function(items, callback) {
            console.log('[Zotero] selectItems called with', Object.keys(items).length, 'items');
            // Mock: select all items
            if (callback) {
                callback(items);
            }
            return Promise.resolve(items);
        };
    }
    
    // Add processDocuments function (for multi-document processing)
    if (!window.ZU.processDocuments) {
        window.ZU.processDocuments = function(urls, processor) {
            console.log('[Zotero] processDocuments called for', urls.length, 'URLs');
            // Mock: process each URL
            urls.forEach(url => {
                if (processor && typeof processor === 'function') {
                    processor(document, url);
                }
            });
        };
    }
    
    // Add getItemArray function (to convert items object to array)
    if (!window.ZU.getItemArray) {
        window.ZU.getItemArray = function(items) {
            if (Array.isArray(items)) {
                return items;
            }
            if (typeof items === 'object') {
                return Object.values(items);
            }
            return [];
        };
    }
    
    // Add cleanISBN function
    if (!window.ZU.cleanISBN) {
        window.ZU.cleanISBN = function(isbn) {
            if (!isbn) return '';
            // Remove all non-alphanumeric characters
            return isbn.replace(/[^0-9X]/gi, '');
        };
    }
    
    // Add cleanISSN function
    if (!window.ZU.cleanISSN) {
        window.ZU.cleanISSN = function(issn) {
            if (!issn) return '';
            // Format: XXXX-XXXX
            const cleaned = issn.replace(/[^0-9X]/gi, '');
            if (cleaned.length === 8) {
                return cleaned.substr(0, 4) + '-' + cleaned.substr(4, 4);
            }
            return cleaned;
        };
    }
    
    // Add cleanDOI function
    if (!window.ZU.cleanDOI) {
        window.ZU.cleanDOI = function(doi) {
            if (!doi) return '';
            // Remove common DOI prefixes
            doi = doi.replace(/^(https?:\/\/)?(dx\.)?doi\.org\//i, '');
            doi = doi.replace(/^doi:/i, '');
            return doi.trim();
        };
    }
    
    // Add cleanAuthor function
    if (!window.ZU.cleanAuthor) {
        window.ZU.cleanAuthor = function(author, type, useComma) {
            if (!author) return null;
            
            // Simple implementation
            const parts = useComma ? author.split(',') : author.split(' ');
            
            if (parts.length >= 2) {
                return {
                    firstName: useComma ? parts[1].trim() : parts[0].trim(),
                    lastName: useComma ? parts[0].trim() : parts[parts.length - 1].trim(),
                    creatorType: type || 'author'
                };
            }
            
            return {
                lastName: author.trim(),
                creatorType: type || 'author',
                fieldMode: 1
            };
        };
    }
    
    // Add strToISO function (date conversion)
    if (!window.ZU.strToISO) {
        window.ZU.strToISO = function(str) {
            if (!str) return '';
            
            try {
                const date = new Date(str);
                if (!isNaN(date.getTime())) {
                    return date.toISOString().split('T')[0];
                }
            } catch (e) {
                console.warn('[Zotero] Could not parse date:', str);
            }
            
            return str;
        };
    }
    
    // Add itemTypeExists function
    if (!window.ZU.itemTypeExists) {
        window.ZU.itemTypeExists = function(type) {
            const validTypes = [
                'artwork', 'audioRecording', 'bill', 'blogPost', 'book',
                'bookSection', 'case', 'computerProgram', 'conferencePaper',
                'dictionaryEntry', 'document', 'email', 'encyclopediaArticle',
                'film', 'forumPost', 'hearing', 'instantMessage', 'interview',
                'journalArticle', 'letter', 'magazineArticle', 'manuscript',
                'map', 'newspaperArticle', 'note', 'patent', 'podcast',
                'presentation', 'radioBroadcast', 'report', 'statute',
                'thesis', 'tvBroadcast', 'videoRecording', 'webpage'
            ];
            
            return validTypes.includes(type);
        };
    }
    
    console.log('[Zotero] Environment enhancements loaded successfully');
    console.log('[Zotero] Added functions: fieldIsValidForType, monitorDOMChanges, selectItems, and more');
    
})();