#!/bin/bash
# Simple Chrome launcher with Scholar extensions
# All extensions are configured with API keys and ad-blocking

echo "🚀 Launching Chrome with Scholar extensions..."

google-chrome \
  --user-data-dir=/home/ywatanabe/.scitex/scholar/cache/chrome/extension \
  --no-sandbox \
  --disable-dev-shm-usage \
  --disable-gpu \
  --remote-debugging-port=9222 \
  --new-window \
  https://www.google.com \
  &

echo "✅ Chrome launched in background!"
echo "🔗 All Scholar extensions are loaded and configured"
echo "📱 Remote debugging: http://localhost:9222"
echo "💡 Extensions include: Lean Library, Pop-up Blocker, Cookie Acceptor, 2Captcha Solver, CAPTCHA Solver"
echo ""
echo "🛑 To close Chrome later, run: pkill -f 'user-data-dir.*extension'"