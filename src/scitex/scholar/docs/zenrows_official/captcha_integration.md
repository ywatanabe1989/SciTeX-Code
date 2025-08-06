<!-- ---
!-- Timestamp: 2025-07-31 23:06:53
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/docs/zenrows_captcha_integration.md
!-- --- -->

JavaScript Rendering (Headless browser)
Many modern websites use JavaScript to dynamically load content, meaning that the data you need might not be available in the initial HTML response. To handle such cases, you can use our JavaScript rendering feature, which simulates a real browser environment to fully load and render the page before extracting the data.
​
Enabling JavaScript Rendering
To activate JavaScript rendering, append js_render=true to the request. This tells our system to process the page using a headless browser, allowing you to scrape_async content that is loaded dynamically by JavaScript.
Enabling JavaScript rendering incurs a higher cost than standard requests. Five times the cost of a standard request

Python

Node.js

Java

PHP

Go

Ruby

cURL

Copy

Ask AI
# pip install requests
import requests

url = 'https://httpbin.io/anything'
apikey = 'YOUR_ZENROWS_API_KEY'
params = {
    'url': url,
    'apikey': apikey,
	'js_render': 'true',
}
response = requests.get('https://api.zenrows.com/v1/', params=params)
print(response.text)
​
Features Requiring JavaScript Rendering
Several features rely on js_render being set to true. These include:
Wait: Introduces a delay before proceeding with the request. Useful for scenarios where you need to allow time for JavaScript to load content.
Wait For: Waits for a specific element to appear on the page before proceeding. When used with js_render, this parameter will cause the request to fail if the selector is not found.
JSON Response: Retrieves the rendered page content in JSON format, including data loaded dynamically via JavaScript.
Block Resources: Block specific types of resources from being loaded.
JavaScript Instructions: Allows you to execute custom JavaScript code on the page. This includes additional parameters.
Screenshot: Capture an above-the-fold screenshot of the target page by adding screenshot=true to the request.
​
Wait Milliseconds
For websites that take longer to load, you might need to introduce a fixed delay to ensure that all content is fully loaded before retrieving the HTML. You can specify this delay in milliseconds using the wait=10000 parameter.
In this example, wait=10000 will cause ZenRows to wait for 10,000 milliseconds (or 10 seconds) before returning the HTML content. You can adjust this value based on your needs, with a maximum total allowable wait time of 30 seconds.

Python

Node.js

Java

PHP

Go

Ruby

cURL

Copy

Ask AI
# pip install requests
import requests

url = 'https://httpbin.io/anything'
apikey = 'YOUR_ZENROWS_API_KEY'
params = {
    'url': url,
    'apikey': apikey,
	'js_render': 'true',
	'wait': '10000',
}
response = requests.get('https://api.zenrows.com/v1/', params=params)
print(response.text)
​
Wait For Selector
In some cases, you may need to wait for a specific CSS selector to be present in the DOM before ZenRows returns the content. This can be particularly useful for ensuring that dynamic elements or data have been fully loaded.
To implement this, add the wait_for=.price parameter to your request URL. Replace .price with the CSS selector of the element you are targeting.

Python

Node.js

Java

PHP

Go

Ruby

cURL

Copy

Ask AI
# pip install requests
import requests

url = 'https://www.scrapingcourse.com/ecommerce/'
apikey = 'YOUR_ZENROWS_API_KEY'
params = {
    'url': url,
    'apikey': apikey,
	'js_render': 'true',
	'wait_for': '.price',
}
response = requests.get('https://api.zenrows.com/v1/', params=params)
print(response.text)
​
JSON Response
To capture and analyze the response of XHR, Fetch, or AJAX requests, you can use the json_response=true parameter in your API call. This will return a JSON object with detailed information about the page and its requests.

Python

Node.js

Java

PHP

Go

Ruby

cURL

Copy

Ask AI
# pip install requests
import requests

