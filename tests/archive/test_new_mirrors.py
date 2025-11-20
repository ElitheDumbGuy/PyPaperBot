#!/usr/bin/env python3
"""
Quick test of new Sci-Hub mirrors with working approach.
"""

import requests
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_mirror(mirror, doi):
    """Test a mirror with the working approach"""
    print(f"\n{'='*60}")
    print(f"Testing: {mirror} with DOI: {doi}")
    print(f"{'='*60}")
    
    try:
        url = f"{mirror.rstrip('/')}/{doi}"
        print(f"GET: {url}")
        
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15, verify=False)
        print(f"Status: {response.status_code}")
        print(f"Final URL: {response.url}")
        
        if response.status_code != 200:
            print(f"[FAIL] Non-200 status code")
            return False
        
        # Check for errors
        html_lower = response.text.lower()
        if "captcha" in html_lower:
            print("[WARN] Captcha detected")
            return False
        if "error" in html_lower or "not found" in html_lower:
            print("[WARN] Error/not found message")
            return False
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Check for iframe
        iframe = soup.find('iframe')
        if iframe and iframe.has_attr('src'):
            pdf_url = iframe.get('src')
            print(f"[OK] Found iframe with src: {pdf_url[:80]}...")
        else:
            # Try embed
            embed = soup.find('embed')
            if embed and embed.has_attr('src'):
                pdf_url = embed.get('src')
                print(f"[OK] Found embed with src: {pdf_url[:80]}...")
            else:
                # Try object
                obj = soup.find('object')
                if obj and obj.has_attr('data'):
                    pdf_url = obj.get('data')
                    print(f"[OK] Found object with data: {pdf_url[:80]}...")
                else:
                    print("[FAIL] No PDF link found (iframe/embed/object)")
                    return False
        
        # Fix relative URL
        if not pdf_url.startswith('http'):
            pdf_url = 'https:' + pdf_url
            print(f"Fixed URL: {pdf_url[:80]}...")
        
        # Try to download PDF
        print(f"Downloading PDF from: {pdf_url[:80]}...")
        pdf_response = requests.get(pdf_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15, verify=False)
        
        if pdf_response.content[:4] == b'%PDF':
            print(f"[SUCCESS] Valid PDF downloaded! Size: {len(pdf_response.content)} bytes")
            return True
        else:
            print(f"[FAIL] Not a valid PDF (got {pdf_response.headers.get('Content-Type', 'unknown')})")
            return False
            
    except Exception as e:
        print(f"[FAIL] Error: {type(e).__name__}: {e}")
        return False

if __name__ == '__main__':
    test_doi = '10.1038/s41586-020-2649-2'  # Known working DOI from example
    
    mirrors = [
        "https://sci-hub.mk",
        "https://sci-hub.shop",
        "https://sci-hub.vg",
    ]
    
    print("Testing new Sci-Hub mirrors with working approach")
    print("="*60)
    
    for mirror in mirrors:
        success = test_mirror(mirror, test_doi)
        if success:
            print(f"\n[SUCCESS] {mirror} works!")
        else:
            print(f"\n[FAIL] {mirror} failed")
        print()

