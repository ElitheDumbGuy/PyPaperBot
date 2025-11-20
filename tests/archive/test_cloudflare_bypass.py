#!/usr/bin/env python3
"""
Test script to bypass DDOS-Guard/Cloudflare based on SciHubEVA's approach.
"""

import requests
import json
import time
from lxml import etree
from urllib.parse import urlparse

# --- Configuration ---
MIRRORS = [
    "https://sci-hub.mk",
    "https://sci-hub.shop",
    "https://sci-hub.vg",
]
TEST_DOI = '10.1038/s41586-020-2649-2'  # Known working DOI
FAKE_MARK_JSON = json.loads(r'''
{
   "_geo": true,
   "_sensor": { "gyroscope": true, "accelerometer": true, "magnetometer": false, "absorient": true, "relorient": true },
   "userAgent": "Windows_10_Blink_Chrome_undefined", "webdriver": false, "language": "en-US",
   "colorDepth": 24, "deviceMemory": 8, "pixelRatio": 1, "hardwareConcurrency": 16,
   "screenResolution": [ 1920, 1080 ], "availableScreenResolution": [ 1920, 1050 ],
   "timezoneOffset": -120, "timezone": "America/New_York", "sessionStorage": true,
   "localStorage": true, "indexedDb": true, "addBehavior": false, "openDatabase": true,
   "cpuClass": "not available", "platform": "Win32", "doNotTrack": "1",
   "plugins": [
      ["PDF Viewer", "Portable Document Format", [["application/pdf", "pdf"], ["text/pdf", "pdf"]]],
      ["Chrome PDF Viewer", "Portable Document Format", [["application/pdf", "pdf"], ["text/pdf", "pdf"]]],
      ["Chromium PDF Viewer", "Portable Document Format", [["application/pdf", "pdf"], ["text/pdf", "pdf"]]],
      ["Microsoft Edge PDF Viewer", "Portable Document Format", [["application/pdf", "pdf"], ["text/pdf", "pdf"]]],
      ["WebKit built-in PDF", "Portable Document Format", [["application/pdf", "pdf"], ["text/pdf", "pdf"]]]
   ],
   "canvas": ["canvas winding:yes", "canvas fp:data:image/png;base64,..."],
   "webgl": ["data:image/png;base64,..."],
   "webglVendorAndRenderer": "Google Inc. (NVIDIA)~ANGLE (NVIDIA, NVIDIA GeForce RTX 3060 Direct3D11 vs_5_0 ps_5_0, D3D11)",
   "adBlock": false, "hasLiedLanguages": false, "hasLiedResolution": false, "hasLiedOs": false,
   "hasLiedBrowser": false, "touchSupport": [ 0, false, false ],
   "fonts": ["Arial", "Arial Black", "Arial Narrow", "Calibri", "Cambria", "Comic Sans MS", "Consolas", "Courier", "Courier New", "Georgia", "Helvetica", "Impact", "Lucida Console", "Lucida Sans Unicode", "Microsoft Sans Serif", "MS Gothic", "MS PGothic", "MS Sans Serif", "MS Serif", "Palatino Linotype", "Segoe Print", "Segoe Script", "Segoe UI", "Tahoma", "Times", "Times New Roman", "Trebuchet MS", "Verdana", "Wingdings"],
   "audio": "124.04347527516074",
   "enumerateDevices": ["id=;gid=;audioinput;", "id=;gid=;videoinput;", "id=;gid=;audiooutput;"],
   "context": "free_splash"
}
''')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'DNT': '1',
}

# --- Functions ---

