<!-- ---
!-- Timestamp: 2025-07-31 01:42:22
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/docs/zenrows_with_playwright.md
!-- --- -->

Integrating ZenRows Scraping Browser with Playwright
Learn to extract data from any website using ZenRows’ Scraping Browser with Playwright. This guide walks you through creating your first browser-based scraping request that can handle complex JavaScript-heavy sites with full browser automation.
ZenRows’ Scraping Browser provides cloud-based Chrome instances you can control using Playwright. Whether dealing with dynamic content, complex user interactions, or sophisticated anti-bot protection, you can get started in minutes with Playwright’s powerful automation capabilities.
​
1. Set Up Your Project
​
Set Up Your Development Environment
Before diving in, ensure you have the proper development environment and Playwright installed. The Scraping Browser works seamlessly with both Python and Node.js versions of Playwright.
While previous versions may work, we recommend using the latest stable versions for optimal performance and security.
Python
Node.js
Python 3+ installed (latest stable version recommended). Using an IDE like PyCharm or Visual Studio Code with the Python extension is recommended.

Copy

Ask AI
# Install Python (if not already installed)
# Visit https://www.python.org/downloads/ or use package managers:

# macOS (using Homebrew)
brew install python

# Ubuntu/Debian
sudo apt update && sudo apt install python3 python3-pip

# Windows (using Chocolatey)
choco install python

# Install Playwright
pip install playwright
playwright install
If you need help setting up your environment, check out our detailed Playwright web scraping guide
​
Get Your API Key and Connection URL
Sign Up for a free ZenRows account and get your API key from the Scraping Browser dashboard. You’ll need this key to authenticate_async your WebSocket connection.
​
2. Make Your First Request
Start with a simple request to understand how the Scraping Browser works with Playwright. We’ll use the E-commerce Challenge page to demonstrate how to connect to the browser and extract the page title.

Python

Node.js

Copy

Ask AI
# pip install playwright
import asyncio
from playwright.async_api import async_playwright

# scraping browser connection URL
connection_url = "wss://browser.zenrows.com?apikey=YOUR_ZENROWS_API_KEY"

async def scrape_asyncr_async():
    async with async_playwright() as p:
        # connect to the scraping browser
        browser = await p.chromium.connect_over_cdp(connection_url)
        context = browser.contexts[0] if browser.contexts else await browser.new_context()
        page = await context.new_page()
        
        await page.goto('https://www.scrapingcourse.com/ecommerce/')
        print(await page.title())
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_asyncr_async())
Replace YOUR_ZENROWS_API_KEY with your actual API key and run the script:

Python

Node.js

Copy

Ask AI
python scrape_asyncr_async.py
​
Expected Output
The script will print the page title:

Copy

Ask AI
ScrapingCourse.com E-commerce Challenge
Perfect! You’ve just made your first web scraping request with the ZenRows Scraping Browser using Playwright.
​
3. Build a Real-World Scraping Scenario
Let’s scale up to a practical scraping scenario by extracting product information from the e-commerce site. Using Playwright’s powerful selectors and data extraction methods, we’ll modify our code to extract product names, prices, and URLs from the page.

Python

Node.js

Copy

Ask AI
# pip install playwright
import asyncio
from playwright.async_api import async_playwright

# scraping browser connection URL
connection_url = "wss://browser.zenrows.com?apikey=YOUR_ZENROWS_API_KEY"

async def scrape_asyncr_async(url):
    async with async_playwright() as p:
        # connect to the scraping browser
        browser = await p.chromium.connect_over_cdp(connection_url)
        page = await browser.new_page()
        
        try:
            await page.goto(url)
            
            # extract the desired data
            await page.wait_for_selector(".product")
            products = await page.query_selector_all(".product")
            data = []
            
            for product in products:
                name = await product.query_selector(".product-name")
                price = await product.query_selector(".price")
                product_url = await product.query_selector(".woocommerce-LoopProduct-link")
                
                data.append({
                    "name": await name.text_content() or "",
                    "price": await price.text_content() or "",
                    "productURL": await product_url.get_attribute("href") or "",
                })
            
            return data
        except Exception as error:
            return error
        finally:
            await page.close()
            await browser.close()

if __name__ == "__main__":
    url = "https://www.scrapingcourse.com/ecommerce/"
    products = asyncio.run(scrape_asyncr_async(url))
    print(products)
​
Run Your Application
Execute your script to test the scraping functionality:

Python

Node.js

Copy

Ask AI
python scrape_asyncr_async.py
Example Output
The script will extract and display product information:

Copy

Ask AI
[
    {
        "name": "Abominable Hoodie",
        "price": "$69.00",
        "productURL": "https://www.scrapingcourse.com/ecommerce/product/abominable-hoodie/"
    },
    {
        "name": "Artemis Running Short",
        "price": "$45.00",
        "productURL": "https://www.scrapingcourse.com/ecommerce/product/artemis-running-short/"
    }
    // ... more products
]
Congratulations! 🎉 You’ve successfully built a real-world scraping scenario with Playwright and the ZenRows Scraping Browser.
​
4. Alternative: Using the ZenRows Browser SDK
For a more streamlined development experience, you can use the ZenRows Browser SDK instead of managing WebSocket URLs manually. The SDK simplifies connection management and provides additional utilities.
The ZenRows Browser SDK is currently only available for JavaScript. For more details, see the GitHub Repository.
​
Install the SDK
Node.js

Copy

