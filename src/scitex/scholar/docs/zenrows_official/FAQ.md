<!-- ---
!-- Timestamp: 2025-07-30 20:44:58
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/docs/zenrows_FAQ.md
!-- --- -->


ZenRows Docs home pagedark logo
Search...



Navigation
Frequently Asked Questions
Frequently Asked Questions
Can I Get Cookies from the Responses?

Headers, including cookies, returned by the target website are prefixed with Zr- and included in all our responses.
Suppose you are scraping a website that requires session cookies for authentication. By capturing the Zr-Cookies header from the initial response, you can include these cookies in your subsequent requests to maintain the session and access authenticate_async content.

Copy

Ask AI
Zr-Content-Encoding: gzip
Zr-Content-Type: text/html
Zr-Cookies: _pxhd=Bq7P4CRaW1B...
Zr-Final-Url: https://www.example.com/
You could send those cookies in a subsequent request as Custom Headers and also use session_id to keep the same IP for up to 10 minutes.
By following this process, you can handle sessions and access restricted areas of the website seamlessly.
Can I Logging In/Register and Access Content Behind Login?

If you need to scrape_async data from a website that requires login authentication, you can log in or register and access content behind a login. However, due to privacy and legal reasons, we offer limited support for these cases.
Login and registration work like regular forms and can be treated as such. There are two main methods to send forms:
Send POST requests.
Fill in and submit a form using JavaScript Instructions.

Copy

Ask AI
{"fill": [".input-selector", "website_username"]} // Fill the username input
{"fill": [".input-selector", "website_password"]} // Fill the password input
All requests will return headers, including the session cookies. By using these cookies in subsequent requests, you can operate as a logged-in user. Additionally, you can include a Session ID to maintain the same IP address for up to 10 minutes.
ZenRows is a scraping tool, not a VPN. If your goal is to log in once and browse the internet with the same IP, you may need a different service.
Can I Maintain Sessions/IPs Between Requests

Suppose you need to perform multiple actions on a website that requires maintaining the same session/IP. You can use the Session ID parameter to maintain the same IP between requests. ZenRows will store the IP for 10 minutes from the first request with that ID. All subsequent requests with that ID will use the same IP.
However, session_id will not store any other request data, such as session cookies. You will receive those cookies as usual and can decide which ones to send on the next request.
Multiple Session IDs can run concurrently, with no limit to the number of sessions.
Can I Run the API/Proxy in Multiple Threads to Improve Speed?

Each plan comes with a concurrency limit. For example, the Developer plan allows 10 concurrent requests, meaning you can have up to 10 requests running simultaneously, significantly improving speed.
Sending requests above that limit will result in a 429 Too Many Requests error.
We wrote a guide on using concurrency that provides more details, including examples in Python and JavaScript. The same principles apply to other languages and libraries.
Can I Send/Submit Forms?

There are different ways to approach submitting forms on a website when you need to retrieve data.
POST Requests: The most straightforward way for non-secured endpoints is to send a POST request as the page does. You can examine and replicate the requests in the browser DevTools.
Imitate User Behavior Using JavaScript Instructions: Use JavaScript Instructions to visit pages protected by anti-bot solutions and interact with them. This includes filling in inputs, clicking buttons, and performing other actions.
CSS Selectors Do Not Work or 'Parser is Not Valid'

​
Common Issues with CSS Selectors
One of the most common issues users encounter when working with CSS Selectors in web scraping is improper encoding. CSS Selectors need to be correctly encoded to be recognized and processed by the API.
You can use ZenRows’ Builder or an online tool to properly encode your CSS Selectors before sending them in a request.
​
Example of Using a CSS Selector
Let’s say you want to extract content from the .my-class CSS selector and store it in a property named test. You would encode the selector and include it in your request like this:

Copy

