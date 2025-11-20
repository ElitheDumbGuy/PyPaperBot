#!/usr/bin/env python
"""Detailed Sci-Hub HTML analysis."""
import requests
import sys
import re
sys.path.insert(0, '.')

from PyPaperBot.NetInfo import NetInfo
from PyPaperBot.Utils import URLjoin
from bs4 import BeautifulSoup

mirror = 'https://sci-hub.st'
doi = '10.1023/a:1020597026919'
url = URLjoin(mirror, doi)

r = requests.get(url, headers=NetInfo.HEADERS, timeout=10)
soup = BeautifulSoup(r.text, 'html.parser')

print("Searching for download buttons/links...")
print("="*60)

# Look for buttons with "download" text
download_buttons = soup.find_all('button', string=re.compile('download', re.I))
print(f"\nDownload buttons: {len(download_buttons)}")
for btn in download_buttons[:3]:
    print(f"  {btn}")

# Look for links with "download" text
download_links = soup.find_all('a', string=re.compile('download', re.I))
print(f"\nDownload links: {len(download_links)}")
for link in download_links[:3]:
    print(f"  href: {link.get('href')}")
    print(f"  text: {link.get_text()[:100]}")

# Look for onclick handlers that might contain PDF URLs
onclick_elements = soup.find_all(attrs={'onclick': True})
print(f"\nElements with onclick: {len(onclick_elements)}")
for elem in onclick_elements[:3]:
    onclick = elem.get('onclick', '')
    if 'pdf' in onclick.lower() or 'download' in onclick.lower():
        print(f"  {elem.name}: {onclick[:200]}")

# Look for data attributes
data_elements = soup.find_all(attrs=lambda x: x and any(k.startswith('data-') for k in x.keys()))
print(f"\nElements with data attributes: {len(data_elements)}")
for elem in data_elements[:5]:
    data_attrs = {k: v for k, v in elem.attrs.items() if k.startswith('data-')}
    if data_attrs:
        print(f"  {elem.name}: {data_attrs}")

# Search for any URL patterns
url_patterns = re.findall(r'https?://[^\s"\'<>]+', r.text)
pdf_urls = [u for u in url_patterns if '.pdf' in u.lower()]
print(f"\nPDF URLs in HTML: {len(pdf_urls)}")
for pdf_url in pdf_urls[:5]:
    print(f"  {pdf_url}")

# Look for script tags that might contain PDF URLs
scripts = soup.find_all('script')
print(f"\nScript tags: {len(scripts)}")
for script in scripts[:3]:
    content = script.string or ''
    if 'pdf' in content.lower() or 'download' in content.lower():
        print(f"  Script contains PDF/download: {content[:300]}")

