#!/usr/bin/env python
"""Test script to diagnose Sci-Hub download issues."""
import requests
import sys
sys.path.insert(0, '.')

from PyPaperBot.NetInfo import NetInfo
from PyPaperBot.Utils import URLjoin

test_doi = "10.1023/a:1020597026919"
test_url = "https://link.springer.com/article/10.1023/a:1020597026919"

mirrors = ["https://sci-hub.st", "https://sci-hub.se"]

print("=" * 60)
print("Testing Sci-Hub Mirrors")
print("=" * 60)

for mirror in mirrors:
    print(f"\n{'='*60}")
    print(f"Testing mirror: {mirror}")
    print(f"{'='*60}")
    
    # Test 1: Check if mirror is accessible
    try:
        r = requests.get(mirror, headers=NetInfo.HEADERS, timeout=10)
        print(f"✓ Mirror accessible: {r.status_code}")
    except Exception as e:
        print(f"✗ Mirror NOT accessible: {type(e).__name__}: {e}")
        continue
    
    # Test 2: Try DOI
    doi_url = URLjoin(mirror, test_doi)
    print(f"\nTesting DOI URL: {doi_url}")
    try:
        r = requests.get(doi_url, headers=NetInfo.HEADERS, timeout=10)
        print(f"  Status: {r.status_code}")
        print(f"  Content-Type: {r.headers.get('content-type', 'unknown')}")
        print(f"  Content length: {len(r.content)} bytes")
        
        if r.status_code == 200:
            if 'application/pdf' in r.headers.get('content-type', '').lower():
                print(f"  ✓ Got PDF directly!")
            elif 'text/html' in r.headers.get('content-type', '').lower():
                print(f"  ✓ Got HTML page (need to extract PDF link)")
                print(f"  First 300 chars: {r.text[:300]}")
            else:
                print(f"  ? Unexpected content type")
        else:
            print(f"  ✗ HTTP error: {r.status_code}")
            print(f"  Response: {r.text[:200]}")
            
    except requests.exceptions.Timeout:
        print(f"  ✗ TIMEOUT after 10 seconds")
    except requests.exceptions.ConnectionError as e:
        print(f"  ✗ CONNECTION ERROR: {e}")
    except requests.exceptions.RequestException as e:
        print(f"  ✗ REQUEST ERROR: {type(e).__name__}: {e}")
    except Exception as e:
        print(f"  ✗ UNEXPECTED ERROR: {type(e).__name__}: {e}")
    
    # Test 3: Try URL
    url_url = URLjoin(mirror, test_url)
    print(f"\nTesting URL URL: {url_url}")
    try:
        r = requests.get(url_url, headers=NetInfo.HEADERS, timeout=10)
        print(f"  Status: {r.status_code}")
        print(f"  Content-Type: {r.headers.get('content-type', 'unknown')}")
    except Exception as e:
        print(f"  ✗ Error: {type(e).__name__}: {e}")

print(f"\n{'='*60}")
print("Test complete")
print(f"{'='*60}")

