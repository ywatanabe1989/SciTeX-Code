// Zotero translator executor
// Executes a Zotero translator in the browser with proper environment setup

async function executeZoteroTranslator(translatorCode, translatorLabel) {
    console.log(`Executing Zotero translator: ${translatorLabel}`);
    
    // Setup Zotero environment
    const { items, urls } = await setupZoteroEnvironment();
    
    let translatorError = null;
    
    try {
        // Step 1: Execute the translator code to define its functions/objects
        eval(translatorCode);
        
        // Step 2: INTELLIGENTLY FIND AND CALL THE CORRECT detectWeb/doWeb functions
        let detected = false;
        let doWebFunction = null;
        let detectWebFunction = null;
        let contextObject = window; // Default to global context
        
        // Pattern 1: Standard global functions (classic translators)
        if (typeof detectWeb === 'function' && typeof doWeb === 'function') {
            console.log('Pattern 1: Found global detectWeb and doWeb functions');
            detectWebFunction = detectWeb;
            doWebFunction = doWeb;
        }
        // Pattern 2: Object-oriented pattern (e.g., 'em' for Embedded Metadata)
        else if (typeof em === 'object' && em !== null) {
            if (typeof em.detectWeb === 'function' && typeof em.doWeb === 'function') {
                console.log('Pattern 2: Found em.detectWeb and em.doWeb methods');
                detectWebFunction = em.detectWeb;
                doWebFunction = em.doWeb;
                contextObject = em;
            }
        }
        // Pattern 3: Check for other common translator objects
        else {
            // Check for any object that has detectWeb/doWeb methods
            const possibleObjects = ['translator', 'trans', 'Translator', 'TRANSLATOR'];
            for (const objName of possibleObjects) {
                if (window[objName] && typeof window[objName].detectWeb === 'function') {
                    console.log(`Pattern 3: Found ${objName}.detectWeb and ${objName}.doWeb methods`);
                    detectWebFunction = window[objName].detectWeb;
                    doWebFunction = window[objName].doWeb;
                    contextObject = window[objName];
                    break;
                }
            }
        }
        
        // Pattern 4: Some translators might just export a single function
        if (!detectWebFunction && typeof detectWeb === 'function') {
            detectWebFunction = detectWeb;
            // Some translators only have detectWeb, not doWeb
            doWebFunction = typeof doWeb === 'function' ? doWeb : null;
        }
        
        if (!detectWebFunction) {
            throw new Error('No detectWeb function found in any pattern');
        }
        
        // Run detectWeb to determine if this page is supported
        console.log('Running detectWeb...');
        const itemType = detectWebFunction.call(contextObject, document, window.location.href);
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
        if (doWebFunction) {
            console.log(`Running doWeb on context: ${contextObject === window ? 'window' : 'object'}...`);
            
            // Call doWeb with proper context
            const doWebPromise = doWebFunction.call(contextObject, document, window.location.href);
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
            console.warn('No doWeb function found - translator may only support detection');
        }
        
    } catch (e) {
        translatorError = e.message;
        console.error('Translator execution error:', e);
    }
    
    // Return whatever the translator collected
    const pdfUrls = Array.from(urls);
    
    console.log(`Translator collected ${items.length} items and ${pdfUrls.length} URLs`);
    
    // If no URLs found and no error, provide more context
    if (pdfUrls.length === 0 && !translatorError) {
        console.warn('No PDF URLs found. This may be due to:');
        console.warn('1. Authentication issues preventing access to full text');
        console.warn('2. The article not having a PDF available');
        console.warn('3. The translator needing a different pattern we haven\'t implemented');
        console.warn('4. The publisher blocking automated access');
    }
    
    return {
        success: !translatorError && pdfUrls.length > 0,
        translator: translatorLabel,
        urls: pdfUrls,
        itemCount: items.length,
        error: translatorError
    };
}