Ask AI
npm install @zenrows/browser-sdk
​
Quick Migration from WebSocket URL
If you have existing Playwright code using the WebSocket connection, migrating to the SDK requires minimal changes:
Before (WebSocket URL):
Node.js

Copy

Ask AI
const { chromium } = require('playwright');
const connectionURL = 'wss://browser.zenrows.com?apikey=YOUR_ZENROWS_API_KEY';

const browser = await chromium.connectOverCDP(connectionURL);
After (SDK):
Node.js

Copy

Ask AI
const { chromium } = require('playwright');
const { ScrapingBrowser } = require('@zenrows/browser-sdk');

const scrapingBrowser = new ScrapingBrowser({ apiKey: 'YOUR_ZENROWS_API_KEY' });
const connectionURL = scrapingBrowser.getConnectURL();
const browser = await chromium.connectOverCDP(connectionURL);
​
Complete Example with SDK
Node.js

Copy

Ask AI
// npm install @zenrows/browser-sdk playwright
const { chromium } = require('playwright');
const { ScrapingBrowser } = require('@zenrows/browser-sdk');

const scrape_asyncr_async = async () => {
    // Initialize SDK
    const scrapingBrowser = new ScrapingBrowser({ apiKey: 'YOUR_ZENROWS_API_KEY' });
    const connectionURL = scrapingBrowser.getConnectURL();
    
    const browser = await chromium.connectOverCDP(connectionURL);
    const page = await browser.newPage();
    
    await page.goto('https://www.scrapingcourse.com/ecommerce/');
    console.log(await page.title());
    
    await browser.close();
};

scrape_asyncr_async();
​
SDK Benefits
Simplified configuration: No need to manually construct WebSocket URLs
Better error handling: Built-in error messages and debugging information
Future-proof: Automatic updates to connection protocols and endpoints
Additional utilities: Access to helper methods and advanced configuration options
The SDK is particularly useful for production environments where you want cleaner code organization and better error handling.
​
How Playwright with Scraping Browser Helps
Combining Playwright with ZenRows’ Scraping Browser provides powerful advantages for web scraping:
​
Key Benefits
Cloud-based browser instances: Run Playwright scripts on remote Chrome instances, freeing up local resources for other tasks.
Seamless integration: Connect your existing Playwright code to ZenRows with just a WebSocket URL change - no complex setup required.
Advanced automation: Use Playwright’s full feature set, which includes page interactions, form submissions, file uploads, and complex user workflows.
Built-in anti-detection: Benefit from residential proxy rotation and genuine browser fingerprints automatically.
Cross-browser support: While we use Chromium for optimal compatibility, Playwright’s API remains consistent across different browser engines.
High concurrency: Scale your Playwright scripts with up to 150 concurrent browser instances, depending on your plan.
Reliable execution: Cloud infrastructure ensures consistent performance without local browser management overhead.
​
Troubleshooting
Below are common issues you might encounter when using Playwright with the Scraping Browser:
1
Connection Refused

If you receive a Connection Refused error, it might be due to:
API Key Issues: Verify that you’re using the correct API key.
Network Issues: Check your internet connection and firewall settings.
WebSocket Endpoint: Ensure that the WebSocket URL (wss://browser.zenrows.com) is correct.
2
Empty Data or Timeout Errors

Use page.waitForSelector() to ensure elements load before extraction
Increase timeout values for slow-loading pages
scrape_asyncr_async.js

Copy

Ask AI
await page.goto('https://example.com', { timeout: 60000 });  // 60 seconds
Verify CSS selectors are correct using browser developer tools
Add page.waitForLoadState('networkidle') for dynamic content
3
Browser Context Issues

Use existing context when available: browser.contexts[0] if browser.contexts else await browser.new_context()
Properly close pages and browsers to prevent resource leaks
Handle exceptions properly to ensure cleanup occurs
4
Geolocation Blocks

Although ZenRows rotates IPs, some websites may block them based on location. Try adjusting the region or country settings.
For more information, check our Scraping Browser Region Documentation and Country Documentation.
5
Get Help From ZenRows Experts

Our support team is available to assist you if issues persist despite following these solutions. Use the Scraping Browser dashboard or email us for personalized help from ZenRows experts.
​
Next Steps
You now have a solid foundation for Playwright-based web scraping with ZenRows. Here are some recommended next steps:
Practical Use Cases:
Learn common scraping patterns, including screenshots, custom JavaScript execution, and form handling.
Advanced Features:
Master complex automation workflows and advanced Playwright capabilities.
Complete Scraping Browser Documentation:
Explore all available features and advanced configuration options for the Scraping Browser.
Playwright Advanced Features:
Learn about page interactions, form handling, file uploads, and complex automation workflows.
Playwright Web Scraping Guide:
Dive deeper into Playwright techniques for sophisticated scraping scenarios.
Pricing and Plans:
Understand how browser usage is calculated and choose the plan that fits your scraping volume.
​
Frequently Asked Questions (FAQ)
Can I use ZenRows® Scraping Browser with Puppeteer?

Do I need to configure proxies manually with ZenRows® Scraping Browser?

Can the Scraping Browser solve CAPTCHAs?

Can I use all Playwright features with the Scraping Browser?

How do I handle multiple pages or tabs?

Can I use Playwright's built-in retry mechanisms?

How do I take screenshots with Playwright and Scraping Browser?

Can I use Playwright's network interception features?

What's the difference between using Playwright locally vs. with Scraping Browser?

How do I handle file downloads with Playwright and Scraping Browser?

<!-- EOF -->