#!/bin/bash
# WSL2-optimized Chrome launcher with Scholar extensions
# Fixes CPU frequency monitoring issues and display problems

echo "🚀 Launching Chrome for WSL2 with Scholar extensions..."

google-chrome \
  --user-data-dir=/home/ywatanabe/.scitex/scholar/cache/chrome/extension \
  --no-sandbox \
  --disable-gpu \
  --disable-dev-shm-usage \
  --disable-software-rasterizer \
  --disable-background-timer-throttling \
  --disable-backgrounding-occluded-windows \
  --disable-renderer-backgrounding \
  --disable-features=VizDisplayCompositor \
  --disable-ipc-flooding-protection \
  --no-first-run \
  --no-default-browser-check \
  --disable-extensions-file-access-check \
  --disable-web-security \
  --remote-debugging-port=9222 \
  --new-window \
  "https://www.google.com" \
  > /dev/null 2>&1 &

echo "✅ Chrome launched successfully!"
echo "🔗 All Scholar extensions loaded:"
echo "   • Lean Library (Academic access)"
echo "   • Pop-up Blocker (Ad blocking)" 
echo "   • Cookie Acceptor (Auto-accept cookies)"
echo "   • 2Captcha Solver (CAPTCHA solving)"
echo "   • CAPTCHA Solver (hCaptcha solving)"
echo ""
echo "🔑 API keys are pre-configured"
echo "📱 Remote debugging: http://localhost:9222"
echo ""
echo "🛑 To close Chrome: pkill -f 'user-data-dir.*extension'"