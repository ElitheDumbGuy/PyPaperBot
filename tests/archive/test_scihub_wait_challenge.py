#!/usr/bin/env python3
"""
Test Sci-Hub with longer waits to see if Cloudflare challenge needs time.
"""

import time
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import undetected_chromedriver as uc

def test_with_wait(mirror, doi, wait_time=10):
    """Test Sci-Hub with extended wait times"""
    print(f"\n{'='*60}")
    print(f"TEST: {mirror} with DOI {doi}, waiting {wait_time}s for challenge")
    print(f"{'='*60}")
    
    options = uc.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    
    driver = None
    try:
        driver = uc.Chrome(options=options, version_main=None)
        driver.set_page_load_timeout(60)
        
        # Try GET
        url = f"{mirror.rstrip('/')}/{doi}"
        print(f"\n[1] Loading: {url}")
        driver.get(url)
        
        # Wait for potential Cloudflare challenge
        print(f"[2] Waiting {wait_time}s for page to fully load...")
        time.sleep(wait_time)
        
        # Check if URL changed (challenge completed)
        current_url = driver.current_url
        print(f"[3] Current URL: {current_url}")
        
        # Check page title
        title = driver.title
        print(f"[4] Page title: {title}")
        
        # Look for Cloudflare challenge text
        html = driver.page_source
        if 'just a moment' in html.lower() or 'checking your browser' in html.lower():
            print("[WARN] Cloudflare challenge detected - need to wait longer")
        elif 'cloudflare' in html.lower():
            print("[WARN] Cloudflare detected in page")
        
        # Check for iframe
        soup = BeautifulSoup(html, 'html.parser')
        iframes = soup.find_all('iframe')
        print(f"[5] Found {len(iframes)} iframe(s):")
        for i, iframe in enumerate(iframes, 1):
            src = iframe.get('src', 'N/A')
            iframe_id = iframe.get('id', 'N/A')
            print(f"     {i}. id='{iframe_id}', src='{src[:80] if src != 'N/A' else 'N/A'}...'")
        
        # Check if we're still on homepage
        if current_url == mirror or current_url == mirror + '/':
            print("[FAIL] Still on homepage - request was blocked")
        else:
            print(f"[OK] Not on homepage - might have paper page")
        
        # Save HTML
        filename = f"tests/test_scihub_only/wait_{wait_time}s_{mirror.split('//')[1].replace('.', '_')}_{doi.replace('/', '_')}.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"[OK] Saved HTML to: {filename}")
        
        return len(iframes) > 0
        
    except TimeoutException:
        print("[FAIL] Page load timeout")
        return False
    except Exception as e:
        print(f"[FAIL] Error: {type(e).__name__}: {e}")
        return False
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

if __name__ == '__main__':
    mirror = "https://sci-hub.st"
    test_doi = "10.1038/nature12373"
    
    # Test with different wait times
    for wait_time in [5, 10, 15, 20]:
        print(f"\n\n{'#'*60}")
        print(f"TESTING WITH {wait_time}s WAIT")
        print(f"{'#'*60}")
        success = test_with_wait(mirror, test_doi, wait_time)
        if success:
            print(f"[SUCCESS] Found iframe with {wait_time}s wait!")
            break
        time.sleep(5)  # Rate limiting

