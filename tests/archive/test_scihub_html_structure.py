#!/usr/bin/env python
"""Investigate Sci-Hub HTML structure to find PDF links."""
import requests
import sys
sys.path.insert(0, '.')

from PyPaperBot.NetInfo import NetInfo
from PyPaperBot.Utils import URLjoin
from bs4 import BeautifulSoup
import re

mirror = 'https://sci-hub.st'
doi = '10.1023/a:1020597026919'
url = URLjoin(mirror, doi)

print(f"Fetching: {url}")
r = requests.get(url, headers=NetInfo.HEADERS, timeout=10)
soup = BeautifulSoup(r.text, 'html.parser')

# Save HTML for inspection
with open('scihub_sample.html', 'w', encoding='utf-8') as f:
    f.write(r.text)
print("Saved HTML to scihub_sample.html\n")

# Look for common patterns
print("="*60)
print("Searching for PDF links...")
print("="*60)

# 1. Check for button with onclick
buttons = soup.find_all('button')
for btn in buttons:
    onclick = btn.get('onclick', '')
    if 'pdf' in onclick.lower() or 'download' in onclick.lower():
        print(f"\nButton with onclick: {onclick[:200]}")

# 2. Check for links
links = soup.find_all('a', href=True)
pdf_links = []
for link in links:
    href = link.get('href', '')
    text = link.get_text().lower()
    if '.pdf' in href.lower() or 'download' in text or 'pdf' in text:
        pdf_links.append((href, text[:50]))
        print(f"\nLink found: href={href[:100]}, text={text[:50]}")

# 3. Check for data attributes
elements_with_data = soup.find_all(attrs=lambda x: x and isinstance(x, dict) and any(k.startswith('data-') for k in x.keys()))
for elem in elements_with_data[:10]:
    data_attrs = {k: v for k, v in elem.attrs.items() if k.startswith('data-')}
    if data_attrs:
        print(f"\nElement with data: {elem.name}, {data_attrs}")

# 4. Search in JavaScript
scripts = soup.find_all('script')
for script in scripts:
    if script.string:
        content = script.string
        # Look for PDF URLs in JavaScript
        pdf_matches = re.findall(r'https?://[^\s"\'<>]+\.pdf', content)
        if pdf_matches:
            print(f"\nPDF URLs in script: {pdf_matches[:3]}")
        
        # Look for download functions
        if 'download' in content.lower() or 'pdf' in content.lower():
            # Extract relevant lines
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'pdf' in line.lower() or 'download' in line.lower():
                    print(f"\nScript line {i}: {line[:150]}")

# 5. Look for any element with id containing 'pdf' or 'download'
pdf_elements = soup.find_all(id=re.compile('pdf|download', re.I))
print(f"\nElements with pdf/download in id: {len(pdf_elements)}")
for elem in pdf_elements[:5]:
    print(f"  {elem.name}#{elem.get('id')}: {elem.get('href') or elem.get('src') or 'no link'}")