Ask AI
curl "https://api.zenrows.com/v1/?apikey=YOUR_ZENROWS_API_KEY&url=YOUR_URL&css_extractor=%257B%2522test%2522%253A%2520%2522.my-class%2522%257D"
​
Troubleshooting CSS Selector Issues
If you’re still getting empty responses or the parser reports an error:
Check the Raw HTML: Request the plain HTML to see if the content served by the website differs from what you see in your browser. Some websites serve different content based on the user’s location, device, or other factors.
Verify the Selector: Ensure the selector you’re using is correct by testing it in your browser’s Developer Tools (e.g., using Chrome’s Console with document.querySelectorAll(".my-class")).
Review the Documentation: Refer to the ZenRows documentation for detailed information on using CSS Selectors with the API.
If the HTML looks correct, the selector works in the browser, but the parser still fails, contact us, and we’ll help you troubleshoot the issue.
​
See Also
For comprehensive examples of working with complex layouts and advanced selector techniques, check out our Advanced CSS Selector Examples guide.
Does session_id Remember Session Data?

session_id won’t store any request data, such as session cookies. You will get those back as usual and decide which ones to send on the next request.
How do I Export Data to CSV using the Universal Scraper API?

Once you’ve extracted data using ZenRows, you might want to store it in CSV format. For simplicity, we’ll focus on a single URL and save the data to one file. In real-world scenarios, you might need to handle multiple URLs and aggregate the results.
To start, we’ll explore how to export data to CSV using both Python and JavaScript.
​
From JSON using Python
If you’ve obtained JSON output from ZenRows with the autoparse feature enabled, you can use Python to convert this data into a CSV file.
Autoparsing can work for many websites but some are not included on this feature
The Pandas library will help us flatten nested JSON attributes and save the data as a CSV file.
Here’s a sample Python script:
scrape_asyncr_async.py

Copy

Ask AI
# pip install requests pandas
import requests
import json
import pandas as pd

url = "https://www.zillow.com/san-francisco-ca/"
apikey = "YOUR_ZENROWS_API_KEY"
params = {"autoparse": True, "url": url, "apikey": apikey}
response = requests.get("https://api.zenrows.com/v1/", params=params)

content = json.loads(response.text)

data = pd.json_normalize(content)
data.to_csv("result.csv", index=False)
You can also adjust the json_normalize function to control how many nested levels to flatten and rename fields. For instance, to flatten only one inner level and remove latLong from latitude and longitude fields:

Copy

Ask AI
data = pd.json_normalize(content, max_level=1).rename(
	columns=lambda x: x.replace("latLong.", ""))
​
From HTML using Python
When dealing with HTML output without the autoparse feature, you can use BeautifulSoup to parse the HTML and extract data. We’ll use the example of an eCommerce site from Scraping Course. Create a dictionary for each product with essential details, then use Pandas to convert this list of dictionaries into a DataFrame and save it as a CSV file.
Here’s how to do it:
scrape_asyncr_async.py

Copy

Ask AI
# pip install requests beautifulsoup4 pandas
import requests
from bs4 import BeautifulSoup
import pandas as pd

url = "https://www.scrapingcourse.com/ecommerce/"
apikey = "YOUR_ZENROWS_API_KEY"
params = {"url": url, "apikey": apikey}
response = requests.get("https://api.zenrows.com/v1/", params=params)
soup = BeautifulSoup(response.content, "html.parser")

content = [{
	"product_name": product.select_one(".product-name").text.strip(),
	"price": product.select_one(".price").text.strip(),
	"rating": product.select_one(".rating").text.strip() if product.select_one(".rating") else "N/A",
	"link": product.select_one(".product-link").get("href"),
} for product in soup.select(".product")]

data = pd.DataFrame(content)
data.to_csv("result.csv", index=False)
​
From JSON using JavaScript
For JavaScript and Node.js, you can use the json2csv library to handle the JSON to CSV conversion.
After getting the data, we will parse it with a flatten transformer. As the name implies, it will flatten the nested structures inside the JSON. Then, save the file using writeFileSync.
Here’s an example using the ZenRows Universal Scraper API with Node.js:
scrape_asyncr_async.js

Copy

