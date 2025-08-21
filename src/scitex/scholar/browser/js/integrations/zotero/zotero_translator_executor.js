// Zotero translator executor
// Executes a Zotero translator in the browser with proper environment setup

async function executeZoteroTranslator(translatorCode, translatorLabel) {
    console.log(`Executing Zotero translator: ${translatorLabel}`);
    
    // Setup Zotero environment
    const { items, urls } = await setupZoteroEnvironment();
    
    let translatorError = null;
    
    try {
        // Execute the translator code in the global scope
        // This defines detectWeb, doWeb, and any other translator functions
        eval(translatorCode);
        
        // Check if translator functions exist
        if (typeof detectWeb !== 'function') {
            throw new Error('detectWeb function not found in translator');
        }
        
        // Run detectWeb to determine if this page is supported
        console.log('Running detectWeb...');
        const itemType = detectWeb(document, window.location.href);
        console.log('detectWeb returned:', itemType);
        
        if (!itemType) {
            console.log('Page not recognized by translator (detectWeb returned null/false)');
            return {
                success: false,
                translator: translatorLabel,
                urls: [],
                itemCount: 0,
                error: 'Page type not recognized by translator'
            };
        }
        
        // Run doWeb if available and page is recognized
        if (typeof doWeb === 'function') {
            console.log('Running doWeb...');
            
            // Run doWeb with a reasonable timeout
            // Some translators make async requests and we need to wait for them
            const doWebPromise = doWeb(document, window.location.href);
            const timeoutPromise = new Promise((resolve) => {
                setTimeout(() => {
                    console.log('doWeb timeout reached (10s), continuing...');
                    resolve();
                }, 10000); // 10 second timeout for complex translators
            });
            
            await Promise.race([doWebPromise, timeoutPromise]);
            console.log('doWeb phase completed');
            
            // Give async operations time to complete
            await new Promise(resolve => setTimeout(resolve, 1000));
        } else {
            throw new Error('doWeb function not found in translator');
        }
        
    } catch (e) {
        translatorError = e.message;
        console.error('Translator execution error:', e);
    }
    
    // Return whatever the translator collected
    // Trust the translator completely - no custom filtering
    const pdfUrls = Array.from(urls);
    
    console.log(`Translator collected ${items.length} items and ${pdfUrls.length} URLs`);
    
    // If no URLs found and no error, provide more context
    if (pdfUrls.length === 0 && !translatorError) {
        console.warn('No PDF URLs found. This may be due to:');
        console.warn('1. Authentication issues preventing access to full text');
        console.warn('2. The article not having a PDF available');
        console.warn('3. The publisher blocking automated access');
    }
    
    return {
        success: !translatorError && pdfUrls.length > 0,
        translator: translatorLabel,
        urls: pdfUrls,
        itemCount: items.length,
        error: translatorError
    };
}