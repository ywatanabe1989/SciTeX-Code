#!/usr/bin/env python3
"""
Capture PAC collection papers to Zotero using WSL-Windows proxy.
This uses Chrome with Zotero Connector to save papers directly to Windows Zotero.

Prerequisites:
1. Zotero running on Windows
2. Zotero-WSL-ProxyServer running on Windows (port 23119)
3. Chrome in WSL with Zotero Connector extension
4. Authenticated Chrome Profile 1 with OpenAthens
"""

import json
import time
import subprocess
import requests
from pathlib import Path
from datetime import datetime


def check_zotero_proxy():
    """Check if Zotero proxy is accessible from WSL."""
    # Get Windows host IP in WSL
    try:
        # Method 1: Using hostname
        result = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
        wsl_ip = result.stdout.strip().split()[0] if result.stdout else None
        
        # Method 2: Get Windows host IP from /etc/resolv.conf
        with open('/etc/resolv.conf', 'r') as f:
            for line in f:
                if line.startswith('nameserver'):
                    windows_ip = line.split()[1]
                    break
        
        # Common Windows host IPs in WSL2
        possible_ips = [
            windows_ip if 'windows_ip' in locals() else None,
            '172.17.0.1',  # Common Docker IP
            '172.31.240.1',  # Common WSL2 IP
            '10.255.255.254',  # Another common WSL2 IP
            'host.docker.internal',
        ]
        
        # Test each possible endpoint
        for ip in possible_ips:
            if ip:
                proxy_urls = [
                    f'http://{ip}:23119',
                    f'http://{ip}.local:23119',
                ]
                
                for url in proxy_urls:
                    try:
                        response = requests.get(f'{url}/connector/ping', timeout=2)
                        if response.status_code == 200:
                            print(f"✅ Zotero proxy found at: {url}")
                            return url
                    except:
                        continue
        
        print("❌ Zotero proxy not accessible. Please ensure:")
        print("  1. Zotero is running on Windows")
        print("  2. Zotero-WSL-ProxyServer is running on Windows")
        print("  3. Windows Firewall allows port 23119")
        return None
        
    except Exception as e:
        print(f"Error checking proxy: {e}")
        return None