Ask AI
// npm install zenrows json2csv
const fs = require("fs");
const {
	Parser,
	transforms: { flatten },
} = require("json2csv");
const { ZenRows } = require("zenrows");

(async () => {
	const client = new ZenRows("YOUR_ZENROWS_API_KEY");
	const url = "https://www.scrapingcourse.com/ecommerce/";

	const { data } = await client.get(url, { autoparse: "true" });

	const parser = new Parser({ transforms: [flatten()] });
	const csv = parser.parse(data);

	fs.writeFileSync("result.csv", csv);
})();
​
From HTML using JavaScript
For extracting data from HTML without autoparse you can use the cheerio library to parse the HTML and extract relevant information. We’ll use the Scraping Course eCommerce example for this task:
As with the Python example, we will use AutoScout24 to extract data from HTML without the autoparse feature. For that, we will get the plain result and load it into cheerio. It will allow us to query elements as we would in the browser or with jQuery. We will return an object with essential data for each car entry in the list. Parse that list into CSV using json2csv, and no flatten is needed this time. And lastly, store the result. These last two steps are similar to the autoparse case.
scrape_asyncr_async.js

Copy

Ask AI
// npm install zenrows json2csv cheerio
const fs = require("fs");
const cheerio = require("cheerio");
const { Parser } = require("json2csv");
const { ZenRows } = require("zenrows");

(async () => {
	const client = new ZenRows("YOUR_ZENROWS_API_KEY");
	const url = "https://www.scrapingcourse.com/ecommerce/";

	const { data } = await client.get(url);
	const $ = cheerio.load(data);

	const content = $(".product").map((_, product) => ({
		product_name: $(product).find(".product-name").text().trim(),
		price: $(product).find(".price").text().trim(),
		rating: $(product).find(".rating").text().trim() || "N/A",
		link: $(product).find(".product-link").attr("href"),
	}))
	.toArray();

	const parser = new Parser();
	const csv = parser.parse(content);

	fs.writeFileSync("result.csv", csv);
})();
If you encounter any issues or need further assistance with your scrape_asyncr_async setup, please contact us, and we’ll be happy to help!
Extract Data from Lists, Tables, and Grids

We’ll explore popular use cases for scraping, such as lists, tables, and product grids. Use these as inspiration and a guide for your scrape_asyncr_asyncs.
​
Scraping from Lists
We will use the Wikipedia page on Web scraping for testing. A section at the bottom, “See also”, contains links in a list. We can get the content by using the CSS selector for the list items: {"items": ".div-col > ul li"}.
That will get the text, but what of the links? To access attributes, we need a non-standard syntax for the selector: @href. It won’t work with the previous selector since the last item is the li element, which does not have an href attribute. So we must change it for the link element: {"links": ".div-col > ul a @href"}.
CSS selectors, in some languages, must be encoded to avoid problems with URLs.

Copy

Ask AI
curl "https://api.zenrows.com/v1/?apikey=YOUR_ZENROWS_API_KEY&url=https%3A%2F%2Fen.wikipedia.org%2Fwiki%2FWeb_scraping&css_extractor=%257B%2522items%2522%253A%2520%2522.div-col%2520%253E%2520ul%2520li%2522%252C%2520%2522links%2522%253A%2520%2522.div-col%2520%253E%2520ul%2520a%2520%2540href%2522%257D"
Our Builder can help you write and test the selectors and output code in several languages.
Extract Data from Wikipedia Lists
​
Scraping from Tables
Assuming regular tables (no empty cells, rows with fewer items, and others), we can extract table data with CSS selectors. We’ll use a list of countries, the first table on the page, the one with the class wikitable.
To extract the rank, which is the first column, we can use "table.wikitable tr > :first-child". It will return an array with 243 items, 2 header lines, and 241 ranks. For the country name, second column, something similar but adding an a to avoid capturing the flags: "table.wikitable tr > :nth-child(2) a". In this case, the array will have one less item since the second heading has no link. That might be a problem if we want to match items by array index.

