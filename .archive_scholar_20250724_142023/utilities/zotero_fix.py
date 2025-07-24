#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-22 23:13:41 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/zotero_fix.py
# ----------------------------------------
import os
__FILE__ = (
    "./zotero_fix.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
"""
Quick Zotero Fix - Run this first to diagnose and fix Zotero connection
"""

import asyncio
import subprocess
from pathlib import Path

import aiohttp


async def quick_fix():
    print("🔧 QUICK ZOTERO CONNECTION FIX")
    print("=" * 40)

    # Step 1: Check if in WSL2
    is_wsl2 = False
    try:
        with open("/proc/version", "r") as f:
            is_wsl2 = "microsoft" in f.read().lower()
    except:
        pass

    print(f"Environment: {'WSL2' if is_wsl2 else 'Linux'}")

    # Step 2: Get Windows IP if WSL2
    windows_ip = None
    if is_wsl2:
        try:
            result = subprocess.run(
                ["ip", "route", "show", "default"],
                capture_output=True,
                text=True,
            )
            windows_ip = result.stdout.split()[2]
            print(f"Windows IP: {windows_ip}")
        except:
            print("❌ Could not get Windows IP")

    # Step 3: Check for Zotero processes
    print("\n🔍 Checking Zotero processes...")

    zotero_running = False

    if is_wsl2:
        try:
            result = subprocess.run(
                [
                    "powershell.exe",
                    "-Command",
                    "Get-Process -Name '*zotero*' -ErrorAction SilentlyContinue",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.stdout.strip():
                print("✅ Zotero running in Windows")
                zotero_running = True
            else:
                print("❌ Zotero NOT running in Windows")
        except:
            print("⚠️ Could not check Windows processes")

    # Step 4: Test connections
    print("\n🔗 Testing connections...")

    test_urls = ["http://127.0.0.1:23119"]
    if windows_ip:
        test_urls.append(f"http://{windows_ip}:23119")

    working_url = None
    for url in test_urls:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{url}/connector/ping", timeout=3
                ) as response:
                    if response.status == 200:
                        print(f"✅ {url} - WORKING")
                        working_url = url
                        break
                    else:
                        print(f"❌ {url} - HTTP {response.status}")
        except:
            print(f"❌ {url} - No response")

    # Step 5: Provide fix instructions
    if working_url:
        print(f"\n🎉 SUCCESS! Zotero accessible at: {working_url}")
        return True
    else:
        print(f"\n❌ ZOTERO CONNECTION FAILED")
        print("\n🔧 FIX INSTRUCTIONS:")

        if is_wsl2:
            print("\nFor WSL2 + Windows Zotero:")
            print("1. Start Zotero on Windows (not in WSL2)")
            print(
                "2. In Zotero: Edit → Preferences → Advanced → Config Editor"
            )
            print("3. Search: extensions.zotero.connector.enabled")
            print("4. Set to: true")
            print("5. Restart Zotero")
            print("6. Run this script again")

            # Try to auto-start
            print("\n🚀 Attempting to start Windows Zotero...")
            zotero_paths = [
                "/mnt/c/Program Files/Zotero/zotero.exe",
                "/mnt/c/Program Files (x86)/Zotero/zotero.exe",
            ]

            # Try to find username and add user path
            try:
                result = subprocess.run(
                    ["cmd.exe", "/c", "echo %USERNAME%"],
                    capture_output=True,
                    text=True,
                )
                username = result.stdout.strip()
                if username and username != "%USERNAME%":
                    user_path = f"/mnt/c/Users/{username}/AppData/Local/Zotero/zotero.exe"
                    zotero_paths.append(user_path)
            except:
                pass

            for path in zotero_paths:
                if Path(path).exists():
                    print(f"Found Zotero at: {path}")
                    try:
                        # Start Zotero
                        windows_path = path.replace("/mnt/c", "C:").replace(
                            "/", "\\"
                        )
                        subprocess.Popen(
                            ["cmd.exe", "/c", f'start "" "{windows_path}"'],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                        )
                        print(
                            "✅ Started Zotero! Wait 10 seconds and run the script again."
                        )
                        return False
                    except Exception as e:
                        print(f"❌ Could not start Zotero: {e}")

            print("❌ Could not find or start Zotero automatically")
            print("Please start Zotero manually on Windows")

        else:
            print("\nFor Linux:")
            print("1. Install and start Zotero desktop")
            print("2. Enable connector in Zotero preferences")
            print("3. Run: zotero &")

        return False


if __name__ == "__main__":
    asyncio.run(quick_fix())

# EOF