url = 'https://httpbin.io/anything'
apikey = 'YOUR_ZENROWS_API_KEY'
params = {
    'url': url,
    'apikey': apikey,
	'js_render': 'true',
	'json_response': 'true',
}
response = requests.get('https://api.zenrows.com/v1/', params=params)
print(response.text)
The JSON object includes the following fields, with optional third and fourth fields:
​
Fields in the JSON Response
HTML: Contains the HTML content of the page. This content is encoded in JSON format and will need to be decoded to access the raw HTML.
XHR: An array where each item represents an XHR, Fetch, or AJAX request made during the page load. Each object in the array includes:
url: The URL of the request.
body: The body of the request, if applicable.
status_code: The HTTP status code of the response.
method: The HTTP method used (e.g., GET, POST).
headers: The response headers.
request_headers: The request headers.

Copy

Ask AI
  {
      "html": "<!DOCTYPE html><html>...</html>",
      "xhr": [{
          "url": "https://www.example.com/fetch",
          "body": "{\"success\": true}\n",
          "status_code": 200,
          "method": "GET",
          "headers": {
              "content-encoding": "gzip",
              // ...
          },
          "request_headers": {
              "accept": "*/*",
              // ...
          }
      }]
  }
js_instructions_report (Optional): An object providing a report on the execution of JavaScript instructions. This includes:
instructions_duration: Total time spent executing JavaScript instructions (in milliseconds).
instructions_executed: Number of JavaScript instructions executed.
instructions_succeeded: Number of instructions that were successfully executed.
instructions_failed: Number of instructions that failed.
instructions: An array of objects detailing each instruction, including:
instruction: The type of instruction (e.g., click, wait).
params: Parameters used for the instruction.
success: Whether the instruction was successful.
duration: Time taken to execute the instruction (in milliseconds).

Copy

Ask AI
{
    "html": "...",
    "xhr": [],
    "js_instructions_report": {
        "instructions_duration": 1041,
        "instructions_executed": 2,
        "instructions_succeeded": 2,
        "instructions_failed": 0,
        "instructions": [{
            "instruction": "wait_for_selector",
            "params": {
                "selector": "div"
            },
            "success": true,
            "duration": 40
        }, {
            "instruction": "wait",
            "params": {
                "timeout": 1000
            },
            "success": true,
            "duration": 1001
        }]
    }
}
screenshot (Optional): An object containing information about the screenshot taken of the target site, including:
data: The base64-encoded image data.
type: The image format (e.g., PNG, JPEG).
width: The width of the screenshot (in pixels).
height: The height of the screenshot (in pixels).

Copy

Ask AI
{
    "html": "...",
    "xhr": [],
    "screenshot": {
        "data": "... image data in base64 ...",
        "type": "image/png",
        "width": 1920,
        "height": 1080
    },
    "js_instructions_report": null
}
​
Block Resources
Why download and process data that you won’t be using? Blocking resources means preventing your headless browser from downloading specific types of content that you don’t need for your scraping task. This can include images, stylesheets, fonts, and other elements that might not be essential for your data extraction.
To improve scraping efficiency, reduce loading times, optimize performance, and reduce bandwidth usage, you can block specific types of resources from being loaded using the block_resources parameter.
ZenRows automatically blocks certain resource types by default, such as stylesheets and images, to optimize scraping speed and reduce unnecessary data load. So we recommend not using this feature unless it’s really necessary.
If you prefer to disable resource blocking entirely, set the parameter to “none”: block_resources=none.
​
Available Resource Types
ZenRows allows you to block the following resource types:
stylesheet: CSS files that define the visual styling of the page.
image: Images, including icons and banners.
media: Audio and video files.
font: Web fonts used for text styling.
script: JavaScript files.
texttrack: Text tracks for video subtitles or captions.
xhr: XMLHttpRequest requests used for AJAX calls.
fetch: Fetch API requests.
eventsource: EventSource requests for server-sent events.
websocket: WebSocket connections.
manifest: Web app manifests that define application metadata.
other: Other resource types not specifically listed above.
To block multiple resources, separate them with commas. For example, to block images and stylesheets, use block_resources=image,stylesheet.

