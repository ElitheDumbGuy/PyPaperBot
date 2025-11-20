#!/usr/bin/env python
"""Test PDF link extraction from Sci-Hub HTML."""
import requests
import sys
sys.path.insert(0, '.')

from PyPaperBot.NetInfo import NetInfo
from PyPaperBot.Utils import URLjoin
from PyPaperBot.HTMLparsers import getSchiHubPDF
from bs4 import BeautifulSoup

mirror = 'https://sci-hub.st'
doi = '10.1023/a:1020597026919'
url = URLjoin(mirror, doi)

print(f"Fetching: {url}")
r = requests.get(url, headers=NetInfo.HEADERS, timeout=10)
print(f"Status: {r.status_code}")
print(f"Content length: {len(r.content)} bytes\n")

# Test current extraction function
pdf_link = getSchiHubPDF(r.text)
print(f"Current getSchiHubPDF() result: {pdf_link}")

# Manual inspection
soup = BeautifulSoup(r.text, 'html.parser')

print("\n" + "="*60)
print("HTML Structure Analysis")
print("="*60)

iframe_pdf = soup.find(id='pdf')
print(f"\niframe#pdf: {iframe_pdf}")
if iframe_pdf:
    print(f"  src: {iframe_pdf.get('src')}")

plugin = soup.find(id='plugin')
print(f"\nembed#plugin: {plugin}")
if plugin:
    print(f"  src: {plugin.get('src')}")

embed = soup.find('embed')
print(f"\nFirst <embed>: {embed}")
if embed:
    print(f"  src: {embed.get('src')}")
    print(f"  original-url: {embed.get('original-url')}")

print("\nAll iframes:")
for i, iframe in enumerate(soup.find_all('iframe')[:5]):
    print(f"  {i+1}. id={iframe.get('id', 'none')}, src={iframe.get('src', 'none')[:80]}")

print("\nAll embeds:")
for i, emb in enumerate(soup.find_all('embed')[:5]):
    print(f"  {i+1}. id={emb.get('id', 'none')}, src={emb.get('src', 'none')[:80]}")
    print(f"      original-url={emb.get('original-url', 'none')[:80]}")

# Search for PDF links in text
import re
pdf_urls = re.findall(r'https?://[^"\'\\s<>]+\.pdf', r.text)
print(f"\nPDF URLs found in HTML: {len(pdf_urls)}")
for i, pdf_url in enumerate(pdf_urls[:5]):
    print(f"  {i+1}. {pdf_url}")

