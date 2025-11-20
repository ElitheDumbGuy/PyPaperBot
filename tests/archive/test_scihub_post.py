#!/usr/bin/env python
"""Test Sci-Hub with POST request."""
import requests
import sys
sys.path.insert(0, '.')

from PyPaperBot.NetInfo import NetInfo

mirror = 'https://sci-hub.st'
doi = '10.1023/a:1020597026919'

# Sci-Hub uses POST with 'request' parameter
print(f"Testing POST to {mirror}")
print(f"DOI: {doi}\n")

# Test POST request
data = {'request': doi}
r = requests.post(mirror, data=data, headers=NetInfo.HEADERS, timeout=10, allow_redirects=True)

print(f"Status: {r.status_code}")
print(f"Final URL: {r.url}")
print(f"Content-Type: {r.headers.get('content-type', 'unknown')}")
print(f"Content length: {len(r.content)} bytes\n")

if r.status_code == 200:
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(r.text, 'html.parser')
    
    # Look for iframe with id='pdf'
    iframe = soup.find('iframe', id='pdf')
    if iframe:
        print(f"✓ Found iframe#pdf: {iframe.get('src')}")
    else:
        print("✗ No iframe#pdf found")
    
    # Look for embed
    embed = soup.find('embed')
    if embed:
        print(f"✓ Found embed: src={embed.get('src')}, original-url={embed.get('original-url')}")
    else:
        print("✗ No embed found")
    
    # Look for button with onclick
    buttons = soup.find_all('button')
    pdf_found = False
    for btn in buttons:
        onclick = btn.get('onclick', '')
        if 'pdf' in onclick.lower() or 'download' in onclick.lower():
            print(f"✓ Found button with onclick: {onclick[:200]}")
            pdf_found = True
    
    if not pdf_found:
        print("✗ No download button found")
    
    # Check for PDF URLs in the page
    import re
    pdf_urls = re.findall(r'https?://[^\s"\'<>]+\.pdf', r.text)
    if pdf_urls:
        print(f"\n✓ Found {len(pdf_urls)} PDF URLs in HTML")
        for url in pdf_urls[:3]:
            print(f"  {url}")
    else:
        print("\n✗ No PDF URLs found in HTML")
    
    # Save a sample to check structure
    with open('scihub_post_response.html', 'w', encoding='utf-8') as f:
        f.write(r.text)
    print("\nSaved response to scihub_post_response.html")

