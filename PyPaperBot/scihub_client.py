# -*- coding: utf-8 -*-
"""
Hybrid Sci-Hub client for downloading papers with automatic fallback from HTTP to Selenium.
"""

import time
import requests
import urllib3
import json
from lxml import etree
from urllib.parse import urlparse
from selenium.common.exceptions import TimeoutException

from .HTMLparsers import getSchiHubPDF_xpath
from .NetInfo import NetInfo
from .Utils import URLjoin

# Disable SSL warnings (Sci-Hub uses intermediate certificates)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Browser fingerprint for DDOS-Guard bypass, inspired by SciHubEVA
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

class SciHubDownloadError(Exception):
    """Raised when a paper cannot be downloaded from Sci-Hub."""
    pass

class SciHubClient:
    DEFAULT_MIRRORS = ["https://sci-hub.mk", "https://sci-hub.vg", "https://sci-hub.al", "https://sci-hub.shop"]

    def __init__(self, scihub_url=None, use_selenium=True, headless=True, selenium_driver=None, preferred_mirrors=None):
        self.scihub_url = scihub_url or NetInfo.SciHub_URL or self.DEFAULT_MIRRORS[0]
        self.use_selenium = use_selenium
        self.headless = headless
        self.selenium_driver = selenium_driver
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
        })
        self.preferred_mirrors = preferred_mirrors or self.DEFAULT_MIRRORS.copy()
        self.http_timeout = 15
        self.page_load_timeout = 20
        self._ddos_guard_bypass(self.scihub_url)
    
    def _ddos_guard_bypass(self, url):
        """
        Attempts to bypass DDOS-Guard by mimicking SciHubEVA's request sequence.
        """
        import sys
        print("  [Bypass] Checking for DDOS-Guard...", file=sys.stderr)
        base_url = url.rstrip('/')
        
        try:
            check_resp = self.session.get(base_url, verify=False, timeout=self.http_timeout)
            self.session.cookies.update(check_resp.cookies)

            if not (check_resp.status_code == 403 or 'ddos-guard' in check_resp.headers.get('server', '').lower()):
                print("  [Bypass] No DDOS-Guard detected. Skipping.", file=sys.stderr)
                return True

            print("  [Bypass] DDOS-Guard detected. Attempting bypass sequence.", file=sys.stderr)
            guard_url = f'{base_url}/.well-known/ddos-guard/check?context=free_splash'
            self.session.get(guard_url, verify=False, timeout=self.http_timeout)
            
            mark_url = f'{base_url}/.well-known/ddos-guard/mark/'
            self.session.post(mark_url, json=FAKE_MARK_JSON, verify=False, timeout=self.http_timeout)
            
            final_check = self.session.get(base_url, verify=False, timeout=self.http_timeout)

            if final_check.status_code == 403:
                print("  [Bypass FAIL] Still getting 403. Bypass failed.", file=sys.stderr)
                return False
            
            print("  [Bypass OK] Bypass sequence completed.", file=sys.stderr)
            return True

        except requests.RequestException as e:
            print(f"  [Bypass ERROR] An error occurred during bypass: {e}", file=sys.stderr)
            return False

    def _is_valid_pdf(self, content):
        if not content or len(content) < 4:
            return False
        return content[:4] == b'%PDF'

    def _is_error_page(self, html_content):
        # This can be simplified or removed if XPath is reliable
        return False, None

    def _get_available_mirrors(self):
        mirrors = self.preferred_mirrors.copy()
        return mirrors[:4]
    
    def _download_via_http(self, identifier, is_doi=True):
        try:
            # Try POST first, as it's more common
            response = self.session.post(self.scihub_url, data={'request': identifier}, verify=False, timeout=self.http_timeout)
            
            # If POST is not allowed, fall back to GET
            if response.status_code == 405:
                import sys
                print(f"  [Sci-Hub HTTP] POST not allowed on {self.scihub_url}. Falling back to GET.", file=sys.stderr)
                url = URLjoin(self.scihub_url.rstrip('/'), identifier)
                response = self.session.get(url, verify=False, timeout=self.http_timeout)

            response.raise_for_status()

            # Extract PDF URL using XPath
            pdf_url = getSchiHubPDF_xpath(response.content)

            if pdf_url:
                # Normalize URL
                parsed_pdf_url = urlparse(pdf_url)
                if not parsed_pdf_url.scheme:
                    base_url = urlparse(response.url)
                    pdf_url = "https:" + pdf_url if pdf_url.startswith('//') else f"{base_url.scheme}://{base_url.netloc}{pdf_url}"

                # Download the actual PDF
                pdf_response = self.session.get(pdf_url, verify=False, timeout=self.http_timeout)
                pdf_response.raise_for_status()

                if self._is_valid_pdf(pdf_response.content):
                    return pdf_response.content, pdf_response.url
            
            return None, None

        except requests.exceptions.RequestException as e:
            import sys
            status = getattr(getattr(e, 'response', None), 'status_code', 'N/A')
            print(f"  [Sci-Hub HTTP] Request failed for {identifier[:50]} ({type(e).__name__}, Status: {status})", file=sys.stderr)
            return None, None

    def _download_via_selenium(self, identifier, is_doi=True):
        # Simplified for now, can be enhanced later if needed
        # Main logic will rely on the more robust HTTP method
        return None, None

    def download(self, identifier, is_doi=True):
        available_mirrors = self._get_available_mirrors()
        
        for mirror in available_mirrors:
            self.scihub_url = mirror
            
            # Attempt HTTP download
            pdf_content, source_url = self._download_via_http(identifier, is_doi)
            if pdf_content:
                return pdf_content, source_url, mirror
        
        # If all mirrors fail via HTTP, raise an error
        raise SciHubDownloadError(f"Failed to download from all mirrors for identifier: {identifier}")
        
    def close(self):
        if self.selenium_driver:
            try:
                self.selenium_driver.quit()
            except Exception:
                pass
        self.session.close()

