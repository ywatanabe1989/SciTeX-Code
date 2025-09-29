<!-- ---
!-- Timestamp: 2025-07-31 02:15:23
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/docs/zenros_final_url.md
!-- --- -->

Introduction to the Universal Scraper API
The ZenRows® Universal Scraper API is a versatile tool designed to simplify and enhance the process of extracting data from websites. Whether you’re dealing with static or dynamic content, our API provides a range of features to meet your scraping needs efficiently.
With Premium Proxies, ZenRows gives you access to over 55 million residential IPs from 190+ countries, ensuring 99.9% uptime and highly reliable scraping sessions. Our system also handles advanced fingerprinting, header rotation, and IP management, enabling you to scrape_async even the most protected sites without needing to manually configure these elements.
ZenRows makes it easy to bypass complex anti-bot measures, handle JavaScript-heavy sites, and interact with web elements dynamically — all with the right features enabled.
​
Key Features
​
JavaScript Rendering
Render JavaScript on web pages using a headless browser to scrape_async dynamic content that traditional methods might miss.
When to use: Use this feature when targeting modern websites built with JavaScript frameworks (React, Vue, Angular), single-page applications (SPAs), or any site that loads content dynamically after the initial page load.
Real-world scenarios:
E-commerce product listings that load items as you scroll
Dashboards and analytics platforms that render charts/data with JavaScript
Social media feeds that dynamically append content
Sites that hide_async certain content until JavaScript is rendered
Additional options:
Wait times to ensure elements are fully loaded
Interaction with the page to click buttons, fill forms, or scroll
Screenshot capabilities for visual verification
CSS-based extraction of specific elements
​
Premium Proxies
Leverage a vast network of residential IP addresses across 190+ countries, ensuring a 99.9% uptime for uninterrupted scraping.
When to use: Essential for accessing websites with sophisticated anti-bot systems, geo-restricted content, or when you consistently encounter blocks with standard datacenter IPs.
Real-world scenarios:
Scraping major e-commerce platforms (Amazon, Walmart)
Accessing real estate listings (Zillow, Redfin)
Gathering pricing data from travel sites (Expedia, Booking.com)
Collecting data from financial or investment platforms
Additional options:
Geolocation selection to access region-specific content
Automatic IP rotation to prevent detection
​
Custom Headers
Add custom HTTP headers to your requests for more control over how your requests appear to target websites.
When to use: When you need to mimic specific browser behavior, set cookies, or a referer.
Real-world scenarios:
Setting language preferences to get content in specific languages
Adding a referer to avoid being blocked by bot detection systems
​
Session Management
Use a session ID to maintain the same IP address across multiple requests for up to 10 minutes.
When to use: When scraping multi-page flows or processes that require maintaining the same IP across multiple requests.
Real-world scenarios:
Multi-step forms processes
Maintaining consistent session for search results and item visits
​
Advanced Data Extraction
Extract only the data you need with CSS selectors or automatic parsing.
When to use: When you need specific information from pages and want to reduce bandwidth usage or simplify post-processing.
Real-world scenarios:
Extracting pricing information from product pages
Gathering contact details from business directories
Collecting specific metrics from analytics pages
​
Language agnostic
While Python examples are provided, the API works with any programming language that can make HTTP requests.
​
Parameter Overview
Customize your scraping requests using the following parameters:
PARAMETER	TYPE	DEFAULT	DESCRIPTION
apikey required	string	Get Your Free API Key	Your unique API key for authentication
url required	string		The URL of the page you want to scrape_async
js_render	boolean	false	Enable JavaScript rendering with a headless browser. Essential for modern web apps, SPAs, and sites with dynamic content.
js_instructions	string		Execute custom JavaScript on the page to interact with elements, scroll, click buttons, or manipulate content. Use when you need to perform actions before the content is returned.
custom_headers	boolean	false	Enables you to add custom HTTP headers to your request, such as cookies or referer, to better simulate real browser traffic or provide site-specific information.
premium_proxy	boolean	false	Use residential IPs to bypass anti-bot protection. Essential for accessing protected sites.
proxy_country	string		Set the country of the IP used for the request (requires Premium Proxies). Use for accessing geo-restricted content or seeing region-specific content.
session_id	integer		Maintain the same IP for multiple requests for up to 10 minutes. Essential for multi-step processes.
original_status	boolean	false	Return the original HTTP status code from the target page. Useful for debugging in case of errors.
allowed_status_codes	string		Returns the content even if the target page fails with specified status codes. Useful for debugging or when you need content from error pages.
wait_for	string		Wait for a specific CSS Selector to appear in the DOM before returning content. Essential for elements that load asynchronously.
wait	integer	0	Wait a fixed amount of milliseconds after page load. Use for sites that load content in stages or have delayed rendering.
block_resources	string		Block specific resources (images, fonts, etc.) from loading to speed up scraping and reduce bandwidth usage. Enabled by default, carefull when changing it.
json_response	string	false	Capture network requests in JSON format, including XHR or Fetch data. Ideal for intercepting API calls made by the web page.
css_extractor	string (JSON)		Extract specific elements using CSS selectors. Perfect for targeting only the data you need from complex pages.
autoparse	boolean	false	Automatically extract structured data from HTML. Great for quick extraction without specifying selectors.
response_type	string		Convert HTML to other formats (Markdown, Plaintext, PDF). Useful for content readability, storage, or to train AI models.
screenshot	boolean	false	Capture an above-the-fold screenshot of the page. Helpful for visual verification or debugging.
screenshot_fullpage	boolean	false	Capture a full-page screenshot. Useful for content that extends below the fold.
screenshot_selector	string		Capture a screenshot of a specific element using CSS Selector. Perfect for capturing specific components.
screenshot_format	string		Choose between png (default) and jpeg formats for screenshots.
screenshot_quality	integer		For JPEG format, set quality from 1 to 100. Lower values reduce file size but decrease quality.
outputs	string		Specify which data types to extract from the scrape_async HTML.
​
Pricing
ZenRows® provides flexible plans tailored to different web scraping needs, starting from $69 per month. This entry-level plan allows you to scrape_async up to 250,000 URLs using basic requests. For more demanding needs, our Enterprise plans scale up to 38 million URLs or more.
For complex or highly protected websites, enabling advanced features like JavaScript rendering (js_render) and Premium Proxies unlocks ZenRows’ full potential, ensuring the best success rate possible.
The pricing depends on the complexity of the request — you only pay for the scraping tech you need.
Basic request: Standard rate per 1,000 requests
JS rendering: 5x cost
Premium proxies: 10x cost
Both (JS & proxies): 25x cost
For example, on the Business plan:
Basic: $0.10 per 1,000 requests
JS: $0.45 per 1,000
Proxies: $0.90 per 1,000
Both: $2.50 per 1,000
For detailed information about different plan options and pricing, visit our pricing page and our pricing documentation page.
​
Concurrency and Response Size Limits
Concurrency determines how many requests can run simultaneously:
Plan	Concurrency Limit	Response Size Limit
Developer	5	5 MB
Startup	20	10 MB
Business	50	10 MB
Business 500	100	20 MB
Business 1K	150	20 MB
Business 2K	200	50 MB
Business 3K	250	50 MB
Enterprise	Custom	50 MB
Important notes about concurrency:
Canceling requests on the client side does NOT immediately free up concurrency slots
The server continues processing canceled requests until completion
If you exceed your concurrency limit, you’ll receive a 429 Too Many Requests error
If response size is exceeded:
You’ll receive a 413 Content Too Large error
No partial data will be returned when a size limit is hit
Strategies for handling large pages:
Use CSS selectors: Target only the specific data you need with css_extractor parameter
Use response_type: Convert to markdown or plaintext to reduce size
Disable screenshots: If using screenshot features, these can significantly increase response size
Segment your scraping: Break down large pages into smaller, more manageable sections
​
Response Headers
ZenRows provides useful information through response headers:
Header	Description	Example Value	Usage
Concurrency-Limit	Maximum concurrent requests allowed by your plan	20	Monitor your plan’s capacity
Concurrency-Remaining	Available concurrent request slots	17	Adjust request rate dynamically
X-Request-Cost	Cost of this request	0.001	Track balance consumption
X-Request-Id	Unique identifier for this request	67fa4e35647515d8ad61bb3ee041e1bb	Include when contacting support
Zr-Final-Url	The final URL after any redirects occurred during the request	https://example.com/page?id=123	Track redirects
Why these headers matter:
Monitoring usage: Track your concurrent usage and stay within limits
Support requests: When reporting issues, always include the X-Request-Id for faster troubleshooting
Cost tracking: The X-Request-Cost helps you monitor your usage per request
Redirection tracking: Zr-Final-Url show_asyncs where you ended up after any redirects
​
Additional Considerations
Beyond the core features and limits, these additional aspects are important to consider when using the Universal Scraper API:
​
Cancelled Request Behavior
When you cancel a request on the client side:
The server continues processing the request until completion
The concurrency slot remains occupied for up to 3 minutes
This can result in unexpected 429 Too Many Requests errors
Implement request timeouts carefully to avoid depleting concurrency slots
​
Security Best Practices
To keep your ZenRows integration secure:
Store API keys as environment variables, never hardcode them
Monitor usage patterns to detect unauthorized use
Rotate API keys periodically for critical applications
​
Regional Performance Optimization
To optimize performance based on target website location:
Consider the geographical distance between your servers and the target website
For global applications, distribute scraping across multiple regions - the system does it by default
Monitor response times by region to identify optimization opportunities
For region-specific content, use the appropriate proxy_country parameter
​
Compression Support
ZenRows API supports response compression to optimize bandwidth usage and improve performance. Enabling compression offers several benefits for your scraping operations:
Reduced latency: Smaller response sizes mean faster data transfer times
Lower bandwidth consumption: Minimize data transfer costs and usage
Improved client performance: Less data to process means reduced memory usage
ZenRows supports the following compression encodings: gzip, deflate, br.
To use compression, include the appropriate Accept-Encoding header in your requests. Most HTTP clients already compress the request automatically. But you can also provide simple options to enable it:

Python (Requests)

Javascript (Axios)

cURL

Copy

Ask AI
import requests

response = requests.get(
    "https://api.zenrows.com/v1/",
    params={
        "apikey": "YOUR_API_KEY",
        "url": "https://example.com"
    },
    # Python Requests uses compression by default
    # headers={"Accept-Encoding": "gzip,  deflate"}
)
Most modern HTTP clients automatically handle decompression, so you’ll receive the uncompressed content in your response object without any additional configuration.
Was this page helpful?


Yes

No

<!-- EOF -->