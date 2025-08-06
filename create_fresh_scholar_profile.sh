#!/bin/bash
# Create fresh Scholar Chrome profile for Playwright automation

set -e  # Exit on any error

echo "🧹 Creating fresh Scholar Chrome profile..."

# Define profile directory
PROFILE_DIR="/home/ywatanabe/.scitex/scholar/cache/chrome/extension-fresh"

# Remove existing profile if it exists
if [ -d "$PROFILE_DIR" ]; then
    echo "🗑️ Removing existing profile..."
    rm -rf "$PROFILE_DIR"
fi

# Create fresh profile directory
mkdir -p "$PROFILE_DIR"
echo "📁 Created fresh profile: $PROFILE_DIR"

# Launch Chrome with fresh profile and extension installation pages
echo "🚀 Launching Chrome with fresh profile and extension installation pages..."

google-chrome \
    --user-data-dir="$PROFILE_DIR" \
    --no-sandbox \
    --disable-gpu \
    --disable-dev-shm-usage \
    --new-window \
    --enable-extensions \
    "https://chrome.google.com/webstore/detail/hghakoefmnkhamdhenpbogkeopjlkpoa" \
    "https://chrome.google.com/webstore/detail/bkkbcggnhapdmkeljlodobbkopceiche" \
    "https://chrome.google.com/webstore/detail/ofpnikijgfhlmmjlpkfaifhhdonchhoi" \
    "https://chrome.google.com/webstore/detail/ifibfemgeogfhoebkmokieepdoobkbpo" \
    "https://chrome.google.com/webstore/detail/hlifkpholllijblknnmbfagnkjneagid" &

echo ""
echo "✅ Chrome launched with fresh profile!"
echo "📁 Profile location: $PROFILE_DIR"
echo ""
echo "📋 NEXT STEPS:"
echo "1. Install all 5 extensions by clicking 'Add to Chrome' on each tab"
echo "2. After installation, close Chrome"
echo "3. Test the profile with:"
echo "   google-chrome --user-data-dir=\"$PROFILE_DIR\" --no-sandbox --disable-gpu"
echo ""
echo "🔧 Configure Scholar to use this profile:"
echo "   python -m scitex.scholar open-browser --profile extension-fresh --configure-only"
echo ""
echo "🌐 Extensions to install:"
echo "   • Lean Library (Academic access)"
echo "   • Pop-up Blocker (Ad blocking)"
echo "   • Accept all cookies (Auto-accept cookies)"
echo "   • 2Captcha Solver (CAPTCHA solving)"
echo "   • CAPTCHA Solver (hCaptcha solving)"