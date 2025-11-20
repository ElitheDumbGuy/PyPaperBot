#!/usr/bin/env python3
"""
Test Sci-Hub with Selenium to see if JavaScript rendering helps.
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

def test_selenium(mirror, doi, headless=False):
    """Test Sci-Hub with Selenium"""
    print(f"\n{'='*60}")
    print(f"SELENIUM TEST: {mirror} with DOI {doi}")
    print(f"Headless: {headless}")
    print(f"{'='*60}")
    
    options = uc.ChromeOptions()
    if headless:
        options.add_argument('--headless')
    options.add_argument('--disable-blink-features=AutomationControlled')
    
    driver = None
    try:
        driver = uc.Chrome(options=options, version_main=None)
        driver.set_page_load_timeout(30)
        
        # Try GET first
        url = f"{mirror.rstrip('/')}/{doi}"
        print(f"\n[1] GET: {url}")
        driver.get(url)
        time.sleep(3)  # Wait for page load
        
        current_url = driver.current_url
        print(f"Current URL: {current_url}")
        
        # Check page source
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        # Look for iframe
        iframes = soup.find_all('iframe')
        print(f"Found {len(iframes)} iframe(s):")
        for i, iframe in enumerate(iframes, 1):
            src = iframe.get('src', 'N/A')
            iframe_id = iframe.get('id', 'N/A')
            print(f"  {i}. id='{iframe_id}', src='{src[:100] if src != 'N/A' else 'N/A'}...'")
        
        # Look for embed
        embeds = soup.find_all('embed')
        print(f"Found {len(embeds)} embed(s):")
        for i, embed in enumerate(embeds, 1):
            src = embed.get('src', 'N/A')
            original_url = embed.get('original-url', 'N/A')
            print(f"  {i}. src='{src[:100] if src != 'N/A' else 'N/A'}...'")
        
        # Check for Cloudflare
        if 'cloudflare' in html.lower() or 'cf-ray' in driver.get_cookies():
            print("[WARN] Cloudflare detected!")
        
        # Check for captcha
        if 'captcha' in html.lower():
            print("[WARN] Captcha detected!")
        
        # If no iframe found, try POST via form submission
        if len(iframes) == 0 and len(embeds) == 0:
            print("\n[2] No iframe found, trying form submission...")
            
            # Find the form
            try:
                form = driver.find_element(By.TAG_NAME, 'form')
                textarea = driver.find_element(By.NAME, 'request')
                textarea.clear()
                textarea.send_keys(doi)
                form.submit()
                
                time.sleep(5)  # Wait for form submission
                
                current_url = driver.current_url
                print(f"After form submit, URL: {current_url}")
                
                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
                
                # Look for iframe again
                iframes = soup.find_all('iframe')
                print(f"Found {len(iframes)} iframe(s) after form submit:")
                for i, iframe in enumerate(iframes, 1):
                    src = iframe.get('src', 'N/A')
                    iframe_id = iframe.get('id', 'N/A')
                    print(f"  {i}. id='{iframe_id}', src='{src[:100] if src != 'N/A' else 'N/A'}...'")
                
                # Save HTML
                filename = f"tests/test_scihub_only/selenium_form_{mirror.split('//')[1].replace('.', '_')}_{doi.replace('/', '_')}.html"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(html)
                print(f"[OK] Saved HTML to: {filename}")
                
            except Exception as e:
                print(f"[FAIL] Form submission error: {type(e).__name__}: {e}")
        else:
            # Save HTML
            filename = f"tests/test_scihub_only/selenium_get_{mirror.split('//')[1].replace('.', '_')}_{doi.replace('/', '_')}.html"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"[OK] Saved HTML to: {filename}")
        
        return driver
        
    except TimeoutException:
        print("[FAIL] Page load timeout")
        return None
    except Exception as e:
        print(f"[FAIL] Error: {type(e).__name__}: {e}")
        return None
    finally:
        if driver:
            driver.quit()

if __name__ == '__main__':
    mirrors = ["https://sci-hub.st", "https://sci-hub.se"]
    test_doi = "10.1038/nature12373"
    
    for mirror in mirrors:
        print(f"\n\n{'#'*60}")
        print(f"TESTING MIRROR: {mirror}")
        print(f"{'#'*60}")
        
        # Test non-headless first (more reliable)
        test_selenium(mirror, test_doi, headless=False)
        time.sleep(5)