def ddos_guard_bypass(url, sess):
    """
    Attempts to bypass DDOS-Guard by mimicking SciHubEVA's request sequence.
    """
    print("  [Bypass] Attempting DDOS-Guard bypass...")
    base_url = url.rstrip('/')
    
    try:
        # 1. Initial request to get session cookies
        print("    - Step 1: Initial GET to base URL")
        check_resp = sess.get(base_url, verify=False)
        sess.cookies.update(check_resp.cookies)

        if not (check_resp.status_code == 403 or 'ddos-guard' in check_resp.headers.get('server', '').lower()):
             print("    - No DDOS-Guard detected. Skipping bypass.")
             return True

        # 2. Check DDOS-Guard endpoint
        print("    - Step 2: GET /.well-known/ddos-guard/check")
        guard_url = f'{base_url}/.well-known/ddos-guard/check?context=free_splash'
        guard_resp = sess.get(guard_url, verify=False)
        if guard_resp.status_code != 200:
            print("    - Check failed. Bypass may not work.")
        sess.cookies.update(guard_resp.cookies)

        # 3. Post fake browser fingerprint
        print("    - Step 3: POST fake fingerprint to /mark/")
        mark_url = f'{base_url}/.well-known/ddos-guard/mark/'
        mark_resp = sess.post(mark_url, json=FAKE_MARK_JSON, verify=False)
        if mark_resp.status_code != 200:
            print(f"    - Mark failed with status {mark_resp.status_code}. Bypass may not work.")
        sess.cookies.update(mark_resp.cookies)
        
        # 4. Final check
        print("    - Step 4: Final verification GET")
        final_check = sess.get(base_url, verify=False)
        sess.cookies.update(final_check.cookies)

        if final_check.status_code == 403:
             print("  [Bypass FAIL] Still getting 403. Bypass failed.")
             return False
        
        print("  [Bypass OK] Bypass sequence completed.")
        return True

    except requests.RequestException as e:
        print(f"  [Bypass ERROR] An error occurred during bypass: {e}")
        return False


def test_mirror(mirror, doi):
    """
    Tests a single mirror with the bypass and download logic.
    """
    print(f"\n{'='*60}\nTesting mirror: {mirror}\n{'='*60}")
    
    with requests.Session() as sess:
        sess.headers.update(HEADERS)
        
        # Attempt bypass first
        ddos_guard_bypass(mirror, sess)
        time.sleep(1) # Small delay
        
        # Now, try to get the paper
        print(f"\n  [Download] POSTing for DOI: {doi}")
        try:
            response = sess.post(mirror, data={'request': doi}, verify=False, timeout=20)
            
            if response.status_code != 200:
                print(f"  [Download FAIL] Status code: {response.status_code}")
                return

            html = etree.HTML(response.content)
            
            # Use XPath to find the PDF URL
            pdf_xpath = '//*[@id="pdf"]/@src|//*[@id="article"]//iframe/@src'
            results = html.xpath(pdf_xpath)
            
            if not results:
                print("  [Download FAIL] Could not find PDF iframe/embed using XPath.")
                # Save HTML for debugging
                with open("tests/test_cloudflare_bypass_fail.html", "wb") as f:
                    f.write(response.content)
                print("  - Saved failing HTML to tests/test_cloudflare_bypass_fail.html")
                return

            pdf_url = results[0]
            print(f"  [Download OK] Found PDF URL: {pdf_url}")

            # Normalize URL
            parsed_pdf_url = urlparse(pdf_url)
            if not parsed_pdf_url.scheme:
                pdf_url = "https:" + pdf_url if pdf_url.startswith('//') else urlparse(response.url).scheme + "://" + urlparse(response.url).netloc + pdf_url

            # Download the PDF
            print(f"  [PDF] Downloading from: {pdf_url}")
            pdf_response = sess.get(pdf_url, verify=False, timeout=20)
            
            if 'application/pdf' in pdf_response.headers.get('Content-Type', ''):
                print(f"  [SUCCESS] PDF downloaded successfully! Size: {len(pdf_response.content)} bytes.")
                filename = f"tests/{doi.replace('/', '_')}.pdf"
                with open(filename, 'wb') as f:
                    f.write(pdf_response.content)
                print(f"  - Saved to {filename}")
            else:
                print(f"  [PDF FAIL] Expected PDF, but got Content-Type: {pdf_response.headers.get('Content-Type', 'N/A')}")

        except requests.RequestException as e:
            print(f"  [Download ERROR] An error occurred: {e}")

# --- Main Execution ---
if __name__ == "__main__":
    for mirror_url in MIRRORS:
        test_mirror(mirror_url, TEST_DOI)
        time.sleep(2)
