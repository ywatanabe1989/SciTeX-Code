# 2Captcha Integration Summary

## Overview
SciTeX Scholar now supports automated CAPTCHA solving through 2Captcha integration. This helps overcome CAPTCHA challenges that may appear during paper downloads or web scraping.

## Configuration

### 1. Set up 2Captcha API Key
Export your 2Captcha API key as an environment variable:
```bash
export SCITEX_SCHOLAR_2CAPTCHA_API_KEY="36d184fbba134f828cdd314f01dc7f18"
```

### 2. Enable CAPTCHA Solving (Optional)
CAPTCHA solving is enabled by default when the API key is set. To disable:
```bash
export SCITEX_SCHOLAR_ENABLE_CAPTCHA_SOLVING=false
```

## Implementation Details

### ScholarConfig Updates
Added two new configuration fields to `_Config.py`:
- `twocaptcha_api_key`: Stores the 2Captcha API key
- `enable_captcha_solving`: Boolean flag to enable/disable CAPTCHA solving

### ZenRows Integration
The `ZenRowsOpenURLResolver` now supports automatic CAPTCHA solving:
- Detects when 2Captcha API key is available
- Adds `solve_captcha` instructions to ZenRows requests
- Handles reCAPTCHA and Cloudflare Turnstile automatically

### Key Features
1. **Automatic Detection**: Checks for 2Captcha API key in environment
2. **Native ZenRows Integration**: Uses ZenRows' built-in 2Captcha support
3. **Multiple CAPTCHA Types**: Supports reCAPTCHA v2/v3, Cloudflare Turnstile
4. **Seamless Operation**: No manual intervention required

## Usage Example

```python
from scitex.scholar import Scholar

# 2Captcha will be used automatically if API key is set
scholar = Scholar()

# Download PDFs - CAPTCHAs will be solved automatically
papers = scholar.search("machine learning")
scholar.download_pdfs(papers)
```

## ZenRows Integration Setup
For the 2Captcha integration to work with ZenRows:
1. Log in to your ZenRows dashboard
2. Go to Integrations page
3. Click on 2Captcha integration
4. Enter your 2Captcha API key
5. Save the integration

## Benefits
- Automated CAPTCHA solving during PDF downloads
- Higher success rate for accessing protected content
- No manual intervention required
- Works with institutional access workflows

## Notes
- The integration uses ZenRows' native 2Captcha support, not a custom implementation
- CAPTCHA solving adds a small delay (5-30 seconds) to requests
- Costs apply per CAPTCHA solved through 2Captcha service
- The TwoCaptchaHandler class was created but is not used in favor of ZenRows' native integration