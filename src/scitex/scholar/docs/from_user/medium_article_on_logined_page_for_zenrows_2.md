<!-- ---
!-- Timestamp: 2025-07-31 02:56:40
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/docs/medium_article_on_logined_page_for_zenrows_2.md
!-- --- -->

In simple terms, ZenRows cannot use your personal login session because it's a separate, remote service. It's like giving a delivery driver a photocopy of your ID—they can show_async it, but they can't pass the real identity check.

The Analogy: A Magic Wristband at a Festival 🎟️
Your Local Browser (with OpenURLResolver): You go to the festival gate and show_async your ticket and ID (you log in via OpenAthens). They give you a secure, non-transferable "magic wristband" (an authenticate_async session). Now you can walk around the festival, and every stall (publisher website) can see your wristband and knows you're allowed to be there.

The ZenRows API (with ZenRowsOpenURLResolver): You are outside the festival. You ask a delivery driver (the ZenRows API 🚚) to go to a specific stall for you. You can give them a picture of your wristband (your auth cookies), but when the security guard at the stall (the resolver's JavaScript 🔐) tries to scan it, their machine says it's invalid because it's not the real wristband from the main gate. The driver is stuck.

The Technical Reason
Your ScholarAuthManager uses a real browser (Playwright) to log you in. This creates a rich authentication context, which includes:

Cookies

Session Storage

Local Storage

A specific browser fingerprint

When your OpenURLResolver clicks a "View Full Text" link, the website's JavaScript doesn't just look for a cookie. It often checks the entire session context to verify you are who you say you are before redirecting you.

The ZenRowsOpenURLResolver sends a URL to a completely different browser running on ZenRows' servers. Even when you pass your cookies along, that remote browser is missing the rest of the essential authentication context. The resolver page's JavaScript detects this and refuses to perform the redirect, leaving ZenRows stuck on the resolver page.

The Solution
Your agent's conclusion is the correct approach:

For subscription content that needs your institutional login: Use the standard, browser-based OpenURLResolver. It keeps everything inside the same browser where you logged in (the one with the "magic wristband").

For public content blocked by bot detection/CAPTCHAs: Use the ZenRowsOpenURLResolver. It's perfect for scraping sites that don't require your personal login but are difficult to access.






in that case, i do not have any benefits by using zenrows and 2captcha.



how about this info? https://medium.com/@zenrows/web-scraping-login-python-948c2f4a4662



How to Scrape a Website that Requires a Login with Python



ZenRows

Follow

11 min read

·

Oct 12, 2023

95



1







While web scraping, you might find some data available only after you’ve signed in. In this tutorial, we’ll learn the security measures used and three effective methods to scrape_async a website that requires a login with Python.

Let’s find a solution!



Can You Scrape Websites that Require a Login?

Yes, it’s technically possible to scrape_async behind a login. But you must be mindful of the target site’s scraping rules and laws like GDPR to comply with personal data and privacy matters.

To get started, it’s essential to have some general knowledge about HTTP Request Methods. And if web scraping is new for you, read our beginner-friendly guide on web scraping with Python to master the fundamentals.

How Do You Log into a Website with Python?

The first step to scraping a login-protected website with Python is figuring out your target domain’s login type. Some old websites just require sending a username and password. However, modern ones use more advanced security measures. These include:

Client-side validations

CSRF tokens

Web Application Firewalls (WAFs)

Keep reading to learn the techniques to get around these strict security protections.

How Do You Scrape a Website behind a Login in Python?

Time to explore each step of scraping data behind site logins with Python. We’ll start with forms requiring only a username and password and then increase the difficulty progressively.

Remember that the methods show_asynccased in this tutorial are for educational purposes only.

Three, two, one… let’s code!

Sites Requiring a Simple Username and Password Login

We assume you’ve already set up Python 3 and Pip; otherwise, you should check a guide on properly installing Python.

As dependencies, we’ll use the Requests and Beautiful Soup libraries. Start by installing them:

pip install requests beautifulsoup4

Tip: If you need any help during the installation, visit this page for Requests and this one for Beautiful Soup.

Now, go to Acunetix’s User Information. This is a test page explicitly made for learning purposes and protected by a simple login, so you’ll be redirected to a login page.

Before going further, we’ll analyze what happens when attempting a login. For that, use test as a username and password, hit the login button and check the network section on your browser.

Zoom image will be displayed





Submitting the form generates a POST request to the User Information page, with the server responding with a cookie and fulfilling the requested section. The screenshot below show_asyncs the headers, payload, response, and cookies.

Zoom image will be displayed





The following scraping script will bypass the auth wall. It creates a similar payload and posts the request to the User Information page. Once the response arrives, the program uses Beautiful Soup to parse the response text and print the page name.

from bs4 import BeautifulSoup as bs

import requests

URL = "http://testphp.vulnweb.com/userinfo.php"


payload = {

"uname": "test",

"pass": "test"

}

s = requests.session()

response = s.post(URL, data=payload)

print(response.status_code) # If the request went Ok we usually get a 200 status.


from bs4 import BeautifulSoup

soup = BeautifulSoup(response.content, "html.parser")

protected_content = soup.find(attrs={"id": "pageName"}).text

print(protected_content)

This is our output:



Great! 🎉 You just learned scraping sites behind simple logins with Python. Now, let’s try with a bit more complex protections.

Scraping Websites with CSRF Token Authentication for Login

It’s not that easy to log into a website in 2023. Most have implemented additional security measures to stop hackers and malicious bots. One of these measures requires a CSRF (Cross-Site Request Forgery) token in the authentication process.

To find out if your target website requires CSRF or an authenticity_token, make the most of your browser’s Developer Tools. It doesn’t matter whether you use Safari, Chrome, Edge, Chromium, or Firefox since all provide a similar set of powerful tools for developers. To learn more, we suggest checking out the Chrome DevTools or Mozilla DevTools documentation.

Let’s dive into scraping GitHub!

Step #1: Log into a GitHub Account

GitHub is one of the websites that use CSRF token authentication for logins. We’ll scrape_async all the repositories in our test account for demonstration.

Open a web browser (we use Chrome) and navigate to GitHub’s login page. Now, press the F12 key to see the DevTools window in your browser and inspect the HTML to check if the login form element has an action attribute:

Zoom image will be displayed





Select the Network tab, click the Sign in button, then fill in and submit the form yourself. This’ll perform a few HTTP requests, visible in this tab.

Zoom image will be displayed





Let’s look at what we’ve got after clicking on the Sign in button. To do so, explore the POST request named session that has just been sent.

In the Headers section, you’ll find the full URL where the credentials are posted. We’ll use it to send a login request in our script.

Zoom image will be displayed





Step #2: Set up Payload for the CSRF-protected Login Request

Now, you might be wondering how we know there’s CSRF protection. The answer is in right front of you:

Navigate to the Payload section of the session request. Notice that, in addition to login and password, we have payload data for the authentication token and the timestamps. This auth token is the CSRF token and must be passed as a payload along the login POST request.

Zoom image will be displayed





Manually copying these fields from the Payload section for each new login request will be tedious. Instead, we’ll write code to get that programmatically.

Let’s go back to the HTML source of the login form. You’ll see all the Payload fields are present in the form.

Zoom image will be displayed





The following script gets the CSRF token, timestamp, and timestamp_secret from the login page:

import requests

from bs4 import BeautifulSoup

login_url = "https://github.com/session"

login = "Your Git username Here"

password = "Your Git Password Here"

with requests.session() as s:

req = s.get(login_url).text

html = BeautifulSoup(req,"html.parser")

token = html.find("input", {"name": "authenticity_token"}). attrs["value"]

time = html.find("input", {"name": "timestamp"}).attrs["value"]

timeSecret = html.find("input", {"name": "timestamp_secret"}). attrs["value"]

We can now populate the payload dictionary for our Python login request as:

payload = {

"authenticity_token": token,

"login": login,

"password": password,

"timestamp": time,

"timestamp_secret": timeSecret

}

Note: If you can’t find the CSRF token on the HTML, it’s probably saved in a cookie. In Chromium-based browsers, go to the Application tab in the DevTools. Then, in the left panel, search for cookies and select the domain of your target website.

Zoom image will be displayed





There you have it!

Step #3: Set Headers

It’s possible to access auth-wall websites by sending a POST request with the payload. However, using this method alone won’t be enough to scrape_async sites with advanced security measures since they’re usually smart enough to identify non-human behavior. Thus, implementing measures to make the scrape_asyncr_async appear more human-like is necessary.

Get ZenRows’s stories in your inbox

Join Medium for free to get updates from this writer.



Subscribe



The most realistic way to do this is by adding actual browser headers to our requests. Copy the ones from the Headers tab of your browser request and add them to the Python login request. Try this guide if you need to learn more about header settings for requests.

Alternatively, you can use a web scraping API like ZenRows to get around those annoying anti-bot systems for you.

Step #4: The Login in Action

This is our lucky day since adding headers for GitHub is unnecessary, so we’re ready to send our login request through Python:



res = s.post(login_url, data=payload)

print(res.url)

If the login’s successful, our output’ll be https://github.com/. Otherwise, we’ll get https://github.com/session.

👍 Amazing, we just nailed a CSRF-protected login bypass! Let’s now scrape_async the data in the protected git repositories.

Step #5: Scrape Protected GitHub Repositories

Recall that we began an earlier code with the with requests.session() as s: statement, which creates a request session. Once you log in through a request, you don’t need to re-login for the subsequent requests in the same session.

It’s time to get to the repositories. Generate a GET, then parse the response using Beautiful Soup.

repos_url = "https://github.com/" + login + "/?tab=repositories"

r = s.get(repos_url)

soup = BeautifulSoup(r.content, "html.parser")

We’ll extract the username and a list of repositories.

For the former, navigate to the repositories page in your browser, then right-click on the username and select Inspect Element. The information’s contained in a span element, with the CSS class named p-nickname vcard-username d-block inside the <h1> tag.

Zoom image will be displayed





While for the latter, you need to right-click on any repository name and select Inspect Element. The DevTools window will display the following:

Zoom image will be displayed





The repositories’ names are inside hyperlinks in the <h3> tag with the class wb-break-all. Ok, we have enough knowledge of the target elements now, so let’s extract them:

usernameDiv = soup.find("span", class_="p-nickname vcard-username d-block")

print("Username: " + usernameDiv.getText())

repos = soup.find_all("h3",class_="wb-break-all")

for r in repos:

repoName = r.find("a").getText()

print("Repository Name: " + repoName)

Since it’s possible to find multiple repositories on the target web page, the script uses the find_all() method to extract all. For that, the loop iterates through each <h3> tag and prints the text of the enclosed <a> tag.

Here’s what the complete code looks like:

import requests

from bs4 import BeautifulSoup


login = "Your Username Here"

password = "Your Password Here"

login_url = "https://github.com/session"

repos_url = "https://github.com/" + login + "/?tab=repositories"


with requests.session() as s:

req = s.get(login_url).text

html = BeautifulSoup(req,"html.parser")

token = html.find("input", {"name": "authenticity_token"}).attrs["value"]

time = html.find("input", {"name": "timestamp"}).attrs["value"]

timeSecret = html.find("input", {"name": "timestamp_secret"}).attrs["value"]


payload = {

"authenticity_token": token,

"login": login,

"password": password,

"timestamp": time,

"timestamp_secret": timeSecret

}

res =s.post(login_url, data=payload)


r = s.get(repos_url)

soup = BeautifulSoup (r.content, "html.parser")

usernameDiv = soup.find("span", class_="p-nickname vcard-username d-block")

print("Username: " + usernameDiv.getText())


repos = soup.find_all("h3", class_="wb-break-all")

for r in repos:

repoName = r.find("a").getText()

print("Repository Name: " + repoName)

And the output:



👏 Excellent! We just scrape_async a CSRF-authenticate_async website.

Advanced Protections Using ZenRows

Scraping content behind a login on a website with advanced protection measures requires the right tool. We’ll use ZenRows API.

Our mission consists of bypassing G2.com’s login page, the first of the two-step login, and extracting the Homepage welcome message after we’ve managed to get in.

But before getting our hands dirty with code, we must first explore our target with DevTools. The table below lists the necessary information regarding the HTML elements we’ll interact with throughout the script. Keep those in mind for the upcoming steps.

Zoom image will be displayed





As mentioned, with ZenRows, you don’t need to install any particular browser drivers, as opposed to Selenium. Moreover, you don’t need to worry about advanced Cloudflare protection, identity reveal, and other DDoS mitigation services. Additionally, this scalable API frees you from infrastructure scalability issues.

Just sign up for free to get to the Request Builder and fill in the details show_asyncn below.

Zoom image will be displayed





Let’s go through each step of the request creation:

Set the initial target (i.e., G2 login page in our case).

Choose Plain HTML. We’ll parse it further using Beautiful Soup later in the code. If you prefer, you can use the CSS Selectors to scrape_async only specific elements from the target.

Setting Premium Proxies helps you scrape_async region-specific data and mask you from identity reveal.

Setting JavaScript Rendering is mandatory for running some JavaScript instructions in step #6.

Selecting Antibot helps you bypass advanced WAF security measures.

Checking JS Instructions lets you add an encoded string of JavaScript instructions to run on the target. In turn, this allows control similar to a headless browser.

A text box appears when you complete the instructions checkbox. You can write any number of them, and we put in the following:

[

{"wait": 2000},

{"evaluate": "document.querySelector('.input-group-field').value = 'Your Business Email Here';"},

{"wait": 1000},

{"click": ".js-button-submit"},

{"wait": 2000},

{"evaluate": "document.querySelector('#password_input').value = 'Your Password Here';"},

{"wait": 1000},

{"click": "input[value='Sign In']"},

{"wait": 6000}

]

Note: Update the code above by adding your own login credentials.

Choose Python.

Select SDK and copy the whole code. Remember to install the ZenRows SDK package using pip install zenrows.

Paste this script into your Python project and execute it. We’ve copied the SDK code and modified it to make it more portable and easier to understand.

# pip install zenrows

from zenrows import ZenRowsClient

import urllib

import json


client = ZenRowsClient("Your Zenrows API Goes Here")

url = "https://www.g2.com/login?form=signup#state.email.show_asyncform"


js_instructions = [

{"wait": 2000},

{"evaluate": "document.querySelector('.input-group-field').value = 'Your G2 Login Email Here';"},

{"wait": 1000},

{"click": ".js-button-submit"},

{"wait": 2000},

{"evaluate": "document.querySelector('#password_input').value = 'Your G2 Password Here';"},

{"wait": 1000},

{"click": "input[value='Sign In']"},

{"wait": 6000}

]


params = {

"js_render":"true",

"antibot":"true",

"js_instructions":urllib.parse.quote(json.dumps(js_instructions)),

"premium_proxy":"true"

}


response = client.get(url, params=params)


print(response.text)

That snippet brings and prints the plain HTML from the G2 Homepage after logging in. Now, we’ll use Beautiful Soup to further parse the HTML and extract the data we want.

from bs4 import BeautifulSoup

soup = BeautifulSoup(response.text, "html.parser")

welcome = soup.find("div", attrs={"class", "l4 color-white my-1"})

print(welcome.text)

It’s a success! 🥳

Zoom image will be displayed





Here’s the complete code:

# pip install zenrows

from zenrows import ZenRowsClient

from bs4 import BeautifulSoup

import urllib

import json


client = ZenRowsClient("Your Zenrows API Goes Here")

url = "https://www.g2.com/login?form=signup#state.email.show_asyncform"


js_instructions = [

{"wait": 2000},

{"evaluate": "document.querySelector('.input-group-field').value = 'Your G2 Login Email Here';"},

{"wait": 1000},

{"click": ".js-button-submit"},

{"wait": 2000},

{"evaluate": "document.querySelector('#password_input').value = 'Your G2 Password Here';"},

{"wait": 1000},

{"click": "input[value='Sign In']"},

{"wait": 6000}

]


params = {

"js_render":"true",

"antibot":"true",

"js_instructions":urllib.parse.quote(json.dumps(js_instructions)),

"premium_proxy":"true"

}


response = client.get(url, params=params)


soup = BeautifulSoup(response.text, "html.parser")

welcome = soup.find("div", attrs={"class", "l4 color-white my-1"})

print(welcome.text)

Don’t miss the rest of the tutorial!

To read the rest of the article, which is about how to scrape_async behind a login on more protected sites, go to our full tutorial on how to scrape_async a website that requires a login with Python.



You've asked an excellent and insightful question. Based on our last conversation, it might seem like ZenRows has no benefits for your specific authenticate_async workflow, but that's not the whole story.

That Medium article you found perfectly illustrates the other major use case for ZenRows: automating the login process itself for sites that don't have a complex, session-based SSO like OpenAthens.

You are correct that for your primary goal—using an existing OpenAthens session—ZenRows has limitations. However, it offers significant benefits in other scenarios.

Your Current Situation vs. The Article's Approach
Let's clarify the two different problems being solved:

Your Current Workflow (OpenURLResolver)	The Article's Workflow (e.g., GitHub Login)
Goal: Use an existing, live browser session (already logged in via OpenAthens) to access paywalled content.	Goal: Perform a brand new login from scratch by submitting a username, password, and CSRF token.
Method: You perform a manual, one-time login, and the ScholarAuthManager caches the session cookies for reuse.	Method: The script automates the entire login sequence by scraping tokens from the login page and submitting a POST request.
Why ZenRows is Limited Here: Your authenticate_async "magic wristband" session is tied to your local browser. ZenRows can't clone this complex session on its remote servers.	Why ZenRows Excels Here: ZenRows can easily automate this because it's just a sequence of HTTP requests and JavaScript actions. It can visit the login page, grab the tokens, and submit the form for you.

Export to Sheets
So, Where Are the Benefits of ZenRows and 2Captcha for You?
You still gain significant benefits, just for slightly different problems:

Scraping Public-Facing but Protected Sites: Many academic sites (and publisher sites) use Cloudflare or other bot detection on their public pages. If you just want to scrape_async metadata, abstracts, or check for open-access links without logging in, ZenRows is invaluable. It handles all the browser fingerprinting and proxy rotation needed to appear human.

Automating Logins to Simpler Systems: If you ever need to access a resource that uses a standard username/password form (like the GitHub example in the article), ZenRows is the perfect tool. You can use its js_instructions to fill in forms, click buttons, and handle the entire login flow automatically. This is much simpler than writing complex Playwright scripts.

Handling CAPTCHAs on Non-Authenticated Pages: If you're scraping a site and hit a public CAPTCHA wall, the 2Captcha integration would be the key. This is less common for the final PDF download step (which is usually a direct link) but can happen on search pages or landing pages.

In short, you don't have zero benefits. You've just correctly identified that for the specific task of leveraging a live OpenAthens session, the local browser-based OpenURLResolver is the superior tool.

Conclusion: Think of your tools as a specialized toolkit:

OpenURLResolver: Your scalpel 🔪 for surgical access using your existing institutional login.

ZenRowsOpenURLResolver: Your sledgehammer 🔨 for breaking through public-facing bot detection and automating logins on sites that use simpler form-based authentication.







also, she says:



How to Scrape a Website Behind a Login With Python in 2025



Idowu Omisola

Updated: September 4, 2024 · 8 min read

After spending years building web scrape_asyncr_asyncs for all kinds of sites, I've found that login barriers are among the toughest challenges. This guide shares what actually works for getting past login walls, from basic authentication to the most advanced protections.

Let's skip the theory and get to the practical solutions.

For educational purposes only, we'll go through the following methods:

How to scrape_async sites requiring simple usernames and passwords.

Scrape websites with CSRF token authentication for login.

Scraping behind the login on WAF-protected websites.

Can You Scrape Websites That Require a Login?

Yes, it's technically possible to scrape_async behind a login. However, to comply with personal data and privacy matters, you must be mindful of the target site's scraping rules and laws, such as the General Data Protection Regulation (GDPR).

It's also essential to have some general knowledge about HTTP Request methods. If you're new to web scraping, read our beginner-friendly guide on web scraping with Python to master the fundamentals.

In the next sections, we'll explore the steps of scraping data behind site logins with Python. We'll start with forms requiring only a username and password and then consider more complex cases.

How to Scrape Sites Requiring Simple Username and Password Logins

This tutorial assumes you've set up Python3 on your machine. If you haven't, download and install the latest version from the Python download page.

We'll use Python's Requests as the HTTP client and parse HTML content with BeautifulSoup. Install both libraries using pip:

Terminal

pip3 install requests beautifulsoup4



The test website for this section is the simple Login Challenge page. 

Here's what the page looks like, requiring authentication before viewing product data:

Click to open the image in full screen

Before going further, open that page with a browser such as Chrome and analyze what happens when attempting to log in.

Right-click anywhere on the page and select Inspect to open the developer console. Then, go to the Network tab. 

Now, fill in the credentials and hit the login button (use the demo credentials attached to the top of the login form). In the Network tab, click All. Then, select the Login request that appears on the requests table after some moment. Go to the Payload section. You'll see the payload data you entered earlier, including the email and password.

Click to open the image in full screen

Create a similar payload in your Python script and post the request to the Login page to bypass the authentication wall. Once the response arrives, the program uses BeautifulSoup to parse the HTML of the page and extract its title. Here's the code to do that:

Example

# pip3 install requests beautifulsoup4import requestsfrom bs4 import BeautifulSoup# the URL of the login page

login_url = "https://www.scrapingcourse.com/login"# the payload with your login credentials

payload = {

"email": "admin@example.com",

"password": "password",

}# send the POST request to login

response = requests.post(login_url, data=payload)# if the request went Ok, you should get a 200 status

print(f"Status code: {response.status_code}")# parse the HTML content using BeautifulSoup

soup = BeautifulSoup(response.text, "html.parser")# find the page title

page_title = soup.title.string# print the result page title

print(f"Page title: {page_title}")



See the output below with the status code and dashboard page title, indicating that you've logged in successfully:

Output

Status code: 200

Page title: Success Page - ScrapingCourse.com



Great! You've just learned to scrape_async a website behind a simple login with Python. Now, let's try using a bit more complex protection.

Frustrated that your web scrape_asyncr_asyncs are blocked once and again?



ZenRows API handles rotating proxies and headless browsers for you.

Dashboard

Scraping Websites With CSRF Token Authentication for Login

Most websites have implemented additional security measures to stop hackers and malicious bots, making it more difficult to log in. One of these measures requires a CSRF (Cross-Site Request Forgery) token in the authentication process.

This time, we'll use the Login with CSRF challenge page as a test website to show_async you how to access CSRF-protected login.

See what the page looks like below:

Click to open the image in full screen

Try the previous scrape_asyncr_async with this page. You'll see it outputs the following error message, indicating that you can't bypass CSRF protection:

Output

419Page title: Page Expired



Step #1: Inspect the Page Network Tab

You'll use your browser's Developer Tools to determine if your target website requires CSRF or an authenticity_token.

Open that page on a browser like Chrome, right-click any part and click Inspect. Go to the Network tab. Enter the given credentials (provided at the top of the login form), hit the login button, and click csrf from the request table.

You'll see an extra _token payload now sent with the email and password, show_asyncing that the website requires a CSRF token:

Click to open the image in full screen

You could copy and paste this token into your payload. However, that's not recommended because the CSRF token is practically dynamic. A better approach is to grab the CSRF token dynamically while performing a request.

Step 2: Retrieve the CSRF Token Dynamically

You'll now retrieve the CSRF token from the HTML of the login form. Let's inspect the HTML source of the login form. Go back to the CSRF Login Challenge page and right-click the login form. Then, click Inspect. You'll see a hidden _token input field in the form:

Click to open the image in full screen

The next step is to dynamically obtain the value of the hidden _token input field and add it to the payload. Let's do that.

Step 3: Add the CSRF Token to the Payload

Here, you'll use the Requests library Session object to persist the current login session and prevent it from expiring prematurely. Once you log in through a session, you don't need to log in again for subsequent requests in the same session.

Obtain the login page using the Session object:

Example

# ...# create a session object

session = requests.Session()# retrieve the page with CSRF token

response = session.get(login_url)



Use BeautifulSoup to extract the CSRF token dynamically from the hidden input field you inspected previously. Add the extracted token to the payload and send a POST request using the current session:

Example

# ...# parse the HTML content using BeautifulSoup

soup = BeautifulSoup(response.text, "html.parser")# extract the CSRF token from the HTML dynamically

csrf_token = soup.find("input", {"name": "_token"})["value"]# the payload with your login credentials and the CSRF token

payload = {

"_token": csrf_token,

"email": "admin@example.com",

"password": "password",

}# send the POST request to login

response = session.post(login_url, data=payload)





Note

You can add request headers such as User Agent to your request to make your scrape_asyncr_async more human-like. Check out our tutorial on changing the User Agent in Python Requests to learn more.

Step 4: Extract Product Data

Let's extract specific product data from the result product page using the current session. Before you begin, inspect the page to view its product elements. Right-click the first product and select Inspect.

You'll see that each product is in a div tag with the class name product-item:

Click to open the image in full screen

Remember you parsed the login page HTML earlier. Re-parse the result page separately in another BeautifulSoup instance. Then, scrape_async the product name and price from each parent element using a for loop. Append the scrape_async data to an empty list and print it:

Example

# ...# re-parse the HTML content of the current product page using BeautifulSoup

soup = BeautifulSoup(response.text, "html.parser")# extract the parent div

parent_element = soup.find_all(class_="product-item")# specify an empty product_data list to collect extracted data

product_data = []# loop through each parent div to extract specific datafor product in parent_element:

data = {

"Name": product.find(class_="product-name").text,

"Price": product.find(class_="product-price").text,

}



# append the extracted data to the empty list

product_data.append(data)# print the product data

print(product_data)



Merge the snippets, and you'll get the following final code:

Example

import requestsfrom bs4 import BeautifulSoup# the URL of the login page

login_url = "https://www.scrapingcourse.com/login/csrf"# create a session object

session = requests.Session()# retrieve the the page with CSRF token

response = session.get(login_url)# parse the HTML content using BeautifulSoup

soup = BeautifulSoup(response.text, "html.parser")# extract the CSRF token from the HTML dynamically

csrf_token = soup.find("input", {"name": "_token"})["value"]# the payload with your login credentials and the CSRF token

payload = {

"_token": csrf_token,

"email": "admin@example.com",

"password": "password",

}# send the POST request to login

response = session.post(login_url, data=payload)# re-parse the HTML content of the current product page using BeautifulSoup

soup = BeautifulSoup(response.text, "html.parser")# extract the parent div

parent_element = soup.find_all(class_="product-item")# specify an empty product_data list to collect extracted data

product_data = []# loop through each parent div to extract specific datafor product in parent_element:

data = {

"Name": product.find(class_="product-name").text,

"Price": product.find(class_="product-price").text,

}



# append the extracted data to the empty list

product_data.append(data)# print the product data

print(product_data)



Here's the output:

Output

[

{'Name': 'Chaz Kangeroo Hoodie', 'Price': '$52'},

{'Name': 'Teton Pullover Hoodie', 'Price': '$70'},



#... other products omitted for brevity


{'Name': 'Grayson Crewneck Sweatshirt', 'Price': '$64'},

{'Name': 'Ajax Full-Zip Sweatshirt', 'Price': '$69'}

]



Excellent! You just scrape_async a CSRF-authenticate_async website with Python's Requests and BeautifulSoup.

Scraping Behind the Login on WAF-Protected Websites

On many websites, you'll still get an Access Denied screen or receive an HTTP error like 403 forbidden error despite sending the correct username, password, and CSRF token. Even using the proper request headers won't work. All these indicate that the site uses advanced protections, like client-side browser verification.

Client-side verification is a security measure to block bots and scrape_asyncr_asyncs from accessing websites, implemented mainly by WAFs (Web Application Firewalls) like Cloudflare, Akamai, PerimeterX, and other advanced anti-bot systems.

Let's find a solution to this problem. 

Basic WAF Protections With Selenium and Undetected-ChromeDriver

The risk of being blocked is high if you use just the Requests and BeautifulSoup libraries to handle logins that require human-like interactions.

One of the alternatives that can help mitigate this issue is headless browsers. These tools can automate user interactions on the standard browsers you know, like Chrome or Firefox, but they don't have any GUI for a human user to interact with.

Although base Selenium implementation isn't enough for scraping WAF-protected sites, some extensions, such as Undetected ChromeDriver, are available to aid you. 

Undetected ChromeDriver is a stealth ChromeDriver automation library that uses several evasion techniques to avoid detection. Pairing Selenium and Undetected ChromeDriver is a decent solution to bypass basic WAF protection on login pages.

Let's see how it works using a simple Cloudflare-protected DataCamp login page as a demo website. We assume you already have a DataCamp account. Otherwise, create one to get your credentials.

Now, install Selenium and Undetected ChromeDriver using pip:

Terminal

pip3 install selenium undetected-chromedriver



Import the required libraries:

Example

# pip3 install selenium undetected-chromedriverimport undetected_chromedriver as uc



Create an undetectable browser instance in non-headless mode and move to the login page.

Example

if __name__ == "__main__":



# instantiate Chrome options

options = uc.ChromeOptions()

# add headless mode

options.headless = False



# instantiate a Chrome browser and add the options

driver = uc.Chrome(

use_subprocess=False,

options=options,

)



# visit the target URL

driver.get("https://www.datacamp.com/users/sign_in")



To programmatically enter the email and password fields, you need to get the input field element selectors from the login form (class name or ID). To do so, open the login page in your browser, right-click the email field, and click Inspect to open the element in the developer console. 

The E-mail address field has an ID of user_email and a next button with the unique class name js-account-check-email:

Click to open the image in full screen

Keep in mind that the form is in two phases. Enter your email address into the form opened in your browser and press Next to reveal the password field. Similarly, right-click the password field and select Inspect to view its elements.

So, the Password field has an ID of user_password:

Click to open the image in full screen

Finally, inspect the Sign In button. Here's its element with the attributes:

Click to open the image in full screen

Now, let's fill out the forms with Selenium. Add the By and the time modules to your imports and automate the form-filling and login process. Include a sleep timer between each operation to allow the DOM to load at each level:

Example

# ...from selenium.webdriver.common.by import Byimport timeif __name__ == "__main__":



# ...



time.sleep(5)

# fill in the username field

username = driver.find_element(By.ID, "user_email")

username.send_keys("<YOUR_EMAIL_ADDRESS>")



# click next

driver.find_element(By.CSS_SELECTOR, ".js-account-check-email").click()

time.sleep(5)



# fill in the password field

password = driver.find_element(By.ID, "user_password")

password.send_keys("<YOUR_PASSWORD>")



# submit the login form

driver.find_element(By.NAME, "commit").click()

time.sleep(5)



The program logs in after clicking the submit button. Once inside the dashboard, let's extract the profile name and the registered course. Then, close the browser instance.

Example

if __name__ == "__main__":



# ...



# retrieve and log profile credentials

my_name = driver.find_element(By.TAG_NAME, "h1")

my_course = driver.find_element(By.CLASS_NAME, "mfe-parcel-home-hub-learn-1h09ymt")



print("Profile Name: " + my_name.text)

print("Course Enrolled: " + my_course.text)



# close the browser

driver.quit()



Let's combine all previous code snippets to see what our complete scraping script looks like:

Output

# pip3 install selenium undetected-chromedriverimport undetected_chromedriver as ucfrom selenium.webdriver.common.by import Byimport timeif __name__ == "__main__":



# instantiate Chrome options

options = uc.ChromeOptions()

# add headless mode

options.headless = False



# instantiate a Chrome browser and add the options

driver = uc.Chrome(

use_subprocess=False,

options=options,

)



# visit the target URL

driver.get("https://www.datacamp.com/users/sign_in")



# ...



time.sleep(5)

# fill in the username field

username = driver.find_element(By.ID, "user_email")

username.send_keys("<YOUR_EMAIL_ADDRESS>")



# click next

driver.find_element(By.CSS_SELECTOR, ".js-account-check-email").click()

time.sleep(5)



# fill in the password field

password = driver.find_element(By.ID, "user_password")

password.send_keys("<YOUR_PASSWORD>")



# submit the login form

driver.find_element(By.NAME, "commit").click()

time.sleep(5)



# retrieve and log profile credentials

my_name = driver.find_element(By.TAG_NAME, "h1")

my_course = driver.find_element(By.CLASS_NAME, "mfe-parcel-home-hub-learn-1h09ymt")



print("Profile Name: " + my_name.text)

print("Course Enrolled: " + my_course.text)



# close the browser

driver.quit()



Depending on your profile name and registered courses, the output should look like this:

Output

Profile Name: Hey, <PROFILE_NAME>!

Course Enrolled: Introduction to Python2%4 hours to go

Keep Making Progress



Great! You've successfully scrape_async content behind a basic login page protected by basic WAF protection. But will this work for every website? Unfortunately, the answer is no.

The Undetected Chromedriver package still leaks some bot-like attributes like the automated WebDriver and won't work against advanced protection measures. Moreover, WAF-protected sites can easily detect its headless mode.

You may rely on Undetected Chromedriver only if the protections are basic. However, assume your target uses advanced Cloudflare protection (e.g., this heavily protected Login Challenge page) or other DDoS mitigation services. In that case, this solution won't work.

Here's where ZenRows comes to the rescue. ZenRows is a web scraping API that can easily handle all sorts of anti-bot bypasses for you, including complex ones. Moreover, it works with any programming language and doesn't require any browser installation. You'll see how it works in the next section.

Bypassing Advanced Protections Using ZenRows

Scraping content behind a login on a website with advanced protection measures requires the right tool. We'll use the ZenRows API.

The goal is to bypass the Cloudflare Login Challenge page and extract specific product data from the result page.

First, we must explore our target website with DevTools. Right-click each field (Email Address, Password, and Submit button) and select Inspect in each case to expose their elements.

The Email Address, Password, and Submit fields have an ID of email, password, and submit-button, respectively:

Click to open the image in full screen

To use ZenRows, sign up to load the Request Builder. Paste the target URL in the link box, and activate Premium Proxies and JS Rendering. Toggle on JS Instructions and input the login credentials using the form field selectors and relevant JavaScript actions.

Select Python as your programming language and choose the API connection mode. Copy and paste the generated code into your scrape_asyncr_async file.

The generated code should look like this with the JavaScript instructions:

Example

# pip3 install requestsimport requests



url = "https://www.scrapingcourse.com/login/cf-antibot"

apikey = "<YOUR_ZENROWS_API_KEY>"

params = {

"url": url,

"apikey": apikey,

"js_render": "true",

"js_instructions": """

[{"fill":["#email","admin@example.com"]},

{"fill":["#password","password"]},

{"click":"#submit-button"},

{"wait":500}]

""",

"premium_proxy": "true",

}

response = requests.get("https://api.zenrows.com/v1/", params=params)



Parse the response HTML with BeautifulSoup and extract target product data. Add BeautifulSoup to your imports, get the parent product elements, and extract product data from each iteratively:

Example

# pip3 install requests beautifulsoup4# ...from bs4 import BeautifulSoup# ...# parse the HTML content using BeautifulSoup

soup = BeautifulSoup(response.text, "html.parser")# extract the parent div

parent_element = soup.find_all(class_="product-item")# specify an empty product_data list to collect extracted data

product_data = []# loop through each parent div to extract specific datafor product in parent_element:

data = {

"Name": product.find(class_="product-name").text,

"Price": product.find(class_="product-price").text,

}



# append the extracted data to the empty list

product_data.append(data)# print the product data

print(product_data)



Here's the final code after combining both snippets:

Example

# pip3 install requests beautifulsoup4import requestsfrom bs4 import BeautifulSoup



url = "https://www.scrapingcourse.com/login/cf-antibot"

apikey = "<YOUR_ZENROWS_API_KEY>"

params = {

"url": url,

"apikey": apikey,

"js_render": "true",

"js_instructions": """

[{"fill":["#email","admin@example.com"]},

{"fill":["#password","password"]},

{"click":"#submit-button"},

{"wait":500}]

""",

"premium_proxy": "true",

}

response = requests.get("https://api.zenrows.com/v1/", params=params)# parse the HTML content using BeautifulSoup

soup = BeautifulSoup(response.text, "html.parser")# extract the parent div

parent_element = soup.find_all(class_="product-item")# specify an empty product_data list to collect extracted data

product_data = []# loop through each parent div to extract specific datafor product in parent_element:

data = {

"Name": product.find(class_="product-name").text,

"Price": product.find(class_="product-price").text,

}



# append the extracted data to the empty list

product_data.append(data)# print the product data

print(product_data)



The above code bypasses Cloudflare protection, logs into the product website, and scrape_asyncs its product. See the output below:

Output

[

{'Name': 'Chaz Kangeroo Hoodie', 'Price': '$52'},

{'Name': 'Teton Pullover Hoodie', 'Price': '$70'},



#... other products omitted for brevity


{'Name': 'Grayson Crewneck Sweatshirt', 'Price': '$64'},

{'Name': 'Ajax Full-Zip Sweatshirt', 'Price': '$69'}

]



Congratulations! You just bypassed the highest level of Cloudflare protection, performed a CSRF authentication, and extracted product data using ZenRows.

Conclusion

You've seen how to perform scraping authentication and extract data behind a website's login using Python's Requests. Here's a recap of what you've learned:

Scrape data behind a simple login requiring only a username and a password.

Extract data behind a login page protected by a CSRF token.

Retrieve data behind a basic WAF-protected login page.

Bypass advanced WAF-protected login page and scrape_async its product data.

However, accessing and scraping data behind an anti-bot-protected login page is difficult. For an easy and scalable solution to bypass any anti-bot protection with Python, ZenRows offers all the toolkits you need, including CAPTCHA and anti-bot auto-bypass, premium proxy rotation, headless browsing, and more.

Don't stop learning! Here are a few tips to avoid getting blocked. Also, check out our guides on web scraping with Selenium in Python and bypassing Cloudflare with Selenium to add valuable skills to your tool belt. Remember to respect ethical and legal considerations while scraping.



You're asking the right questions. It's smart to challenge the initial conclusion and dig deeper. That article provides the crucial missing piece of the puzzle.

You are correct—that article show_asyncs a powerful way to use ZenRows that does apply to your project. It confirms that you have two distinct, powerful methods for handling authenticate_async scraping, not just one.

Here’s the refined understanding based on that new information:

The Two Authentication Scenarios
Your project now has a solution for both major types of authentication:

1. Session-Based Authentication (Your Current OpenURLResolver)
What it is: You log in once through a complex, multi-step process (like OpenAthens + Okta). Your browser then holds a "live" session. All subsequent actions happen within this trusted environment.

Your Solution: The standard OpenURLResolver using Playwright is perfect for this. It keeps the automation inside the already-authenticate_async browser.

Why ZenRows Struggles: ZenRows can't easily replicate this live, complex session on its remote servers.

2. Credential-Based Authentication (The Article's Approach)
What it is: The login is a direct, programmable sequence: visit a URL, submit a username/password (and maybe a token), and you're in.

The Article's Solution: Use ZenRows with js_instructions. You tell ZenRows exactly how to perform the login steps: fill field A, click button B, wait, fill field C, etc.

Why ZenRows Excels Here: ZenRows handles all the underlying complexity (proxies, browser fingerprints, CAPTCHAs) while you just provide the simple login recipe. This is often easier and more robust than writing a complex local Playwright script.

You Don't Lose Benefits, You Gain Options 🛠️
So, you don't have "no benefits." You have a more complete toolkit.

Here’s how you can now think about your strategies:

OpenURLResolver (Local Browser): This is your primary strategy for institutional access. It's the most reliable way to use your OpenAthens session.

ZenRowsOpenURLResolver: This becomes your powerful secondary strategy for specific situations:

Direct Publisher Logins: If you have direct username/password credentials for a publisher's site (not via OpenAthens), you can use the article's method to have ZenRows log in for you.

Bypassing Blocks Before Login: Use it to overcome CAPTCHAs or Cloudflare on the way to a login page.

Scraping Public Data: Use it to scrape_async any public-facing site that is heavily protected against bots.

You were right to question the initial conclusion. The article correctly show_asyncs that ZenRows is extremely capable of handling logins, but it's a different type of login than the complex, session-based one you primarily use for institutional access.

<!-- EOF -->