Copy

Ask AI
curl "https://api.zenrows.com/v1/?apikey=YOUR_ZENROWS_API_KEY&url=https%3A%2F%2Fen.m.wikipedia.org%2Fwiki%2FList_of_countries_and_dependencies_by_population&css_extractor=%257B%2522rank%2522%253A%2520%2522table.wikitable%2520tr%2520%253E%2520%253Afirst-child%2522%252C%2520%2522countries%2522%253A%2520%2522table.wikitable%2520tr%2520%253E%2520%253Anth-child%282%29%2520a%2522%257D"
Outputs:

Copy

Ask AI
{
	"countries": ["Country or dependent territory", "China", "India", ...],
	"rank": ["Rank", "-", "1", "2", ...]
}
As stated above, this might prove difficult for non-regular tables. For those, we might prefer to get the Plain HTML and scrape_async the content with a tool or library so we can add conditionals and logic.
This example lists items by column, not row, which might prove helpful in various cases. However, there are no easy ways to extract structured data from tables using CSS Selectors and group it by row.
​
Scraping from Product Grids
As with the tables, non-regular grids might cause problems. We’ll scrape_async the price, product name, and link from an online store. By manually searching the page’s content, we arrive at cards with the class .product. Those contain all the data we want.
It is essential to avoid duplicates, so we have to use some precise selectors. For example, ".product-item .product-link @href" for the links. We added the .product-link class because it is unique to the product cards. The same goes for name and price, which also have unique classes. All in all, the final selector would be:

Copy

Ask AI
{
	"links": ".product-item .product-link @href",
	"names": ".product-item .product-name",
	"prices": ".product-item .product-price"
}
Several items are on the page at the time of this writing. And each array has the same number of elements, so everything looks fine. If we were to group them, we could zip the arrays.
For example, in python, taking advantage of the auto-encoding that requests.get does to parameters. Remember to encode the URL and CSS extractor for different scenarios when that is not available.
scrape_asyncr_async.py

Copy

Ask AI
# pip install requests
import requests
import json

zenrows_api_base = "https://api.zenrows.com/v1/?apikey=YOUR_ZENROWS_API_KEY"
url = "https://www.scrapingcourse.com/ecommerce/"

css_extractor = """{
	"links": ".product .product-link @href",
	"names": ".product .product-name",
	"prices": ".product .product-price"
}"""

response = requests.get(zenrows_api_base, params={
						"url": url, "css_extractor": css_extractor})
parsed_json = json.loads(response.text)
result = zip(parsed_json["links"], parsed_json["names"], parsed_json["prices"])
print(list(result))

# [('/products/product1', 'Product 1', '$10.00'), ... ]
Remember that this approach won’t work properly if, for example, some products have no price. Not all the arrays would have the same length, and the zipping would misassign data. Getting the Plain HTML and parsing the content with a library and custom logic is a better solution for those cases.
If you encounter any problems or cannot correctly set up your scrape_asyncr_async, contact us, and we’ll help you.
How Can I Set Specific Headers?

ZenRows allows you to send Custom Headers on requests on case you need to scrape_async a website that requires a specific headers.
However, it’s important to test the success rate when changing them. ZenRows® automatically manages certain headers, especially those related to the browser environment, such as User-Agent.
Defensive systems inspect headers as a whole, and not all browsers use the same ones. If you choose to send custom headers, ensure the rest of the headers match accordingly.
How Do I Send POST Requests with JSON Data?

By default, POST requests use application/x-www-form-urlencoded. To send JSON data, you need to add the Content-Type: application/json header manually, though some software/tools may do this automatically.
Before trying on your target site, we recommend using a testing site like httpbin.io to verify that the parameters are sent correctly.
Ensure that the parameters are sent and the format is correct. If in doubt, switch between both modes to confirm that the changes are applied correctly.
For more info on POST requests, see How do I send POST requests?.
How do I Send POST Requests?

