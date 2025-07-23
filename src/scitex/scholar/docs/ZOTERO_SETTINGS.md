<!-- ---
!-- Timestamp: 2025-07-22 23:19:50
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/docs/ZOTERO_SETTINGS.md
!-- --- -->

Option 3: Fix Zotero Connector (If you want full automation)
The WSL2 networking issue can sometimes be fixed:

In Windows Zotero: Edit → Preferences → Advanced → Config Editor
Search for: extensions.zotero.connector.enabled
Set to: true
Also search for: extensions.zotero.connector.port
Set to: 23119
Restart Zotero

Then try this in Windows admin PowerShell:

``` powershell
netsh interface portproxy add v4tov4 listenport=23119 listenaddress=0.0.0.0 connectport=23119 connectaddress=127.0.0.1
```

<!-- EOF -->