def send_to_zotero(proxy_url: str, paper_data: dict):
    """Send paper metadata to Zotero via proxy."""
    try:
        # Prepare Zotero item
        zotero_item = {
            'itemType': 'journalArticle',
            'title': paper_data.get('title', ''),
            'creators': [],
            'date': paper_data.get('year', ''),
            'DOI': paper_data.get('doi', ''),
            'url': paper_data.get('url', ''),
            'publicationTitle': paper_data.get('journal', ''),
            'volume': paper_data.get('volume', ''),
            'issue': paper_data.get('issue', ''),
            'pages': paper_data.get('pages', ''),
            'abstractNote': paper_data.get('abstract', ''),
            'tags': [],
        }
        
        # Process authors
        authors = paper_data.get('authors', [])
        for author in authors:
            if isinstance(author, str):
                # Parse "Last, First" format
                if ',' in author:
                    parts = author.split(',', 1)
                    creator = {
                        'creatorType': 'author',
                        'lastName': parts[0].strip(),
                        'firstName': parts[1].strip() if len(parts) > 1 else ''
                    }
                else:
                    # Parse "First Last" format
                    parts = author.strip().split()
                    creator = {
                        'creatorType': 'author',
                        'lastName': parts[-1] if parts else '',
                        'firstName': ' '.join(parts[:-1]) if len(parts) > 1 else ''
                    }
                zotero_item['creators'].append(creator)
        
        # Send to Zotero
        response = requests.post(
            f'{proxy_url}/connector/saveItems',
            json={'items': [zotero_item]},
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 201:
            return True, "Saved to Zotero"
        else:
            return False, f"Status {response.status_code}: {response.text}"
            
    except Exception as e:
        return False, str(e)


def open_and_capture_with_zotero(url: str, paper_name: str):
    """Open URL in Chrome and trigger Zotero Connector."""
    
    chrome_paths = [
        'google-chrome',
        'google-chrome-stable',
        'chromium',
        'chromium-browser',
    ]
    
    chrome_cmd = None
    for cmd in chrome_paths:
        try:
            subprocess.run(['which', cmd], capture_output=True, check=True)
            chrome_cmd = cmd
            break
        except:
            continue
    
    if not chrome_cmd:
        return False, "Chrome not found"
    
    profile_dir = Path.home() / '.scitex' / 'scholar' / 'cache' / 'chrome'
    
    # Chrome arguments with Zotero Connector
    args = [
        chrome_cmd,
        f'--user-data-dir={profile_dir}',
        '--profile-directory=Profile 1',
        '--new-tab',
        url
    ]
    
    try:
        # Open in Chrome
        subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Wait for page to load
        time.sleep(5)
        
        # Try to trigger Zotero Connector via JavaScript
        # This would need to be done through Chrome DevTools or extension messaging
        # For now, we rely on manual clicking or auto-detection
        
        return True, "Opened in Chrome with Zotero Connector"
        
    except Exception as e:
        return False, str(e)


def main():
    """Main function to capture PAC papers to Zotero."""
    
    library_dir = Path.home() / '.scitex' / 'scholar' / 'library'
    pac_dir = library_dir / 'pac'
    master_dir = library_dir / 'MASTER'
    
    print("PAC Collection → Zotero Capture (via WSL Proxy)")
    print("=" * 60)
    print()
    
    # Check Zotero proxy
    proxy_url = check_zotero_proxy()
    
    if not proxy_url:
        print("\nTo set up the proxy:")
        print("1. Download Zotero-WSL-ProxyServer.exe from:")
        print("   https://github.com/XFY9326/Zotero-WSL-ProxyServer/releases")
        print("2. Run it on Windows (it will open port 23119)")
        print("3. Make sure Zotero is running on Windows")
        print("4. Run this script again")
        return
    
    print()
    
    # Get papers to capture
    papers_to_capture = []
    
    for item in sorted(pac_dir.iterdir()):
        if not item.is_symlink() or item.name.startswith('.') or item.name == 'info':
            continue
        
        target = item.readlink()
        if target.parts[0] != '..':
            continue
            
        unique_id = target.parts[-1]
        master_path = master_dir / unique_id
        
        if not master_path.exists():
            continue
        
        # Load metadata
        metadata_file = master_path / 'metadata.json'
        if not metadata_file.exists():
            continue
            
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        doi = metadata.get('doi', '')
        if not doi:
            continue
        
        # Check if already has PDF
        pdf_files = list(master_path.glob('*.pdf'))
        
        papers_to_capture.append({
            'name': item.name,
            'master_path': master_path,
            'metadata': metadata,
            'has_pdf': len(pdf_files) > 0,
            'doi': doi,
            'url': f"https://doi.org/{doi}" if not doi.startswith('http') else doi
        })
    
    print(f"Found {len(papers_to_capture)} papers in PAC collection")
    
    # Filter based on user preference
    print("\nOptions:")
    print("1. Capture ALL papers to Zotero")
    print("2. Capture only papers WITHOUT PDFs")
    print("3. Open papers in Chrome for manual Zotero capture")
    
    choice = input("\nSelect option (1/2/3): ").strip()
    
    if choice == '2':
        papers_to_capture = [p for p in papers_to_capture if not p['has_pdf']]
        print(f"\nFiltered to {len(papers_to_capture)} papers without PDFs")
    elif choice == '3':
        # Open in Chrome for manual capture
        print("\nOpening papers in Chrome...")
        print("Use Zotero Connector extension to save papers")
        print("(Click the Zotero button in Chrome toolbar)")
        print()
        
        batch_size = 5
        for i in range(0, len(papers_to_capture), batch_size):
            batch = papers_to_capture[i:i+batch_size]
            
            print(f"Batch {i//batch_size + 1}:")
            for paper in batch:
                print(f"  Opening: {paper['name'][:50]}")
                open_and_capture_with_zotero(paper['url'], paper['name'])
                time.sleep(2)
            
            if i + batch_size < len(papers_to_capture):
                print("\nPress Enter to continue with next batch...")
                input()
        
        print("\n✅ All papers opened in Chrome!")
        print("Use Zotero Connector to save them to your library")
        return
    
    # Direct capture to Zotero
    print("\nCapturing papers to Zotero...")
    print()
    
    successful = 0
    failed = []
    
    for i, paper in enumerate(papers_to_capture, 1):
        print(f"[{i}/{len(papers_to_capture)}] {paper['name'][:50]}")
        
        # Send to Zotero
        success, message = send_to_zotero(proxy_url, paper['metadata'])
        
        if success:
            print(f"  ✅ {message}")
            successful += 1
            
            # Update metadata
            metadata = paper['metadata']
            metadata['in_zotero'] = True
            metadata['zotero_capture_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            with open(paper['master_path'] / 'metadata.json', 'w') as f:
                json.dump(metadata, f, indent=2)
        else:
            print(f"  ❌ {message}")
            failed.append(paper['name'])
        
        time.sleep(1)  # Small delay between items
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print(f"Successfully captured: {successful}/{len(papers_to_capture)}")
    
    if failed:
        print(f"Failed: {len(failed)}")
        print("\nFailed papers:")
        for name in failed[:10]:
            print(f"  - {name}")
    
    print("\n✅ Check your Zotero library on Windows!")
    print("The papers should appear with full metadata")
    print("\nTo download PDFs:")
    print("1. Select papers in Zotero")
    print("2. Right-click → Find Available PDFs")
    print("3. Zotero will use your institutional access to download")


if __name__ == "__main__":
    main()