Python

Node.js

Java

PHP

Go

Ruby

cURL

Copy

Ask AI
# pip install requests
import requests

url = 'https://httpbin.io/anything'
apikey = 'YOUR_ZENROWS_API_KEY'
params = {
    'url': url,
    'apikey': apikey,
	'js_render': 'true',
    'block_resources': 'image,media,font',
}
response = requests.get('https://api.zenrows.com/v1/', params=params)
print(response.text)
​
Troubleshooting
Sometimes, blocking particular resources, especially Javascript files, results in an error or missing content. That might happen, for example, when the target website expects XHR calls after the initial render.
Follow these steps to troubleshoot:
1
Compare HTML Outputs

Compare the Plain HTML obtained with ZenRows and a sample obtained manually. The HTML should be similar.
2
Adjust Blocked Resources

If essential elements are missing, test again by removing the blocked resources (likely JavaScript or XHR).
If the issue persists, please contact us, and we’ll assist you.
​
JavaScript Instructions
ZenRows provides an extensive set of JavaScript Instructions, allowing you to interact with web pages dynamically.
These instructions enable you to click on elements, fill out forms, submit them, or wait for specific elements to appear, providing flexibility for tasks such as clicking the read more buttons or submitting forms.
​
Using the JavaScript Instructions
To use JavaScript Instructions, you must include two parameters: js_render and js_instructions. The js_instructions parameter must be encoded.
You can use our Builder or an online tool to encode the instructions.
Here is an example of how to encode and use the instructions:

Copy

Ask AI
[
    {"click": ".button-selector"}
]
This set of instructions will load the page, locate the first element matching the .button-selector CSS selector, and click on it. The instructions parameter accepts an array of commands that ZenRows will execute sequentially.
​
Sample Code for Various Languages

Python

Node.js

Java

PHP

Go

Ruby

C#

cURL

Copy

Ask AI
# pip install requests
import requests

url = 'https://www.example.com'
apikey = 'YOUR_ZENROWS_API_KEY'
params = {
    'url': url,
    'apikey': apikey,
	'js_render': 'true',
	'js_instructions': """[{"click":".button-selector"},{"wait":500}]""",
}
response = requests.get('https://api.zenrows.com/v1/', params=params)
print(response.text)
​
Summary of Actions
Here are some common actions you can perform with JavaScript Instructions:

Copy

Ask AI
{"click": ".button-selector"} // Click on the first element that matches the CSS Selector
{"wait_for": ".late-selector"} // Wait for a given CSS Selector to load in the DOM
{"wait": 2000} // Wait an exact amount of time in ms
{"fill": [".input-selector", "value"]} // Fill in an input
{"check": ".checkbox-selector"} // Check a checkbox input
{"uncheck": ".checkbox-selector"} // Uncheck a checkbox input
{"select_option": [".select-selector", "option_value"]} // Select an option by its value
{"scroll_y": 1500} // Vertical scroll in pixels
{"scroll_x": 1500} // Horizontal scroll in pixels
{"evaluate": "document.body.style.backgroundColor = '#c4b5fd';"} // Execute JavaScript code
​
Click on an element
The click action lets you programmatically interact with webpage elements like buttons or links. It’s essential for navigating sites or accessing additional content, such as expanding sections or moving through pagination.
This action is often paired with wait_for to handle elements that load dynamically. For example, on some pages, you might click a read more button to reveal the full content of an article.

Copy

Ask AI
[
	{"click": ".read-more-selector"}
]
​
Wait For Selector
The wait_for instruction pauses the script until a specific element appears on the page, making it ideal for handling delayed content loading in Single Page Applications (SPAs) or dynamic websites.
This ensures that all necessary elements, like data fields or navigation buttons, are fully loaded before further actions are taken. For instance, after clicking a button, you might use wait_for to ensure the next page’s key elements are present before proceeding with data extraction. This step is crucial for accurate and complete data retrieval in web scraping.
If the selector takes too long to load or is not present, the instruction will fail and move on to the next one

