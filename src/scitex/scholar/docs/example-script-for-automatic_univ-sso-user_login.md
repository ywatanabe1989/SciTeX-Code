<!-- ---
!-- Timestamp: 2025-07-31 03:39:00
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/docs/skelton_for_automatic_univ-sso-user_login.md
!-- --- -->

Example Login Script
Here's a skeleton of what your AuthenticationManager would do inside the remote browser. You would, of course, load your credentials securely from environment variables.

Python

# This code runs locally but controls the remote browser

# Get the remote browser instance
browser = await browser_manager.get_browser() 
page = await browser.new_page()

# 1. Go to the login portal
await page.goto("https://my-university-login.com")

# 2. Find the institution field and type the name
await page.locator("#institution-search-field").fill("University of Melbourne")

# 3. Wait for the dropdown and click the correct entry
await page.locator("li:has-text('University of Melbourne')").click()

# 4. Fill in username and password
# (Load these securely, e.g., from os.environ)
await page.locator("#username").fill(os.getenv("MY_UNI_USERNAME"))
await page.locator("#password").fill(os.getenv("MY_UNI_PASSWORD"))

# 5. Click the sign-in button
await page.locator("button[type='submit']").click()

# Now the remote browser is at the post-login page, ready for the Okta prompt.
# You approve the prompt on your phone, and the remote browser's page will update.
# The session is now live inside the remote browser.

<!-- EOF -->