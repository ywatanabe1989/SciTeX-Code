/**
 * Popup detection utilities for browser automation
 * 
 * Provides functions to detect various types of popups including:
 * - Cookie consent banners
 * - Newsletter/subscription modals  
 * - Authentication prompts
 * - General modal dialogs
 */

/**
 * Detect all visible popups on the page
 * @returns {Array} List of detected popups with details
 */
function detectPopups() {
    const modalSelectors = [
        '.modal',
        '.overlay',
        '[role="dialog"]',
        '.popup',
        '#onetrust-banner-sdk',
        '.onetrust-pc-dark-filter',
        '[class*="modal"]',
        '[class*="popup"]',
        '[class*="overlay"]',
        '[class*="dialog"]',
        '[class*="banner"]',
        'div[aria-modal="true"]'
    ];
    
    const found = [];
    
    for (const selector of modalSelectors) {
        try {
            const elements = document.querySelectorAll(selector);
            for (const el of elements) {
                const style = window.getComputedStyle(el);
                const rect = el.getBoundingClientRect();
                
                // Check if element is visible
                if (style.display !== 'none' && 
                    style.visibility !== 'hidden' && 
                    rect.width > 0 && 
                    rect.height > 0 &&
                    style.opacity !== '0') {
                    
                    // Get text preview
                    let text = el.innerText || el.textContent || '';
                    text = text.substring(0, 200).trim();
                    
                    // Try to identify popup type
                    let type = 'unknown';
                    const lowerText = text.toLowerCase();
                    if (lowerText.includes('cookie') || lowerText.includes('privacy')) {
                        type = 'cookie';
                    } else if (lowerText.includes('subscribe') || lowerText.includes('newsletter')) {
                        type = 'newsletter';
                    } else if (lowerText.includes('sign in') || lowerText.includes('login')) {
                        type = 'auth';
                    } else if (lowerText.includes('ai') || lowerText.includes('assistant')) {
                        type = 'ai_promotion';
                    }
                    
                    found.push({
                        selector: selector,
                        type: type,
                        text: text,
                        zIndex: style.zIndex || '0',
                        position: {
                            top: rect.top,
                            left: rect.left,
                            width: rect.width,
                            height: rect.height
                        }
                    });
                }
            }
        } catch (e) {
            // Ignore selector errors
        }
    }
    
    // Sort by z-index (highest first)
    found.sort((a, b) => {
        const zA = parseInt(a.zIndex) || 0;
        const zB = parseInt(b.zIndex) || 0;
        return zB - zA;
    });
    
    return found;
}

/**
 * Find and click cookie accept button
 * @returns {boolean} True if cookie button was clicked
 */
function acceptCookies() {
    const cookieSelectors = [
        'button#onetrust-accept-btn-handler',
        'button#onetrust-pc-btn-handler',
        'button[id*="accept-cookie"]',
        'button[id*="accept-all"]',
        'button[aria-label*="accept cookie"]',
        'button[aria-label*="Accept cookie"]',
        'button:has-text("Accept all")',
        'button:has-text("Accept All")',
        'button:has-text("I agree")',
        'button:has-text("I Agree")',
        'button:has-text("Accept")',
        '.cookie-notice button.accept',
        '[class*="cookie"] button[class*="accept"]'
    ];
    
    for (const selector of cookieSelectors) {
        try {
            const button = document.querySelector(selector);
            if (button && isElementVisible(button)) {
                button.click();
                console.log(`Accepted cookies with selector: ${selector}`);
                return true;
            }
        } catch (e) {
            // Continue to next selector
        }
    }
    
    return false;
}

/**
 * Find and click close button for popups
 * @returns {boolean} True if popup was closed
 */
function closePopup() {
    const closeSelectors = [
        'button[aria-label="Close"]',
        'button[aria-label="close"]',
        'button[aria-label*="Close"]',
        'button[aria-label*="close"]',
        'button[aria-label*="dismiss"]',
        'button[aria-label*="Dismiss"]',
        'button.close',
        'button.close-button',
        'button.modal-close',
        'button.popup-close',
        'button.dialog-close',
        'a.close',
        'a.close-button',
        'span.close',
        '[class*="close-button"]',
        '[class*="close-icon"]',
        'svg[class*="close"]',
        'button:has-text("No thanks")',
        'button:has-text("No Thanks")',
        'button:has-text("Maybe later")',
        'button:has-text("Maybe Later")',
        'button:has-text("Skip")',
        'button:has-text("Dismiss")',
        'button:has-text("Not now")',
        'button:has-text("Not Now")'
    ];
    
    for (const selector of closeSelectors) {
        try {
            const button = document.querySelector(selector);
            if (button && isElementVisible(button)) {
                button.click();
                console.log(`Closed popup with selector: ${selector}`);
                return true;
            }
        } catch (e) {
            // Continue to next selector
        }
    }
    
    return false;
}

/**
 * Check if element is visible
 * @param {Element} element - DOM element to check
 * @returns {boolean} True if element is visible
 */
function isElementVisible(element) {
    if (!element) return false;
    
    const style = window.getComputedStyle(element);
    const rect = element.getBoundingClientRect();
    
    return style.display !== 'none' &&
           style.visibility !== 'hidden' &&
           rect.width > 0 &&
           rect.height > 0 &&
           style.opacity !== '0' &&
           element.offsetParent !== null;
}

/**
 * Handle all popups on the page
 * @returns {Object} Result with count of handled popups
 */
function handleAllPopups() {
    let handled = 0;
    const popups = detectPopups();
    
    console.log(`Found ${popups.length} popup(s)`);
    
    for (const popup of popups) {
        let success = false;
        
        // Try cookie handling first if it's a cookie popup
        if (popup.type === 'cookie') {
            success = acceptCookies();
        }
        
        // Otherwise try to close it
        if (!success) {
            success = closePopup();
        }
        
        if (success) {
            handled++;
        } else {
            console.warn(`Could not handle popup: ${popup.type}`);
        }
    }
    
    return {
        detected: popups.length,
        handled: handled,
        popups: popups
    };
}

// Export functions for use in page.evaluate()
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        detectPopups,
        acceptCookies,
        closePopup,
        handleAllPopups,
        isElementVisible
    };
}