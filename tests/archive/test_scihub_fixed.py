#!/usr/bin/env python3
"""
Fixed Sci-Hub test script with smart error handling.
- Mirror-specific method configuration (POST vs GET)
- Early termination after consecutive failures
- Smart 504 handling (don't retry across mirrors)
- Progress indication on stdout
- Minimal stderr noise
"""

import sys
import os
import requests
import urllib3
from lxml import etree
from urllib.parse import urlparse

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Mirror configuration with method preferences
MIRROR_CONFIG = {
    "https://sci-hub.mk": {"method": "POST", "name": ".mk"},
    "https://sci-hub.vg": {"method": "POST", "name": ".vg"},
    "https://sci-hub.al": {"method": "POST", "name": ".al"},
    "https://sci-hub.shop": {"method": "GET", "name": ".shop"},  # Only supports GET
}

# Test DOIs (first 10 from the list)
TEST_DOIS = [
    "10.1023/a:1020597026919",
    "10.1097/nmd.0000000000000685",
    "10.1016/j.amp.2019.08.014",
    "10.54079/jpmi.37.1.3087",
    "10.1016/j.concog.2016.03.017",
    "10.4103/ijsp.ijsp_227_21",
    "10.1097/nmd.0000000000000507",
    "10.1002/ijop.70027",
    "10.3389/fpsyt.2022.871041",
    "10.1080/15299732.2016.1160463",
]

class SmartSciHubClient:
    """Improved Sci-Hub client with smart error handling"""
    
    def __init__(self, mirrors_config):
        self.mirrors_config = mirrors_config
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Mozilla/5.0'})
        self.timeout = 15
    
    def _extract_pdf_url(self, html_content):
        """Extract PDF URL using XPath"""
        try:
            html = etree.HTML(html_content)
            pdf_xpath = '//*[@id="pdf"]/@src|//*[@id="article"]//iframe/@src'
            results = html.xpath(pdf_xpath)
            return results[0] if results else None
        except Exception:
            return None
    
    def _normalize_url(self, url):
        """Fix relative URLs"""
        if not url:
            return None
        if url.startswith('http'):
            return url
        if url.startswith('//'):
            return 'https:' + url
        return 'https:' + url
    
    def _download_from_mirror(self, mirror_url, doi, method):
        """
        Try to download from a single mirror using specified method.
        Returns: (success, pdf_content, error_type)
        error_type: None, '504', 'timeout', 'not_found', 'other'
        """
        try:
            # Make request based on mirror's preferred method
            if method == "POST":
                response = self.session.post(mirror_url, data={'request': doi}, 
                                            verify=False, timeout=self.timeout)
            else:  # GET
                url = f"{mirror_url.rstrip('/')}/{doi}"
                response = self.session.get(url, verify=False, timeout=self.timeout)
            
            # Check status
            if response.status_code == 504:
                return False, None, '504'
            elif response.status_code != 200:
                return False, None, 'not_found'
            
            # Extract PDF URL
            pdf_url = self._extract_pdf_url(response.content)
            if not pdf_url:
                return False, None, 'no_pdf_link'
            
            # Normalize and download PDF
            pdf_url = self._normalize_url(pdf_url)
            pdf_response = self.session.get(pdf_url, verify=False, timeout=self.timeout)
            
            # Validate PDF
            if pdf_response.content[:4] == b'%PDF':
                return True, pdf_response.content, None
            else:
                return False, None, 'invalid_pdf'
                
        except requests.exceptions.Timeout:
            return False, None, 'timeout'
        except requests.exceptions.RequestException:
            return False, None, 'other'
        except Exception:
            return False, None, 'other'
    
    def download(self, doi):
        """
        Download paper with smart mirror fallback.
        Returns: (success, pdf_content, mirror_name, error_type)
        """
        first_error = None
        
        for mirror_url, config in self.mirrors_config.items():
            success, pdf_content, error_type = self._download_from_mirror(
                mirror_url, doi, config['method']
            )
            
            if success:
                return True, pdf_content, config['name'], None
            
            # Remember first error
            if first_error is None:
                first_error = error_type
            
            # Smart error handling: don't try other mirrors for certain errors
            if error_type == '504':
                # 504 = paper not in database, no point trying other mirrors
                return False, None, None, '504_not_available'
        
        # All mirrors failed
        return False, None, None, first_error or 'unknown'


def main():
    print("="*70)
    print("FIXED SCI-HUB TEST - 10 DOIs")
    print("="*70)
    print(f"Testing {len(TEST_DOIS)} DOIs with smart error handling\n")
    
    client = SmartSciHubClient(MIRROR_CONFIG)
    
    results = {
        'success': [],
        'failed': []
    }
    
    consecutive_failures = 0
    MAX_CONSECUTIVE_FAILURES = 5
    
    for i, doi in enumerate(TEST_DOIS, 1):
        # Progress indicator
        print(f"[{i}/{len(TEST_DOIS)}] {doi}...", end=' ', flush=True)
        
        success, pdf_content, mirror_name, error_type = client.download(doi)
        
        if success:
            # Save PDF
            filename = f"tests/test_fixed_downloads/{doi.replace('/', '_').replace(':', '_')}.pdf"
            os.makedirs("tests/test_fixed_downloads", exist_ok=True)
            with open(filename, 'wb') as f:
                f.write(pdf_content)
            
            print(f"OK ({len(pdf_content):,} bytes from {mirror_name})")
            results['success'].append({
                'doi': doi,
                'mirror': mirror_name,
                'size': len(pdf_content)
            })
            consecutive_failures = 0  # Reset counter
            
        else:
            # Categorize failure
            if error_type == '504_not_available':
                print(f"FAIL (not in Sci-Hub database)")
            elif error_type == 'timeout':
                print(f"FAIL (timeout)")
            else:
                print(f"FAIL ({error_type})")
            
            results['failed'].append({
                'doi': doi,
                'reason': error_type
            })
            consecutive_failures += 1
            
            # Early termination check
            if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                print(f"\n[STOP] {MAX_CONSECUTIVE_FAILURES} consecutive failures. Stopping test.")
                print("This likely means Sci-Hub is down or blocking requests.")
                break
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Tested: {i}/{len(TEST_DOIS)}")
    print(f"Success: {len(results['success'])}")
    print(f"Failed: {len(results['failed'])}")
    if i > 0:
        print(f"Success rate: {len(results['success'])/i*100:.1f}%")
    
    # Mirror breakdown
    if results['success']:
        mirror_counts = {}
        for r in results['success']:
            mirror = r['mirror']
            mirror_counts[mirror] = mirror_counts.get(mirror, 0) + 1
        
        print("\nDownloads by mirror:")
        for mirror, count in sorted(mirror_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {mirror}: {count} papers")
    
    # Failure breakdown
    if results['failed']:
        error_counts = {}
        for r in results['failed']:
            reason = r['reason']
            error_counts[reason] = error_counts.get(reason, 0) + 1
        
        print("\nFailure reasons:")
        for reason, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {reason}: {count} papers")
    
    return results


if __name__ == "__main__":
    main()