Send POST requests using your chosen programming language. ZenRows will transparently forward the data to the target site.
Before trying on your target site, we recommend using a testing site like httpbin.io to verify that the parameters are sent correctly.
Testing is important because not all languages and tools handle POST requests the same way. Ensure that the parameters and format are correct. By default, browsers send content as application/x-www-form-urlencoded, but many sites expect JSON content, requiring the Content-Type: application/json header.
How to encode URLs?

When working with the ZenRows Universal Scraper API, it’s crucial to encode your target URLs, especially if they contain query parameters. Encoding ensures that your URLs are correctly interpreted by the API, avoiding potential conflicts between the target URL’s parameters and those used in the API request.
Consider the following URL example:
https://www.scrapingcourse.com/ecommerce/?course=web-scraping&section=advanced
If you were to send this URL directly as part of your API request without encoding, and you also include the premium_proxy parameter, the request might look something like this:

Copy

Ask AI
curl "https://api.zenrows.com/v1/?apikey=YOUR_ZENROWS_API_KEY&url=https://www.scrapingcourse.com/ecommerce/?course=web-scraping&section=advanced&premium_proxy=true"
In this scenario, the API might incorrectly interpret the course and section parameters as part of the API’s query string rather than the target URL. This could lead to errors or unintended behavior.
To avoid such issues, you should encode your target URL before including it in the API request. URL encoding replaces special characters (like &, ?, and =) with a format that can be safely transmitted over the internet.
Here’s how you can encode the URL in Python:
encoder.py

Copy

Ask AI
import urllib.parse
encoded_url = urllib.parse.quote("https://www.scrapingcourse.com/ecommerce/?course=web-scraping&section=advanced")
After encoding, your Universal Scraper API request would look like this:

Copy

Ask AI
curl "https://api.zenrows.com/v1/?apikey=YOUR_ZENROWS_API_KEY&url=https%3A%2F%2Fwww.scrapingcourse.com%2Fecommerce%2F%3Fcourse%3Dweb-scraping%26section%3Dadvanced&premium_proxy=true"
Many HTTP clients, such as axios (JavaScript) and requests (Python), automatically encode URLs for you. However, if you are manually constructing requests or using a client that doesn’t handle encoding, you can use programming language functions or online tools to encode your URLs.
For quick manual encoding, you can use an online tool, but remember that this method is not scalable for automated processes.
Using Premium Proxies + JS Render and still blocked

If you are scraping a site with high-security measures and encounter blocks even with Premium Proxies and JS Render enabled, try these steps to unblock your requests:
1
Add Geotargeting

Use geotargeting by selecting a country for the proxy, e.g., proxy_country=us. Many sites respond better to proxies close to their operation centers.
2
Use Wait For Selector

Implement Wait For Selector to have the scrape_asyncr_async look for specific content before returning. This feature can change how the system interacts with the site and might help unblock the request.
3
Change Default Block Resources

Adjust the Block Resources settings. ZenRows blocks certain resources by default, such as CSS or images, to speed up scraping. Use your browser’s DevTools to identify other resources to block, such as media or xhr (block_resources=stylesheet,image,media,xhr). Alternatively, disable blocking by setting it to false (block_resources=none).
4
Add Custom Headers

Many websites inspect the headers of a request to determine if it is coming from a legitimate browser. Adding custom headers to mimic normal browser behavior can help bypass these checks.
Refer to our documentation on Custom Headers for more details.
Combining these methods may yield the expected results.
For high-security endpoints or inner pages, you may need to simulate a typical user session to avoid detection. First, obtain session cookies from a less protected page on the same site. This step mimics the initial user interaction with the site. Then, use these session cookies to access the more secure target page.
Additionally, you can use the Session ID feature to maintain the same IP address for up to 10 minutes, ensuring consistency in your requests and reducing the likelihood of being blocked.
What are Residential IPs?

