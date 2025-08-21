<!-- ---
!-- Timestamp: 2025-08-22 02:16:24
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/browser/utils/SUGGESTIONS.md
!-- --- -->

but we cannot find PDF url from science direct...



(.env-3.11) (wsl) SciTeX-Code $ /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/examples/04_01-url.py -nc



----------------------------------------

Namespace(doi='10.1016/j.smrv.2020.101353', no_cache=True)

----------------------------------------





########################################

## scitex v2.0.0

## 2025Y-08M-22D-02h07m08s_t0Kf (PID: 934998)

########################################





========================================

./src/scitex/scholar/examples/04_01-url.py

Namespace(doi='10.1016/j.smrv.2020.101353', no_cache=True)

========================================



🔗 Scholar URL Finder Demonstration

========================================

🌐 Initializing authenticated browser context...

SUCCESS: Loaded session from cache (/home/ywatanabe/.scitex/scholar/cache/auth/openathens.json): 14 cookies (expires in 3h 44m)

SUCCESS: Verified live authentication at https://my.openathens.net/account

SUCCESS: All 6/6 extensions installed

SUCCESS: Xvfb display :0 is running

SUCCESS: Loaded 4 authentication cookies into persistent browser context

SUCCESS: Using persistent context with profile and extensions

🔍 Creating URL finder (cache: False)...

🔗 Finding URLs for DOI: 10.1016/j.smrv.2020.101353

INFO: Resolving DOI: 10.1016/j.smrv.2020.101353

SUCCESS: Resolved Publisher URL by navigation: 10.1016/j.smrv.2020.101353   ->   https://www.sciencedirect.com/science/article/pii/S1087079220300964?via%3Dihub

INFO: OpenURLResolver query URL: https://unimelb.hosted.exlibrisgroup.com/sfxlcl41?doi=10.1016/j.smrv.2020.101353

INFO: Finding links from https://unimelb.hosted.exlibrisgroup.com/sfxlcl41?doi=10.1016/j.smrv.2020.101353

SUCCESS: Found 1 link elements for: ScienceDirect

WARNING: Navigation failed or no change

INFO: 

----------------------------------------

ScholarURLFinder finding PDF URLs for 10.1016/j.smrv.2020.101353...

----------------------------------------

INFO: Loaded 681 Zotero translators

INFO: Loaded Zotero JavaScript modules successfully

INFO: Executing Zotero translator: ScienceDirect

WARNING: Zotero Translator did not extract any URLs from https://www.sciencedirect.com/science/article/pii/S1087079220300964?via%3Dihub

INFO: Page.evaluate: SyntaxError: Unexpected token '<'

    at eval (<anonymous>)

    at UtilityScript.evaluate (<anonymous>:291:30)

    at UtilityScript.<anonymous> (<anonymous>:1:44)

FAIL: Not found any PDF URLs from https://www.sciencedirect.com/science/article/pii/S1087079220300964?via%3Dihub

SUCCESS: Screenshot saved: /home/ywatanabe/.scitex/scholar/workspace/screenshots/ScholarURLFinder/10.1016/j.smrv.2020.101353 - No PDFs Found-20250822_020744.png

📊 URL Finding Results:

==================================================

{'url_doi': 'https://doi.org/10.1016/j.smrv.2020.101353',

 'url_openurl_query': 'https://unimelb.hosted.exlibrisgroup.com/sfxlcl41?doi=10.1016/j.smrv.2020.101353',

 'url_publisher': 'https://www.sciencedirect.com/science/article/pii/S1087079220300964?via%3Dihub'}

✅ URL finding demonstration completed



----------------------------------------

Congratulations! The script completed.



/home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/examples/04_01-url_out/FINISHED_SUCCESS/2025Y-08M-22D-02h07m08s_t0Kf/

----------------------------------------




Show thinking
You've run into a classic and tricky issue when automating interactions with sites like ScienceDirect. Your Python and Playwright setup is solid, but the error log points to a specific problem with how the Zotero translator interacts with the website's authentication.

