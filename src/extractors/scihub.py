# -*- coding: utf-8 -*-
"""
Hybrid Sci-Hub client for downloading papers with automatic fallback from HTTP to Selenium.
Improved with smart error handling and mirror-specific configuration.
"""

import time
import requests
import urllib3
import json
from lxml import etree
from urllib.parse import urlparse
from selenium.common.exceptions import TimeoutException

from extractors.parsers import getSchiHubPDF_xpath, is_scihub_paper_not_available, is_cloudflare_page
from utils.net_info import NetInfo
from utils.utils import URLjoin

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
    # Mirror configuration with method preferences
    DEFAULT_MIRRORS = [
        {"url": "https://sci-hub.mk", "method": "POST"},
        {"url": "https://sci-hub.vg", "method": "POST"},
        {"url": "https://sci-hub.al", "method": "POST"},
        {"url": "https://sci-hub.shop", "method": "GET"},  # Only supports GET
    ]

    def __init__(self, scihub_url=None, use_selenium=True, headless=True, selenium_driver=None, preferred_mirrors=None):
        self.use_selenium = use_selenium
        self.headless = headless
        self.selenium_driver = selenium_driver
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
        })
        
        # Set up mirror configuration
        if preferred_mirrors:
            # Convert old-style list to new config format
            self.mirrors = []
            for mirror in preferred_mirrors:
                if isinstance(mirror, dict):
                    self.mirrors.append(mirror)
                else:
                    # Determine method based on URL
                    method = "GET" if "shop" in mirror else "POST"
                    self.mirrors.append({"url": mirror, "method": method})
        else:
            self.mirrors = self.DEFAULT_MIRRORS.copy()
        
        self.scihub_url = scihub_url or (self.mirrors[0]["url"] if self.mirrors else NetInfo.SciHub_URL)
        self.http_timeout = 15
        self.page_load_timeout = 20
        
        # Run DDOS-Guard bypass on first mirror only (quietly)
        if self.mirrors:
            self._ddos_guard_bypass(self.mirrors[0]["url"])
    
    def _ddos_guard_bypass(self, url):
        """Attempts to bypass DDOS-Guard by mimicking SciHubEVA's request sequence."""
        try:
            check_resp = self.session.get(url, verify=False, timeout=self.http_timeout)
            self.session.cookies.update(check_resp.cookies)

            if not (check_resp.status_code == 403 or 'ddos-guard' in check_resp.headers.get('server', '').lower()):
                return True

            guard_url = f'{url.rstrip("/")}/.well-known/ddos-guard/check?context=free_splash'
            self.session.get(guard_url, verify=False, timeout=self.http_timeout)
            
            mark_url = f'{url.rstrip("/")}/.well-known/ddos-guard/mark/'
            self.session.post(mark_url, json=FAKE_MARK_JSON, verify=False, timeout=self.http_timeout)
            
            final_check = self.session.get(url, verify=False, timeout=self.http_timeout)
            return final_check.status_code != 403

        except Exception:
            return False

    def _is_valid_pdf(self, content):
        if not content or len(content) < 4:
            return False
        return content[:4] == b'%PDF'

    def _get_available_mirrors(self):
        return self.mirrors[:4]
    
    def _download_via_http(self, identifier, mirror_config, is_doi=True, retry_on_cloudflare=True):
        """
        Attempt to download from a single mirror using its preferred method.
        Returns: (pdf_content, source_url, error_type)
        error_type: None, 'not_available', 'cloudflare', 'timeout', 'not_found', 'no_pdf_link', 'other'
        """
        mirror_url = mirror_config["url"]
        method = mirror_config["method"]
        
        try:
            # Make request based on mirror's preferred method
            if method == "POST":
                response = self.session.post(mirror_url, data={'request': identifier}, 
                                            verify=False, timeout=self.http_timeout)
            else:  # GET
                url = URLjoin(mirror_url.rstrip('/'), identifier)
                response = self.session.get(url, verify=False, timeout=self.http_timeout)
            
            # Check for 504 (paper not in database)
            if response.status_code == 504:
                return None, None, 'not_available'
            
            response.raise_for_status()
            
            # Check if paper is not available in database
            if is_scihub_paper_not_available(response.content):
                return None, None, 'not_available'
            
            # Check for Cloudflare blocking
            if is_cloudflare_page(response.content):
                if retry_on_cloudflare:
                    # Wait a moment and retry once
                    import sys
                    print(f"  [Sci-Hub] Cloudflare detected on {mirror_url}, retrying...", file=sys.stderr)
                    time.sleep(2)
                    return self._download_via_http(identifier, mirror_config, is_doi, retry_on_cloudflare=False)
                else:
                    return None, None, 'cloudflare'

            # Extract PDF URL using XPath
            pdf_url = getSchiHubPDF_xpath(response.content)

            if not pdf_url:
                return None, None, 'no_pdf_link'
            
            # Normalize URL
            parsed_pdf_url = urlparse(pdf_url)
            if not parsed_pdf_url.scheme:
                base_url = urlparse(response.url)
                pdf_url = "https:" + pdf_url if pdf_url.startswith('//') else f"{base_url.scheme}://{base_url.netloc}{pdf_url}"

            # Download the actual PDF
            pdf_response = self.session.get(pdf_url, verify=False, timeout=self.http_timeout)
            pdf_response.raise_for_status()

            if self._is_valid_pdf(pdf_response.content):
                return pdf_response.content, pdf_response.url, None
            else:
                return None, None, 'invalid_pdf'
            
        except requests.exceptions.Timeout:
            return None, None, 'timeout'
        except requests.exceptions.HTTPError as e:
            if e.response and e.response.status_code == 504:
                return None, None, 'not_available'
            return None, None, 'http_error'
        except Exception:
            return None, None, 'other'

    def _download_via_selenium(self, identifier, is_doi=True):
        # Selenium fallback disabled for now - HTTP method is sufficient
        return None, None, 'selenium_disabled'

    def download(self, identifier, is_doi=True):
        """
        Download a paper with smart mirror fallback.
        Returns: (pdf_content, source_url, mirror_url)
        Raises: SciHubDownloadError with specific error message
        """
        available_mirrors = self._get_available_mirrors()
        first_error = None
        
        for mirror_config in available_mirrors:
            pdf_content, source_url, error_type = self._download_via_http(identifier, mirror_config, is_doi)
            
            if pdf_content:
                return pdf_content, source_url, mirror_config["url"]
            
            # Remember first error
            if first_error is None:
                first_error = error_type
            
            # Smart error handling: don't try other mirrors if paper is not available
            if error_type == 'not_available':
                # Paper not in database, no point trying other mirrors
                raise SciHubDownloadError(f"Paper not available in Sci-Hub database")
        
        # All mirrors failed
        error_msg = {
            'cloudflare': 'Blocked by Cloudflare',
            'timeout': 'Request timeout',
            'no_pdf_link': 'No PDF link found',
            'invalid_pdf': 'Invalid PDF content',
            'http_error': 'HTTP error',
            'other': 'Unknown error'
        }.get(first_error, 'Failed to download')
        
        raise SciHubDownloadError(f"{error_msg}: {identifier}")
        
    def close(self):
        """Clean up resources gracefully."""
        if self.selenium_driver:
            # Close all windows first
            try:
                self.selenium_driver.close()
            except Exception:
                pass
            # Then quit
            try:
                self.selenium_driver.quit()
            except (OSError, Exception):
                # Ignore handle errors on Windows
                pass
        
        # Close requests session
        try:
            self.session.close()
        except Exception:
            pass