Copy

Ask AI
[
	{"wait_for": ".late-selector"}
]
​
Wait
The wait instruction pauses execution for a specified duration, defined in milliseconds. For example, {"wait": 1000} pauses the script for one second.
This can be useful for ensuring specific actions, such as animations or data loading processes, are given enough time to complete before proceeding with further steps. It’s a straightforward way to handle timing issues and ensure all elements are ready for interaction or extraction.

Copy

Ask AI
[
	{"wait": 1000}
]
​
Fill in an Input
The fill instruction populates form fields with specified values, using a CSS selector to target the input element. This is particularly useful for automating form submissions, such as logging into a website.
The syntax below specifies the CSS selector for the input field and the value to enter. This method allows you to automate interactions with web forms, making it easier to perform tasks like login automation or data entry.

Copy

Ask AI
[
	{"fill": ["input[name='username']", "MyUsername"]}
]
​
Check a Checkbox Input
The check instruction is used to select the checkbox or radio input elements on a webpage specified by a CSS selector. It helps ensure that options like’ Remember me’ are selected during form submissions.
Calling check on an already checked input will not uncheck it

Copy

Ask AI
[
	{"check": "input[name='remember']"}
]
​
Uncheck a Checkbox Input
The uncheck instruction is used to deselect checkbox or radio input elements on a webpage, specified by a CSS selector. This is useful for clearing default selections or ensuring specific options are not selected in forms.

Copy

Ask AI
[
	{"uncheck": "input[name='remember']"}
]
​
Select an Option by its Value
To select an option from a dropdown menu, use the select_option instruction. This requires an array with two strings: the first is the CSS selector for the dropdown, and the second is the value of the option you want to select.

Copy

Ask AI
[
	{"select_option": ["input[name='countries']", "USA"]}
]
​
Scroll Y
To scroll the page vertically, use the scroll_y instruction with the number of pixels you want to scroll. Below is the example for scrolling 1500 px.

Copy

Ask AI
[
	{"scroll_y": 1500}
]
​
Scroll X
To scroll the page horizontally, use the scroll_y instruction with the number of pixels you want to scroll. Below is the example for scrolling 1500 px.

Copy

Ask AI
[
	{"scroll_x": 1500}
]
​
Execute JavaScript Code (evaluate)
Use evaluate instructions to execute custom JavaScript on the page. If none of the previous ones fits your needs, you can write JavaScript code, and ZenRows will run it. Let’s say you want to scroll to a given element to trigger a “load more” event. Then, you can add another instruction to wait for the new part to load.

Copy

Ask AI
[
	{"evaluate": "document.querySelector('.load-more-item').scrollIntoView();"}
]
​
Solve CAPTCHAs
ZenRows bypasses most CAPTCHAs, but for in-page CAPTCHAs (such as those that appear when submitting forms) you can integrate a paid solver (2Captcha). To use it, add your API Key in the integrations section.
You can solve various CAPTCHA types including reCAPTCHA and Cloudflare Turnstile. For invisible CAPTCHAs, send solve_inactive set as true inside options.

Copy

Ask AI
[
    // Solve reCAPTCHA
	{"solve_captcha": {"type": "recaptcha"}},

    // Solve Cloudflare Turnstile
	{"solve_captcha": {"type": "cloudflare_turnstile"}},

    // Solve Invisible reCAPTCHA with inactive option
	{"solve_captcha": {"type": "recaptcha", "options": {"solve_inactive": true}}}
]
For more details on the resolution, you can add JSON Response to get a detailed summary of the JS Instructions.

Copy

