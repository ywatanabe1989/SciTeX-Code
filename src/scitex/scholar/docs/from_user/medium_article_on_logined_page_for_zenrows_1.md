<!-- ---
!-- Timestamp: 2025-07-31 01:21:27
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/docs/medium_article_on_logined_page_for_zenrows.md
!-- --- -->

How to Scrape a Website that Requires a Login with Python
ZenRows
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

To get started, it’s essential to have some general knowledge about HTTP Request Methods. And if web scraping is new for you, read our beginner-friendly guide on web scraping with Python to master the fundamentals.

How Do You Log into a Website with Python?
The first step to scraping a login-protected website with Python is figuring out your target domain’s login type. Some old websites just require sending a username and password. However, modern ones use more advanced security measures. These include:

Client-side validations
CSRF tokens
Web Application Firewalls (WAFs)
Keep reading to learn the techniques to get around these strict security protections.

How Do You Scrape a Website behind a Login in Python?
Time to explore each step of scraping data behind site logins with Python. We’ll start with forms requiring only a username and password and then increase the difficulty progressively.

Remember that the methods show_asynccased in this tutorial are for educational purposes only.

Three, two, one… let’s code!

Sites Requiring a Simple Username and Password Login
We assume you’ve already set up Python 3 and Pip; otherwise, you should check a guide on properly installing Python.

As dependencies, we’ll use the Requests and Beautiful Soup libraries. Start by installing them:

pip install requests beautifulsoup4
Tip: If you need any help during the installation, visit this page for Requests and this one for Beautiful Soup.

Now, go to Acunetix’s User Information. This is a test page explicitly made for learning purposes and protected by a simple login, so you’ll be redirected to a login page.

Before going further, we’ll analyze what happens when attempting a login. For that, use test as a username and password, hit the login button and check the network section on your browser.

Zoom image will be displayed

Submitting the form generates a POST request to the User Information page, with the server responding with a cookie and fulfilling the requested section. The screenshot below show_asyncs the headers, payload, response, and cookies.

Zoom image will be displayed

The following scraping script will bypass the auth wall. It creates a similar payload and posts the request to the User Information page. Once the response arrives, the program uses Beautiful Soup to parse the response text and print the page name.

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

To find out if your target website requires CSRF or an authenticity_token, make the most of your browser’s Developer Tools. It doesn’t matter whether you use Safari, Chrome, Edge, Chromium, or Firefox since all provide a similar set of powerful tools for developers. To learn more, we suggest checking out the Chrome DevTools or Mozilla DevTools documentation.

Let’s dive into scraping GitHub!

Step #1: Log into a GitHub Account
GitHub is one of the websites that use CSRF token authentication for logins. We’ll scrape_async all the repositories in our test account for demonstration.

Open a web browser (we use Chrome) and navigate to GitHub’s login page. Now, press the F12 key to see the DevTools window in your browser and inspect the HTML to check if the login form element has an action attribute:

Zoom image will be displayed

Select the Network tab, click the Sign in button, then fill in and submit the form yourself. This’ll perform a few HTTP requests, visible in this tab.

Zoom image will be displayed

Let’s look at what we’ve got after clicking on the Sign in button. To do so, explore the POST request named session that has just been sent.

In the Headers section, you’ll find the full URL where the credentials are posted. We’ll use it to send a login request in our script.

Zoom image will be displayed

Step #2: Set up Payload for the CSRF-protected Login Request
Now, you might be wondering how we know there’s CSRF protection. The answer is in right front of you:

Navigate to the Payload section of the session request. Notice that, in addition to login and password, we have payload data for the authentication token and the timestamps. This auth token is the CSRF token and must be passed as a payload along the login POST request.

Zoom image will be displayed

Manually copying these fields from the Payload section for each new login request will be tedious. Instead, we’ll write code to get that programmatically.

Let’s go back to the HTML source of the login form. You’ll see all the Payload fields are present in the form.

Zoom image will be displayed

The following script gets the CSRF token, timestamp, and timestamp_secret from the login page:

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
We can now populate the payload dictionary for our Python login request as:

payload = { 
 "authenticity_token": token, 
 "login": login, 
 "password": password, 
 "timestamp": time, 
 "timestamp_secret": timeSecret 
}
Note: If you can’t find the CSRF token on the HTML, it’s probably saved in a cookie. In Chromium-based browsers, go to the Application tab in the DevTools. Then, in the left panel, search for cookies and select the domain of your target website.

Zoom image will be displayed

There you have it!

