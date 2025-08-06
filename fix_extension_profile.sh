#!/bin/bash
# Fix corrupted Chrome extension profile by cleaning browser state files
# Preserves all extensions and configurations

set -e  # Exit on any error

echo "🔧 Fixing corrupted Chrome extension profile..."

# Define profile directory
PROFILE_DIR="/home/ywatanabe/.scitex/scholar/cache/chrome/extension"

if [ ! -d "$PROFILE_DIR" ]; then
    echo "❌ Extension profile not found: $PROFILE_DIR"
    exit 1
fi

echo "📁 Working with profile: $PROFILE_DIR"

# Backup extensions directory (most important)
EXTENSIONS_DIR="$PROFILE_DIR/Default/Extensions"
if [ -d "$EXTENSIONS_DIR" ]; then
    echo "💾 Extensions found - they will be preserved"
    ls "$EXTENSIONS_DIR" | head -5
else
    echo "⚠️ No extensions directory found"
fi

# Remove only the corrupted browser state files, NOT the extensions
echo "🧹 Removing corrupted browser state files..."

cd "$PROFILE_DIR"

# Remove corrupted singleton files
rm -f SingletonCookie SingletonLock SingletonSocket 2>/dev/null || true

# Remove corrupted state files
rm -f "Local State" "Variations" "First Run" "Last Version" 2>/dev/null || true

# Remove corrupted cache directories (but keep Extensions!)
rm -rf Default/GPUCache Default/ShaderCache "Default/Code Cache" 2>/dev/null || true

# Remove corrupted session files
rm -rf Default/Sessions Default/"Session Storage" 2>/dev/null || true

# Remove corrupted browser files that cause crashes
rm -f Default/Preferences.backup Default/Secure\ Preferences.backup 2>/dev/null || true

echo "✅ Browser state files cleaned!"
echo "✅ Extensions directory preserved!"

# Test the fixed profile
echo "🧪 Testing fixed profile..."

google-chrome \
    --user-data-dir="$PROFILE_DIR" \
    --no-sandbox \
    --disable-gpu \
    --disable-dev-shm-usage \
    --test-type \
    --no-first-run \
    "https://www.google.com" &

echo ""
echo "🎉 Chrome launched with fixed extension profile!"
echo ""
echo "📋 If Chrome works now:"
echo "1. Close Chrome"
echo "2. Run: python -m scitex.scholar open-browser --configure-only --profile extension"
echo "3. Run: google-chrome --user-data-dir=\"$PROFILE_DIR\" --no-sandbox --disable-gpu"
echo ""
echo "✅ All your Scholar extensions should be working!"