Ask AI
{
    "instruction": "solve_captcha",
    "success": true,
    "params": {
        "options": null,
        "type": "recaptcha"
    },
    "result": [
        {
            "id": "xxxxxxxxx",
            "solved": true,
            "solved_at": "2024-01-01T00:00:00.000Z"
        }
    ],
    "duration": 12345
}
To ensure the CAPTCHA is solved before proceeding, add wait instructions before and after the CAPTCHA-solving step, allowing time for the CAPTCHA to load and be resolved.

Copy

Ask AI
[
    {"wait": 3000}, // Wait for 3 seconds to allow the page to load
    {"solve_captcha": {"type": "recaptcha"}},
    {"wait": 2000} // Wait 2 seconds to confirm CAPTCHA resolution
]
​
Wait for a browser event
Specific actions require waiting for the browser to finish an action or navigation. The service can wait for the browser to trigger an event like load or networkidle.

Copy

Ask AI
[
	{"wait_event": "networkidle"},
	{"wait_event": "networkalmostidle"},
	{"wait_event": "load"},
	{"wait_event": "domcontentloaded"}
]
​
Instructions Inside Iframes
The instructions mentioned above won’t work inside iframes
Instructions for interacting with iframes are prefixed with frame_ and follow a similar syntax but require specifying the iframe.

Copy

Ask AI
[
	{"frame_click": ["#iframe", ".read-more-selector"]}
    {"frame_click": ["#iframe", ".button-selector"]}
    {"frame_wait_for": ["#iframe", ".late-selector"]}
    {"frame_fill": ["#iframe", ".input-selector", "value"]}
    {"frame_check": ["#iframe", ".checkbox-selector"]}
    {"frame_uncheck": ["#iframe", ".checkbox-selector"]}
    {"frame_select_option": ["#iframe", ".select-selector", "option_value"]}
    {"frame_evaluate": ["iframe-name", "document.body.style.backgroundColor = '#c4b5fd';"]} // won't work with selectors, will match iframe's name or URL
    {"frame_reveal": "#iframe"} // will create a node with the class "iframe-content-element"
]
For security, iframe’s content isn’t returned on the response. To get that content, use frame_reveal. It will append a node with the content encoded in base64 to avoid problems with JS or HTML inyection. The new node will have an attribute data-id with the given param and a iframe-content-element class.

Copy

Ask AI
[
	{"frame_reveal": "#iframe"}
	// <div class="iframe-content-element" style="display: none;" data-id="#iframe">...</div>
]
​
Using XPath
In addition to CSS selectors, you can use XPath to locate elements on a web page.
XPath is particularly useful when dealing with dynamic selectors or when more precise element selection is needed. However, if the website owner makes changes, the XPath might fail.

Copy

Ask AI
[
  {"click": "//h2[text()='Example']"}
]
In this example, ZenRows will find the first <h2> element that contains the text “Example” and click on it.
The most common use cases for the XPath are:
Dynamic Content: When dealing with dynamic web pages with unreliable CSS selectors due to frequent changes.
Nested Elements: When selecting elements deeply nested within other elements.
Text-based Selection: Selecting elements based on their text content might not be easily achievable with CSS selectors.
​
Debug JS Instructions
To see a detailed report of the JS Instructions’ execution, set json_response to true. That will return the result in JSON format, one of the fields being js_instructions_report. Useful for testing and debugging. For more details, check the JSON Response documentation.
Here is an example report:

Copy

Ask AI
{
	"html": "...",
	"xhr": [],
	"js_instructions_report": {
		"instructions_duration": 1041,
		"instructions_executed": 2,
		"instructions_succeeded": 2,
		"instructions_failed": 0,
		"instructions": [{
			"instruction": "wait_for_selector",
			"params": {
				"selector": "div"
			},
			"success": true,
			"duration": 40
		}, {
			"instruction": "wait",
			"params": {
				"timeout": 1000
			},
			"success": true,
			"duration": 1001
		}]
	}
}
​
Example Using Instructions
What does a real example look like? We will use an AliExpress product page for a demo. We can summarize the process in a few steps:
We wait for the selectors to appear and choose the color and size.
Add to cart and wait for the cart modal to appear. We click on “View Shopping Cart,” which redirects us to a different page.
Wait for the Cart page to load and check the added element.
Click on “Buy” and fill in the registration form with an email and password.