Step #3: Set Headers
It’s possible to access auth-wall websites by sending a POST request with the payload. However, using this method alone won’t be enough to scrape_async sites with advanced security measures since they’re usually smart enough to identify non-human behavior. Thus, implementing measures to make the scrape_asyncr_async appear more human-like is necessary.

Get ZenRows’s stories in your inbox
Join Medium for free to get updates from this writer.

Enter your email
Subscribe
The most realistic way to do this is by adding actual browser headers to our requests. Copy the ones from the Headers tab of your browser request and add them to the Python login request. Try this guide if you need to learn more about header settings for requests.

Alternatively, you can use a web scraping API like ZenRows to get around those annoying anti-bot systems for you.

Step #4: The Login in Action
This is our lucky day since adding headers for GitHub is unnecessary, so we’re ready to send our login request through Python:

res = s.post(login_url, data=payload) 
print(res.url)
If the login’s successful, our output’ll be https://github.com/. Otherwise, we’ll get https://github.com/session.

👍 Amazing, we just nailed a CSRF-protected login bypass! Let’s now scrape_async the data in the protected git repositories.

Step #5: Scrape Protected GitHub Repositories
Recall that we began an earlier code with the with requests.session() as s: statement, which creates a request session. Once you log in through a request, you don’t need to re-login for the subsequent requests in the same session.

It’s time to get to the repositories. Generate a GET, then parse the response using Beautiful Soup.

repos_url = "https://github.com/" + login + "/?tab=repositories" 
r = s.get(repos_url) 
soup = BeautifulSoup(r.content, "html.parser")
We’ll extract the username and a list of repositories.

For the former, navigate to the repositories page in your browser, then right-click on the username and select Inspect Element. The information’s contained in a span element, with the CSS class named p-nickname vcard-username d-block inside the <h1> tag.

Zoom image will be displayed

While for the latter, you need to right-click on any repository name and select Inspect Element. The DevTools window will display the following:

Zoom image will be displayed

The repositories’ names are inside hyperlinks in the <h3> tag with the class wb-break-all. Ok, we have enough knowledge of the target elements now, so let’s extract them:

usernameDiv = soup.find("span", class_="p-nickname vcard-username d-block") 
print("Username: " + usernameDiv.getText()) 
repos = soup.find_all("h3",class_="wb-break-all") 
for r in repos: 
 repoName = r.find("a").getText() 
 print("Repository Name: " + repoName)
Since it’s possible to find multiple repositories on the target web page, the script uses the find_all() method to extract all. For that, the loop iterates through each <h3> tag and prints the text of the enclosed <a> tag.

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
Scraping content behind a login on a website with advanced protection measures requires the right tool. We’ll use ZenRows API.

Our mission consists of bypassing G2.com’s login page, the first of the two-step login, and extracting the Homepage welcome message after we’ve managed to get in.

But before getting our hands dirty with code, we must first explore our target with DevTools. The table below lists the necessary information regarding the HTML elements we’ll interact with throughout the script. Keep those in mind for the upcoming steps.

Zoom image will be displayed

As mentioned, with ZenRows, you don’t need to install any particular browser drivers, as opposed to Selenium. Moreover, you don’t need to worry about advanced Cloudflare protection, identity reveal, and other DDoS mitigation services. Additionally, this scalable API frees you from infrastructure scalability issues.

Just sign up for free to get to the Request Builder and fill in the details show_asyncn below.

Zoom image will be displayed

Let’s go through each step of the request creation:

Set the initial target (i.e., G2 login page in our case).
Choose Plain HTML. We’ll parse it further using Beautiful Soup later in the code. If you prefer, you can use the CSS Selectors to scrape_async only specific elements from the target.
Setting Premium Proxies helps you scrape_async region-specific data and mask you from identity reveal.
Setting JavaScript Rendering is mandatory for running some JavaScript instructions in step #6.
Selecting Antibot helps you bypass advanced WAF security measures.
Checking JS Instructions lets you add an encoded string of JavaScript instructions to run on the target. In turn, this allows control similar to a headless browser.
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
Note: Update the code above by adding your own login credentials.

Choose Python.
Select SDK and copy the whole code. Remember to install the ZenRows SDK package using pip install zenrows.
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
That snippet brings and prints the plain HTML from the G2 Homepage after logging in. Now, we’ll use Beautiful Soup to further parse the HTML and extract the data we want.

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
To read the rest of the article, which is about how to scrape_async behind a login on more protected sites, go to our full tutorial on how to scrape_async a website that requires a login with Python.

Thanks for reading! If you liked this guide, kindly click the 👏 clap button below a few times to show_async your support! ⬇⬇

<!-- EOF -->