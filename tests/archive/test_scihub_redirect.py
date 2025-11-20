#!/usr/bin/env python
"""Test Sci-Hub redirects and actual paper page."""
import requests
import sys
sys.path.insert(0, '.')

from PyPaperBot.NetInfo import NetInfo
from PyPaperBot.Utils import URLjoin

mirror = 'https://sci-hub.st'
doi = '10.1023/a:1020597026919'

# Test different URL formats
urls_to_test = [
    URLjoin(mirror, doi),
    f"{mirror}/{doi}",
    f"{mirror}/?{doi}",
]

for url in urls_to_test:
    print(f"\n{'='*60}")
    print(f"Testing: {url}")
    print(f"{'='*60}")
    
    try:
        # Don't follow redirects automatically
        r = requests.get(url, headers=NetInfo.HEADERS, timeout=10, allow_redirects=False)
        print(f"Status: {r.status_code}")
        print(f"Location header: {r.headers.get('Location', 'None')}")
        print(f"Content-Type: {r.headers.get('content-type', 'unknown')}")
        print(f"Content length: {len(r.content)} bytes")
        
        if r.status_code in [301, 302, 303, 307, 308]:
            redirect_url = r.headers.get('Location')
            if redirect_url:
                print(f"\nFollowing redirect to: {redirect_url}")
                r2 = requests.get(redirect_url, headers=NetInfo.HEADERS, timeout=10)
                print(f"Final status: {r2.status_code}")
                print(f"Final Content-Type: {r2.headers.get('content-type', 'unknown')}")
                print(f"Contains 'pdf': {'pdf' in r2.text.lower()}")
                print(f"Contains 'iframe': {'iframe' in r2.text.lower()}")
                
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")

# Now test with redirects enabled
print(f"\n{'='*60}")
print("Testing with redirects enabled")
print(f"{'='*60}")
url = URLjoin(mirror, doi)
r = requests.get(url, headers=NetInfo.HEADERS, timeout=10, allow_redirects=True)
print(f"Final URL: {r.url}")
print(f"Status: {r.status_code}")
print(f"Content-Type: {r.headers.get('content-type', 'unknown')}")
print(f"Content length: {len(r.content)} bytes")

# Check if this is different from what we got before
if 'sci-hub' in r.url.lower() and r.status_code == 200:
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(r.text, 'html.parser')
    
    # Look for iframe with id='pdf'
    iframe = soup.find('iframe', id='pdf')
    if iframe:
        print(f"\n✓ Found iframe#pdf: {iframe.get('src')}")
    
    # Look for embed
    embed = soup.find('embed')
    if embed:
        print(f"✓ Found embed: src={embed.get('src')}, original-url={embed.get('original-url')}")
    
    # Look for button with download
    buttons = soup.find_all('button')
    for btn in buttons:
        onclick = btn.get('onclick', '')
        if 'pdf' in onclick.lower() or 'download' in onclick.lower():
            print(f"✓ Found button with onclick: {onclick[:200]}")

