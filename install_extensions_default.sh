#!/bin/bash
# Install Scholar extensions in default Chrome profile

echo "🚀 Installing Scholar extensions in default Chrome profile..."

# Find default Chrome profile directory
CHROME_DEFAULT_DIR="$HOME/.config/google-chrome/Default"

if [ ! -d "$CHROME_DEFAULT_DIR" ]; then
    echo "❌ Default Chrome profile not found. Please run 'google-chrome' first to create it."
    exit 1
fi

echo "📁 Using Chrome profile: $CHROME_DEFAULT_DIR"

# Launch Chrome with extension installation URLs
google-chrome \
    --no-sandbox \
    --disable-gpu \
    --new-window \
    "https://chrome.google.com/webstore/detail/hghakoefmnkhamdhenpbogkeopjlkpoa" \
    "https://chrome.google.com/webstore/detail/bkkbcggnhapdmkeljlodobbkopceiche" \
    "https://chrome.google.com/webstore/detail/ofpnikijgfhlmmjlpkfaifhhdonchhoi" \
    "https://chrome.google.com/webstore/detail/ifibfemgeogfhoebkmokieepdoobkbpo" \
    "https://chrome.google.com/webstore/detail/hlifkpholllijblknnmbfagnkjneagid" &

echo ""
echo "🌐 Chrome opened with extension installation pages:"
echo "   • Lean Library (Academic access)"
echo "   • Pop-up Blocker (Ad blocking)"
echo "   • Accept all cookies (Auto-accept cookies)" 
echo "   • 2Captcha Solver (CAPTCHA solving)"
echo "   • CAPTCHA Solver (hCaptcha solving)"
echo ""
echo "📋 INSTRUCTIONS:"
echo "1. Click 'Add to Chrome' on each extension page"
echo "2. After installing all extensions, close Chrome"
echo "3. Run: google-chrome"
echo "4. Your Scholar extensions will be loaded!"
echo ""
echo "🔑 API Keys to configure:"
echo "   2Captcha: 36****************************18" 
echo "   CAPTCHA Solver: sk***********************************33"