<!-- ---
!-- Timestamp: 2025-07-24 06:25:58
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/docs/ZOTERO_SETTINGS.md
!-- --- -->

Option 3: Fix Zotero Connector (If you want full automation)
The WSL2 networking issue can sometimes be fixed:

In Windows Zotero: Edit → Preferences → Advanced → Config Editor
`extensions.zotero.connector.enabled`: true
`extensions.zotero.connector.port`: 23119
Restart Zotero

Then try this in Windows admin PowerShell:

``` powershell
netsh interface portproxy add v4tov4 listenport=23119 listenaddress=0.0.0.0 connectport=23119 connectaddress=127.0.0.1
```

<!-- EOF -->