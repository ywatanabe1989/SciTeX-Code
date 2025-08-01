# Chrome Extension Automation Summary

## Available Methods

### 1. **Policy-based Installation** (Most Reliable)
- Uses Chrome enterprise policies
- Extensions auto-install on browser start
- Requires admin rights to set up
- Works silently in background

### 2. **CRX File Loading**
- Download extension files directly
- Load via command-line flags
- May be blocked by Chrome security

### 3. **Selenium/Puppeteer Automation**
- Simulates user clicking "Add to Chrome"
- Can handle popups and confirmations
- Works with current Chrome versions

### 4. **Developer Mode**
- Load unpacked extensions
- Requires manual enable of dev mode
- Good for testing

### 5. **Browser Profile Persistence**
- Install once, reuse profile
- Extensions persist across sessions
- Most practical for automation

## Recommended Approach for SciTeX Scholar

```bash
# One-time setup: Install extensions to persistent profile
python /home/ywatanabe/proj/SciTeX-Code/.dev/chrome_extension_automation.py

# Then use the profile in your automation
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--user-data-dir=/home/ywatanabe/.scitex/scholar/chrome_profile")
driver = webdriver.Chrome(options=options)
```

## Quick Start

1. **Install extensions once** using any method
2. **Save the Chrome profile** with extensions installed
3. **Reuse profile** in all future automations

This avoids repeatedly installing extensions and maintains their configurations (like 2Captcha API key).