Copy

Ask AI
[
	{"wait_for": ".sku-property-list .sku-property-image"},
	{"click": ".sku-property-list .sku-property-image"},
	{"click": ".sku-property-list .sku-property-text"},

	{"click": ".product-action button.addcart"},
	{"wait_for": ".addcart-result"},
	{"click": "button.view-shopcart"},

	{"wait_for": ".shopping-cart-list"},
	{"check": ".shopping-cart-product input[type='checkbox']"},

	{"click": "#checkout-button"},
	{"wait_for": ".batman-channel-other"},
	{"click": ".batman-channel-other"},
	{"wait_for": "#batman-dialog-overlay-wrap input"},
	{"fill": ["#batman-dialog-overlay-wrap input", "user@example.com"]},
	{"fill": ["#batman-dialog-overlay-wrap input[type='password']", "myPass1234"]},
]
JS Instructions result
It show_asyncs only part of the potential that this functionality adds. You could calculate different shipping prices by changing the shipping address. Or execute custom JavaScript logic with evaluate to click an element from a list. The possibilities are endless.
Although we show_async examples with login forms, we discourage this usage. It would require you to log in to every request. If you need to scrape_async content as a logged-in user, don’t hesitate to contact us.
​
Troubleshooting Selectors
If your JavaScript Instructions are not interacting with the expected elements, the issue often lies with the selector used. Here are some quick steps to help you troubleshoot:
See if your instruction is failing: Add the parameter json_response=true to your request and check if the instruction is failing.
Double-check your selector: Make sure the CSS or XPath selector you’re using matches an element on the page. Open the page in your browser’s DevTools and test the selector directly in the console.
Wait for dynamic content: If the element is loaded dynamically, use the wait_for instruction to pause until it appears. If the selector is still not found, verify that the element is present in the final rendered DOM.
Check for frames/iframes: Elements inside iframes require specific instructions (e.g., frame_click). Standard selectors will not work on elements within iframes.
Selector specificity: Ensure your selector is specific enough to avoid matching multiple elements, but not so specific that it breaks if the page layout changes.
Use alternate strategies: If CSS selectors are unreliable, try using XPath, or leverage text-based or attribute-based selection.
For more in-depth troubleshooting tips and advanced selector examples, refer to our CSS Selector Troubleshooting Guide and Advanced Selector Examples.
If you continue to have issues, review the page structure in your browser’s DevTools, and consider if the element is loaded asynchronously or inside a shadow DOM or iframe.
​
Frequently Asked Questions (FAQ)
Does enabling JavaScript rendering increase costs?

Yes, enabling JavaScript rendering incurs a higher cost — specifically, it is five times the cost of a standard request. This is due to the additional resources required to render the page fully.
What should I do if I encounter missing content after blocking resources?

If you notice that essential elements are missing after blocking certain resources (especially JavaScript), try removing the blocked resources to see if that resolves the issue. Essential elements may depend on JavaScript execution or XHR requests.
Can I use XPath for selecting elements in JavaScript instructions?

Yes, you can use XPath in addition to CSS selectors when using JavaScript instructions. XPath is especially useful for selecting dynamic or nested elements. Just ensure that the XPath expressions are correctly formulated.
How can I debug my JavaScript instructions?

To debug your JavaScript instructions, set json_response=true in your request. This will return a detailed execution report, including the success or failure of each instruction and the time taken for execution.
What should I do if my requests keep failing after implementing JavaScript instructions?

If your requests fail even after implementing JavaScript instructions, compare the HTML outputs obtained through ZenRows with a manually obtained sample. Ensure that the HTML structures are similar. Adjust the JavaScript instructions as needed based on the findings.
Was this page helpful?


Yes

No
Premium Proxies
Headers
Powered by Mintlify

<!-- EOF -->