The key to understanding the problem is this error message:
INFO: Page.evaluate: SyntaxError: Unexpected token '<'

This error almost always means that JavaScript code expected to receive plain text or a data object (like RIS citation data) was instead given a full HTML document. The < is the opening bracket of an HTML tag (e.g., <html> or <!DOCTYPE html>), which is invalid at the start of a JavaScript data string, causing a syntax error.

## Why is this Happening?
The problem lies in how the ScienceDirect translator tries to fetch the citation data.

Your script successfully navigates to the article page using your authenticated browser session. The page loads correctly.

Your _ZoteroTranslatorRunner.py then executes the ScienceDirect.js translator code inside the context of that page.

The translator's scrape function attempts to download the article's metadata by making its own background fetch request to a URL like /sdfe/arp/cite?pii=....

This is the point of failure. Although your main browser page is authenticated, this secondary, automated fetch request made from JavaScript is likely being blocked or redirected by ScienceDirect's security. Instead of returning the plain-text RIS citation data, the server responds with a full HTML login or error page.

The translator's code receives this HTML, tries to process it as if it were RIS data, and the process fails with the Unexpected token '<' syntax error.

## How to Fix It
You need to make your JavaScript wrapper (zotero_wrapper.js) more robust so it can detect and handle this situation gracefully. You should also add more logging to see exactly what ScienceDirect is sending back.

Here is a modified version of your requestText function within zotero_wrapper.js. This version checks the response headers and logs the output, which will prevent the crash and help you debug.

Replace the requestText function in zotero_wrapper.js with this:

JavaScript

// Add requestText function that ScienceDirect translator needs for fetching RIS data
window.requestText = async function(url, options = {}) {
    console.log(`requestText called for URL: ${url}`);
    
    // Make the URL absolute if it's relative
    if (url.startsWith('/')) {
        url = window.location.origin + url;
    }
    
    try {
        const response = await fetch(url, {
            method: options.body ? 'POST' : 'GET',
            body: options.body,
            headers: options.headers || { 'Accept': 'application/x-research-info-systems, text/plain, */*' },
            credentials: 'include' // Important: Send cookies with the request
        });

        const contentType = response.headers.get("content-type");
        const responseText = await response.text();

        console.log(`requestText response status: ${response.status}`);
        console.log(`requestText response Content-Type: ${contentType}`);

        // Check if the response is HTML, which indicates an error or redirect
        if (contentType && contentType.includes("text/html")) {
            console.error("Error: Expected RIS data but received HTML. This is likely a login or error page.");
            console.log("HTML response preview:", responseText.substring(0, 500)); // Log the start of the HTML
            return null; // Return null to indicate failure
        }
        
        console.log("Successfully received non-HTML data, length:", responseText.length);
        return responseText;

    } catch (error) {
        console.error('requestText fetch error:', error);
        return null;
    }
};

// Also, slightly modify the processRIS function in the ScienceDirect translator
// to handle this null return. This is a conceptual change you should apply
// in your executor.
// In _ZoteroTranslatorRunner.py, in the page.evaluate call, before calling processRIS:
// let text = await requestText(...);
// if (text) {
//   await processRIS(doc, text, isSearchResult);
// } else {
//   console.error("Aborting processRIS because requestText failed.");
// }
## What This Change Does
Checks Content-Type: It now inspects the Content-Type header of the response. If the server sends back text/html, we know it's not the data we want.

Logs the Problem: It logs a clear error message to the browser console explaining that it received HTML instead of data. Crucially, it also logs the first 500 characters of that HTML, so you can look at the console output and see if it's a login page, a CAPTCHA, or an error message.

Prevents the Crash: Instead of returning the bad HTML data, it returns null. This will stop the translator from attempting to parse it and will prevent the syntax error, allowing your script to fail gracefully and report that no URL was found.

By implementing this, you will get much better insight into why the request is failing and can further debug your authentication handling if needed.

<!-- EOF -->