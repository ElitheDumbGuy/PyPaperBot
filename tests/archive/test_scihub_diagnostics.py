#!/usr/bin/env python3
"""
Comprehensive diagnostics for Sci-Hub download issues.
Tests GET vs POST, iframe extraction, Cloudflare detection, etc.
"""

import requests
import urllib3
from bs4 import BeautifulSoup
import sys
import time

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Test DOIs
TEST_DOIS = [
    "10.1038/nature12373",  # Known working DOI
    "10.1023/a:1020597026919",  # One that failed in test
]

MIRRORS = [
    "https://sci-hub.st",
    "https://sci-hub.se",
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def test_get_request(mirror, doi):
    """Test GET request: mirror/doi"""
    print(f"\n{'='*60}")
    print(f"TEST: GET {mirror}/{doi}")
    print(f"{'='*60}")
    
    try:
        url = f"{mirror.rstrip('/')}/{doi}"
        response = requests.get(url, headers=HEADERS, timeout=15, verify=False, allow_redirects=True)
        
        print(f"Status Code: {response.status_code}")
        print(f"Final URL: {response.url}")
        print(f"Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        print(f"Content Length: {len(response.content)} bytes")
        
        # Check for Cloudflare
        if 'cloudflare' in response.text.lower() or 'cf-ray' in response.headers:
            print("[WARN]  CLOUDFLARE DETECTED!")
        
        # Check for captcha
        if 'captcha' in response.text.lower():
            print("[WARN]  CAPTCHA DETECTED!")
        
        # Check for error messages
        if 'article not found' in response.text.lower() or 'not available' in response.text.lower():
            print("[WARN]  ERROR: Paper not available")
        
        # Look for iframe
        soup = BeautifulSoup(response.text, 'html.parser')
        iframes = soup.find_all('iframe')
        print(f"\nFound {len(iframes)} iframe(s):")
        for i, iframe in enumerate(iframes, 1):
            src = iframe.get('src', 'N/A')
            iframe_id = iframe.get('id', 'N/A')
            print(f"  {i}. id='{iframe_id}', src='{src[:100]}...'")
        
        # Look for embed
        embeds = soup.find_all('embed')
        print(f"\nFound {len(embeds)} embed(s):")
        for i, embed in enumerate(embeds, 1):
            src = embed.get('src', 'N/A')
            original_url = embed.get('original-url', 'N/A')
            print(f"  {i}. src='{src[:100] if src != 'N/A' else 'N/A'}...', original-url='{original_url[:100] if original_url != 'N/A' else 'N/A'}...'")
        
        # Look for form with request field
        forms = soup.find_all('form')
        print(f"\nFound {len(forms)} form(s):")
        for i, form in enumerate(forms, 1):
            action = form.get('action', 'N/A')
            method = form.get('method', 'GET').upper()
            request_input = form.find('input', {'name': 'request'}) or form.find('textarea', {'name': 'request'})
            print(f"  {i}. method={method}, action='{action}', has request field={request_input is not None}")
        
        # Save HTML for inspection
        filename = f"tests/test_scihub_only/get_{mirror.split('//')[1].replace('.', '_')}_{doi.replace('/', '_')}.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"\n[OK] Saved HTML to: {filename}")
        
        return response
        
    except requests.exceptions.Timeout:
        print("[FAIL] TIMEOUT")
        return None
    except requests.exceptions.RequestException as e:
        print(f"[FAIL] ERROR: {type(e).__name__}: {e}")
        return None

def test_post_request(mirror, doi):
    """Test POST request: mirror with data={'request': doi}"""
    print(f"\n{'='*60}")
    print(f"TEST: POST {mirror} with data={{'request': '{doi}'}}")
    print(f"{'='*60}")
    
    try:
        data = {'request': doi}
        response = requests.post(mirror, data=data, headers=HEADERS, timeout=15, verify=False, allow_redirects=True)
        
        print(f"Status Code: {response.status_code}")
        print(f"Final URL: {response.url}")
        print(f"Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        print(f"Content Length: {len(response.content)} bytes")
        
        # Check for Cloudflare
        if 'cloudflare' in response.text.lower() or 'cf-ray' in response.headers:
            print("[WARN]  CLOUDFLARE DETECTED!")
        
        # Check for captcha
        if 'captcha' in response.text.lower():
            print("[WARN]  CAPTCHA DETECTED!")
        
        # Check for error messages
        if 'article not found' in response.text.lower() or 'not available' in response.text.lower():
            print("[WARN]  ERROR: Paper not available")
        
        # Look for iframe
        soup = BeautifulSoup(response.text, 'html.parser')
        iframes = soup.find_all('iframe')
        print(f"\nFound {len(iframes)} iframe(s):")
        for i, iframe in enumerate(iframes, 1):
            src = iframe.get('src', 'N/A')
            iframe_id = iframe.get('id', 'N/A')
            print(f"  {i}. id='{iframe_id}', src='{src[:100] if src != 'N/A' else 'N/A'}...'")
        
        # Look for embed
        embeds = soup.find_all('embed')
        print(f"\nFound {len(embeds)} embed(s):")
        for i, embed in enumerate(embeds, 1):
            src = embed.get('src', 'N/A')
            original_url = embed.get('original-url', 'N/A')
            print(f"  {i}. src='{src[:100] if src != 'N/A' else 'N/A'}...', original-url='{original_url[:100] if original_url != 'N/A' else 'N/A'}...'")
        
        # Look for form with request field
        forms = soup.find_all('form')
        print(f"\nFound {len(forms)} form(s):")
        for i, form in enumerate(forms, 1):
            action = form.get('action', 'N/A')
            method = form.get('method', 'GET').upper()
            request_input = form.find('input', {'name': 'request'}) or form.find('textarea', {'name': 'request'})
            print(f"  {i}. method={method}, action='{action}', has request field={request_input is not None}")
        
        # Save HTML for inspection
        filename = f"tests/test_scihub_only/post_{mirror.split('//')[1].replace('.', '_')}_{doi.replace('/', '_')}.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"\n[OK] Saved HTML to: {filename}")
        
        return response
        
    except requests.exceptions.Timeout:
        print("[FAIL] TIMEOUT")
        return None
    except requests.exceptions.RequestException as e:
        print(f"[FAIL] ERROR: {type(e).__name__}: {e}")
        return None

def test_pdf_download(pdf_url):
    """Test downloading PDF from extracted URL"""
    print(f"\n{'='*60}")
    print(f"TEST: Download PDF from {pdf_url[:80]}...")
    print(f"{'='*60}")
    
    try:
        response = requests.get(pdf_url, headers=HEADERS, timeout=15, verify=False, allow_redirects=True)
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        print(f"Content Length: {len(response.content)} bytes")
        
        # Check if it's actually a PDF
        is_pdf = response.content[:4] == b'%PDF'
        print(f"Is PDF (starts with %PDF): {is_pdf}")
        
        if is_pdf:
            print("[SUCCESS] Valid PDF downloaded!")
            # Save first 100 bytes for inspection
            filename = f"tests/test_scihub_only/pdf_sample_{pdf_url.split('/')[-1][:20]}.bin"
            with open(filename, 'wb') as f:
                f.write(response.content[:100])
            print(f"[OK] Saved first 100 bytes to: {filename}")
        else:
            print("[FAIL] FAILED: Not a valid PDF")
            # Save content for inspection
            filename = f"tests/test_scihub_only/not_pdf_{pdf_url.split('/')[-1][:20]}.html"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(response.text[:5000])
            print(f"[WARN]  Saved content to: {filename}")
        
        return response if is_pdf else None
        
    except requests.exceptions.RequestException as e:
        print(f"[FAIL] ERROR: {type(e).__name__}: {e}")
        return None

def main():
    print("="*60)
    print("SCI-HUB DIAGNOSTICS")
    print("="*60)
    
    for mirror in MIRRORS:
        print(f"\n\n{'#'*60}")
        print(f"TESTING MIRROR: {mirror}")
        print(f"{'#'*60}")
        
        for doi in TEST_DOIS:
            print(f"\n\nTesting DOI: {doi}")
            
            # Test GET
            get_response = test_get_request(mirror, doi)
            time.sleep(2)  # Rate limiting
            
            # Test POST
            post_response = test_post_request(mirror, doi)
            time.sleep(2)  # Rate limiting
            
            # If we got a response, try to extract PDF URL and test download
            for response, method in [(get_response, 'GET'), (post_response, 'POST')]:
                if response and response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Try to find iframe
                    iframe = soup.find('iframe')
                    if iframe:
                        pdf_src = iframe.get('src')
                        if pdf_src:
                            if not pdf_src.startswith('http'):
                                if pdf_src.startswith('//'):
                                    pdf_src = 'https:' + pdf_src
                                elif pdf_src.startswith('/'):
                                    pdf_src = mirror.rstrip('/') + pdf_src
                            
                            print(f"\n[PDF] Found PDF URL via {method}: {pdf_src[:100]}...")
                            test_pdf_download(pdf_src)
                            break
            
            print("\n" + "-"*60)
            time.sleep(3)  # Rate limiting between DOIs

if __name__ == '__main__':
    main()

