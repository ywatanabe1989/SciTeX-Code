# Setting up Zotero WSL Proxy

## Problem
Chrome in WSL2 cannot directly connect to Zotero on Windows. The Zotero Connector shows "Is Zotero Running?" error.

## Solution: Zotero-WSL-ProxyServer

### Step 1: On Windows - Start Zotero
1. Open Zotero desktop application on Windows
2. Keep it running

### Step 2: On Windows - Start Proxy Server
1. Download the proxy from: https://github.com/XFY9326/Zotero-WSL-ProxyServer/releases
   - Download `Zotero-WSL-ProxyServer.exe`
   
2. Run the proxy server:
   ```cmd
   Zotero-WSL-ProxyServer.exe
   ```
   
3. The proxy will:
   - Open port 23119
   - Bridge WSL → Windows Zotero connection
   - Show "Proxy server running on port 23119"

### Step 3: Configure Chrome Zotero Connector (in WSL)
1. In Chrome, click Zotero Connector extension icon
2. Right-click → Options/Preferences
3. Advanced → Config Editor
4. Set connector URL to one of:
   - `http://10.255.255.254:23119` (your Windows IP)
   - `http://host.windows.internal:23119`
   
### Step 4: Test Connection
Run this in WSL to verify:
```bash
curl http://10.255.255.254:23119/connector/ping
```

Should return: `Zotero is running`

## Alternative: Direct Save to Zotero.org
If proxy setup is complex, you can:
1. Login to zotero.org in Chrome
2. Zotero Connector will save directly to web library
3. Sync later with desktop Zotero

## Current Windows IP
Your Windows host IP from WSL: `10.255.255.254`

## Quick Test Script
```python
import requests
response = requests.get('http://10.255.255.254:23119/connector/ping')
print(response.text if response.status_code == 200 else "Not connected")
```

## Firewall Note
Windows Firewall may block port 23119. If so:
1. Windows Defender Firewall → Advanced Settings
2. Inbound Rules → New Rule
3. Port → TCP → 23119
4. Allow connection
5. Name: "Zotero WSL Proxy"