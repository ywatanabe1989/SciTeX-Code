# ZenRows Troubleshooting Guide

## Overview
This guide helps resolve common issues with the ZenRows integration in SciTeX Scholar module.

## Common Issues and Solutions

### 1. ZenRows API Key Not Detected

**Symptom**: ZenRows strategy not initialized, downloads fall back to other methods

**Solution**:
```bash
# Set environment variable
export SCITEX_SCHOLAR_ZENROWS_API_KEY="your-api-key"

# Verify it's set
echo $SCITEX_SCHOLAR_ZENROWS_API_KEY
```

**Python verification**:
```python
import os
print(os.environ.get("SCITEX_SCHOLAR_ZENROWS_API_KEY"))
```

### 2. 400 Bad Request Errors

**Symptom**: `ZenRows request failed: 400`

**Common Causes**:
- Invalid API key
- Session ID too large (must be 1-9999)
- Invalid parameters

**Solutions**:
1. Verify API key is correct
2. Check session ID generation:
   ```python
   # Correct: 1-9999
   session_id = str(random.randint(1, 9999))
   ```
3. Remove unsupported parameters like `wait_for`

### 3. 422 Unprocessable Entity

**Symptom**: `Could not get content. try enabling javascript rendering`

**Solution**: Always enable JavaScript rendering for academic publishers:
```python
params = {
    "url": url,
    "apikey": api_key,
    "js_render": "true",  # Required for most publishers
    "premium_proxy": "true"
}
```

### 4. No PDF Link Found

**Symptom**: `No PDF link found in page`

**Common with**: Elsevier, Springer, some Wiley journals

**Solutions**:
1. The paper may require additional authentication beyond ZenRows capabilities
2. Try with authenticated session cookies from OpenAthens
3. Check if the publisher has a different PDF URL pattern

### 5. Downloaded Content Not PDF

**Symptom**: `Downloaded content is not a PDF`

**Common with**: Wiley journals

**Causes**:
- Redirected to login page
- Downloaded HTML instead of PDF
- Publisher-specific protections

**Solutions**:
1. Check the debug HTML file saved in same directory
2. May need publisher-specific handling
3. Consider using OpenAthens authentication first

## Testing ZenRows Integration

### Basic Connectivity Test
```python
import requests

api_key = "your-api-key"
params = {
    "url": "https://httpbin.org/get",
    "apikey": api_key
}

response = requests.get("https://api.zenrows.com/v1/", params=params)
print(f"Status: {response.status_code}")
```

### Test with Real Paper
```python
from scitex.scholar import Scholar

# ZenRows auto-enabled if API key is set
scholar = Scholar()
papers = scholar.download_pdfs(["10.1038/nature12373"])

for paper in papers:
    if paper.pdf_path:
        print(f"✅ Success: {paper.pdf_path}")
    else:
        print("❌ Failed")
```

## Debug Mode

Enable debug logging to see detailed ZenRows requests:

```python
from scitex.scholar._Config import ScholarConfig
from scitex import logging

# Enable debug logging
logging.configure_logging(level=logging.DEBUG)

# Create config with debug mode
config = ScholarConfig(debug_mode=True)
scholar = Scholar(config)
```

## Publisher-Specific Issues

### Elsevier
- Often requires institutional authentication
- May redirect to auth.elsevier.com
- Consider using OpenAthens + ZenRows combination

### Wiley
- PDF URLs found but content blocked
- May return HTML login page instead of PDF
- Check for different PDF URL patterns

### PNAS
- Generally works well with ZenRows
- May have rate limiting - add delays between requests

### Nature
- Usually works well
- Large files may take time to download

### Science (AAAS)
- May find supplementary PDFs instead of main article
- Check PDF URL patterns carefully

## Best Practices

1. **Use Session IDs**: Maintain same IP for related requests
   ```python
   # Session persists for 10 minutes
   session_id = str(random.randint(1, 9999))
   ```

2. **Handle Cookies**: Transfer authentication cookies
   ```python
   # Cookies from OpenAthens or other auth
   if session_data and session_data.get("cookies"):
       params["custom_headers"] = "true"
       headers["Cookie"] = cookie_string
   ```

3. **Add Delays**: Respect rate limits
   ```python
   import time
   time.sleep(2)  # Between requests
   ```

4. **Check Response Headers**: Look for useful information
   - `Zr-Cookies`: New cookies to store
   - `Zr-Final-Url`: Actual URL after redirects

## Getting Help

1. Check ZenRows dashboard for API usage and errors
2. Enable debug logging to see full request details
3. Save HTML responses for debugging (`debug_path.write_text(html_content)`)
4. Test with simpler sites first (httpbin.org)
5. Verify network connectivity and proxy settings

## Environment Variables

All ZenRows-related environment variables:
```bash
# Required
export SCITEX_SCHOLAR_ZENROWS_API_KEY="your-api-key"

# Optional proxy settings (if using residential proxies)
export SCITEX_SCHOLAR_ZENROWS_PROXY_USERNAME="username"
export SCITEX_SCHOLAR_ZENROWS_PROXY_PASSWORD="password"
export SCITEX_SCHOLAR_ZENROWS_PROXY_DOMAIN="superproxy.zenrows.com"
export SCITEX_SCHOLAR_ZENROWS_PROXY_PORT="1337"
```