​
Understanding Proxy Types: Data Center vs. Residential IPs
When it comes to web scraping proxies, there are two main types of IPs you can use: data center and residential.
Data Center IPs: These are IP addresses provided by cloud service providers or hosting companies. They are typically fast and reliable, but because they are easily recognizable as belonging to data centers, they are more likely to be blocked by websites that have anti-scraping measures in place.
Residential IPs: These IP addresses are assigned by Internet Service Providers (ISPs) to real residential users. Since they appear as regular users browsing the web, they are much harder to detect and block. This makes residential IPs particularly valuable when scraping sites with strong anti-bot protections, like Google or other heavily guarded domains.
​
How ZenRows Uses Residential IPs
By default, ZenRows uses data center connections for your requests. However, if you’re facing blocks or need to scrape_async highly protected websites, you can opt for residential IPs by setting the premium_proxy parameter to true. This will route your request through a residential IP, significantly increasing your chances of success.
It’s important to note that using residential IPs comes with an additional cost due to the higher value and lower detection rate of these proxies.
YOu can check out more about Premium Proxies here!
​
Example of a Request with Residential IPs
Here’s how you can make a request using a residential IP:

Copy

Ask AI
curl "https://api.zenrows.com/v1/?apikey=YOUR_ZENROWS_API_KEY&url=YOUR_URL&premium_proxy=true"
In cases where you’re also targeting content localized to specific regions, ZenRows supports geotargeting with residential IPs, allowing you to specify the country of the IP.
​
Troubleshooting Blocks
If you continue to experience blocks even with residential IPs, feel free to contact us, and we’ll work with you to find a solution.
What is Autoparse?

​
Simplifying Data Extraction with Autoparse
ZenRows offers a powerful feature called Autoparse, designed to simplify the process of extracting structured data from websites. This feature leverages custom parsers allowing you to easily retrieve data in a structured JSON format rather than raw HTML.
​
How It Works
By default, when you call the ZenRows API, the response will be in Plain HTML. However, when you activate the autoparse parameter, the API will automatically parse the content of supported websites and return the data as a JSON object. This makes it much easier to work with the data, especially when dealing with complex websites that require extensive parsing logic.
​
Example of a Request with Autoparse
Here’s how you can make an API call with the Autoparse feature enabled:

Copy

Ask AI
curl "https://api.zenrows.com/v1/?apikey=YOUR_ZENROWS_API_KEY&url=YOUR_URL&autoparse=true"
​
Limitations and Troubleshooting
Supported Domains: The Autoparse feature is in experimental phase and doesn’t work in all domains. You can view some of the supported domains on the ZenRows Scraper page. If the website you’re trying to scrape_async isn’t supported, the response will either be empty, incomplete, or an error.
Fallback to HTML: If you find that Autoparse doesn’t return the desired results, you can simply remove the autoparse parameter and try the request again. This will return the plain HTML response, allowing you to manually parse the data as needed.
What Are the Benefits of JavaScript Rendering?

Enabling JavaScript Rendering not only allows you to scrape_async content that would otherwise be inaccessible, but it also unlocks advanced scraping features. For example, with JavaScript Rendering, you can use the wait_for parameter to delay scraping until a specific element is present on the page, ensuring you capture the content you need.
Check out more about JavaScript Rendering here!
Why Some Headers are Managed by ZenRows?

Browser-based headers are crucial for ensuring that requests appear legitimate to target websites. ZenRows manages these headers to mimic real user behavior, which significantly reduces the risk of being blocked. By preventing customers from manually setting these headers, ZenRows can optimize the success rate and avoid common pitfalls associated with improper header configurations.
​
Example of Sending Custom Headers
Here’s an example using cURL to send custom headers that are permitted along with your ZenRows request:
bash

Copy

Ask AI
curl \
-H "Accept: application/json" \
-H "Referer: https://www.google.com" \
"https://api.zenrows.com/v1/?apikey=YOUR_ZENROWS_API_KEY&url=YOUR_URL&custom_headers=true"
Was this page helpful?


Yes

No
Scrape and Crawl from a Seed URL
Powered by Mintlify
Frequently Asked Questions - ZenRows Docs

<!-- EOF -->