#!/usr/bin/env python3
import webbrowser
import time

dois = ['10.1371/journal.pone.0159279', '10.3389/fnins.2019.00573', '10.1016/j.tics.2010.09.001']

print("Opening DOIs in browser for Zotero import...")
print("Make sure Zotero is running!")
print()

for i, doi in enumerate(dois, 1):
    print(f"[{i}/{len(dois)}] Opening: {doi}")
    webbrowser.open(f"https://doi.org/{doi}")
    
    # Wait for user to save to Zotero
    if i < len(dois):
        input("Press Enter after saving to Zotero...")
    
print("\nDone! Check Zotero for imported papers with PDFs.")
