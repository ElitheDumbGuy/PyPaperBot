# -*- coding: utf-8 -*-
"""
Hybrid Sci-Hub client for downloading papers with automatic fallback from HTTP to Selenium.

This module provides a robust download mechanism that:
1. Attempts direct HTTP requests with session management
2. Validates PDF content (not just Content-Type headers)
3. Falls back to Selenium browser automation when HTTP fails
4. Detects and handles anti-bot challenges (Cloudflare, captchas)
"""

import time
import requests
from selenium.common.exceptions import TimeoutException
from .HTMLparsers import getSchiHubPDF
from .NetInfo import NetInfo
from .Utils import URLjoin


class SciHubDownloadError(Exception):
    """Raised when a paper cannot be downloaded from Sci-Hub."""
    pass


class SciHubClient:
    DEFAULT_MIRRORS = ["https://sci-hub.st", "https://sci-hub.se"]
    """
    Hybrid client for downloading papers from Sci-Hub.
    
    Attempts HTTP requests first, then falls back to Selenium if needed.
    """
    
    def __init__(self, scihub_url=None, use_selenium=True, headless=True, selenium_driver=None, preferred_mirrors=None):
        """
        Initialize the Sci-Hub client.
        
        Args:
            scihub_url: Specific Sci-Hub mirror URL to use (None = auto-detect)
            use_selenium: Whether to allow Selenium fallback (default: True)
            headless: Whether to run Selenium in headless mode (default: True)
            selenium_driver: Pre-configured Selenium driver (None = create on demand)
            preferred_mirrors: Optional ordered list of mirrors to try
        """
        self.scihub_url = scihub_url or NetInfo.SciHub_URL or self.DEFAULT_MIRRORS[0]
        self.use_selenium = use_selenium
        self.headless = headless
        self.selenium_driver = selenium_driver
        self.session = requests.Session()
        self.session.headers.update(NetInfo.HEADERS)
        self.preferred_mirrors = preferred_mirrors or self.DEFAULT_MIRRORS.copy()
        self.http_timeout = 10
        self.page_load_timeout = 12
        
    def _is_valid_pdf(self, content):
        """
        Validate that content is actually a PDF by checking the PDF header.
        
        Args:
            content: Bytes content to validate
            
        Returns:
            bool: True if content starts with PDF magic bytes
        """
        if not content or len(content) < 4:
            return False
        return content[:4] == b'%PDF'
    
    def _is_error_page(self, html_content):
        """
        Detect if the response is an HTML error/challenge page.
        
        Args:
            html_content: HTML content string
            
        Returns:
            tuple: (is_error: bool, error_type: str)
                   error_type: 'not_available', 'captcha', 'cloudflare', 'other', or None
        """
        if not html_content or not isinstance(html_content, str):
            return False, None
        
        html_lower = html_content.lower()
        
        # Check for "paper not available" - this is a specific error we want to detect
        if "not yet available in my database" in html_lower or "not available" in html_lower:
            return True, 'not_available'
        
        # Check for captcha
        if "captcha" in html_lower:
            return True, 'captcha'
        
        # Check for Cloudflare challenge
        if "cloudflare" in html_lower or "checking your browser" in html_lower or "please wait" in html_lower:
            return True, 'cloudflare'
        
        # Check for access denied/blocked
        if "access denied" in html_lower or "blocked" in html_lower:
            return True, 'blocked'
        
        return False, None
    
    def _get_available_mirrors(self):
        """Get ordered list of allowed Sci-Hub mirrors."""
        mirrors = []
        for url in self.preferred_mirrors:
            if url and url not in mirrors:
                mirrors.append(url)
        
        if not mirrors:
            mirrors = self.DEFAULT_MIRRORS.copy()
        
        # Ensure current mirror is first
        if self.scihub_url and self.scihub_url in mirrors:
            mirrors.remove(self.scihub_url)
            mirrors.insert(0, self.scihub_url)
        elif self.scihub_url:
            mirrors.insert(0, self.scihub_url)
        
        return mirrors[:2]
    
    def _download_via_http(self, identifier, is_doi=True):
        """
        Attempt to download paper via direct HTTP request.
        
        Args:
            identifier: DOI or URL to download
            is_doi: Whether identifier is a DOI (True) or URL (False)
            
        Returns:
            tuple: (pdf_content: bytes, source_url: str) or (None, None) on failure
        """
        try:
            if is_doi:
                url = URLjoin(self.scihub_url, identifier)
            else:
                url = URLjoin(self.scihub_url, identifier)
            
            response = self.session.get(url, timeout=self.http_timeout)
            response.raise_for_status()
            
            content_type = response.headers.get('content-type', '').lower()
            
            # Check if we got a PDF directly
            if 'application/pdf' in content_type or 'application/octet-stream' in content_type:
                if self._is_valid_pdf(response.content):
                    return response.content, response.url
            
            # Check if we got an HTML page (Sci-Hub landing page)
            if 'text/html' in content_type or not content_type:
                # Check for error pages
                is_error, error_type = self._is_error_page(response.text)
                if is_error:
                    if error_type == 'not_available':
                        raise SciHubDownloadError("Paper not available in Sci-Hub database")
                    return None, None
                
                # Try to extract PDF link from HTML
                pdf_link = getSchiHubPDF(response.text)
                
                if pdf_link:
                    # Make sure link is absolute
                    if pdf_link.startswith('//'):
                        pdf_link = 'https:' + pdf_link
                    elif not pdf_link.startswith('http'):
                        pdf_link = URLjoin(self.scihub_url, pdf_link.lstrip('/'))
                    
                    # Download the actual PDF
                    pdf_response = self.session.get(pdf_link, timeout=self.http_timeout)
                    pdf_response.raise_for_status()
                    
                    if self._is_valid_pdf(pdf_response.content):
                        return pdf_response.content, pdf_response.url
            
            return None, None
            
        except requests.exceptions.RequestException as e:
            return None, None
    
    def _download_via_selenium(self, identifier, is_doi=True):
        """
        Attempt to download paper via Selenium browser automation.
        
        Args:
            identifier: DOI or URL to download
            is_doi: Whether identifier is a DOI (True) or URL (False)
            
        Returns:
            tuple: (pdf_content: bytes, source_url: str) or (None, None) on failure
        """
        if not self.use_selenium:
            return None, None
        
        try:
            import undetected_chromedriver as uc
            
            # Create driver if not provided
            driver = self.selenium_driver
            if driver is None:
                driver = uc.Chrome(headless=self.headless, use_subprocess=False)
                try:
                    driver.set_page_load_timeout(self.page_load_timeout)
                except Exception:
                    pass
                self.selenium_driver = driver
            
            if is_doi:
                url = URLjoin(self.scihub_url, identifier)
            else:
                url = URLjoin(self.scihub_url, identifier)
            
            try:
                driver.get(url)
            except TimeoutException:
                return None, None
            except Exception:
                return None, None
            
            # Wait briefly for JavaScript-rendered content
            time.sleep(1)
            
            html = driver.page_source
            
            # Check for error pages
            is_error, error_type = self._is_error_page(html)
            if is_error:
                if error_type == 'not_available':
                    raise SciHubDownloadError("Paper not available in Sci-Hub database")
                return None, None
            
            # Extract PDF link
            pdf_link = getSchiHubPDF(html)
            
            if pdf_link:
                # Make sure link is absolute
                if pdf_link.startswith('//'):
                    pdf_link = 'https:' + pdf_link
                elif not pdf_link.startswith('http'):
                    pdf_link = URLjoin(self.scihub_url, pdf_link.lstrip('/'))
                
                # Navigate to PDF
                try:
                    driver.get(pdf_link)
                except TimeoutException:
                    return None, None
                except Exception:
                    return None, None
                time.sleep(1)
                
                # Get PDF content from page source or download
                # For PDFs, Selenium may not give us the content directly
                # We'll use requests with the same session cookies
                cookies = driver.get_cookies()
                session = requests.Session()
                for cookie in cookies:
                    session.cookies.set(cookie['name'], cookie['value'])
                session.headers.update(NetInfo.HEADERS)
                
                pdf_response = session.get(pdf_link, timeout=self.http_timeout)
                pdf_response.raise_for_status()
                
                if self._is_valid_pdf(pdf_response.content):
                    return pdf_response.content, pdf_response.url
            
            return None, None
            
        except Exception as e:
            return None, None
    
    def download(self, identifier, is_doi=True):
        """
        Download a paper using hybrid approach (HTTP first, then Selenium).
        Tries multiple Sci-Hub mirrors before giving up.
        
        Args:
            identifier: DOI or URL to download
            is_doi: Whether identifier is a DOI (True) or URL (False)
            
        Returns:
            tuple: (pdf_content: bytes, source_url: str, mirror_url: str)
            
        Raises:
            SciHubDownloadError: If download fails after all attempts (with error message)
        """
        mirrors = self._get_available_mirrors()
        last_error = None
        not_available_error = None
        
        # Try each mirror (ordered preference: .st then .se)
        for mirror_idx, mirror_url in enumerate(mirrors[:2]):
            original_url = self.scihub_url
            self.scihub_url = mirror_url
            
            try:
                # Try HTTP first
                pdf_content, source_url = self._download_via_http(identifier, is_doi)
                
                if pdf_content and self._is_valid_pdf(pdf_content):
                    return pdf_content, source_url, mirror_url
                
                # Fall back to Selenium if HTTP failed
                if self.use_selenium:
                    pdf_content, source_url = self._download_via_selenium(identifier, is_doi)
                    
                    if pdf_content and self._is_valid_pdf(pdf_content):
                        return pdf_content, source_url, mirror_url
                        
            except SciHubDownloadError as e:
                # If it's a "not available" error, remember it but try next mirror
                if "not available" in str(e).lower():
                    not_available_error = e
                else:
                    last_error = e
            except Exception as e:
                last_error = SciHubDownloadError(f"Error on mirror {mirror_url}: {str(e)}")
            finally:
                # Restore original URL
                self.scihub_url = original_url
        
        # If we got a "not available" error from any mirror, that's definitive
        if not_available_error:
            raise not_available_error
        
        # Otherwise raise the last error or a generic one
        if last_error:
            raise last_error
        
        raise SciHubDownloadError(f"Failed to download paper from {len(mirrors[:2])} mirrors: {identifier}")
    
    def close(self):
        """Clean up resources (close Selenium driver if created)."""
        if self.selenium_driver:
            try:
                self.selenium_driver.quit()
            except:
                pass
            self.selenium_driver = None

