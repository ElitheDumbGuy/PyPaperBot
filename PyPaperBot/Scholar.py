# -*- coding: utf-8 -*-
"""
Google Scholar search and paper information retrieval module.

This module handles searching Google Scholar and extracting paper metadata
using either direct HTTP requests or Selenium browser automation.
"""

import time
import requests
import functools
import os
import re
import subprocess
import platform
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from .HTMLparsers import schoolarParser
from .Crossref import getPapersInfo
from .NetInfo import NetInfo


def waithIPchange():
    """Wait for user to change IP or continue after being blocked."""
    while True:
        inp = input('You have been blocked, try changing your IP or using a VPN. '
                    'Press Enter to continue downloading, or type "exit" to stop and exit....')
        if inp.strip().lower() == "exit":
            return False
        elif not inp.strip():
            print("Wait 30 seconds...")
            time.sleep(30)
            return True


def _detect_chrome_path():
    """
    Detect Chrome browser installation path based on the operating system.
    
    Returns:
        str: Path to Chrome executable, or None if not found
    """
    system = platform.system()
    
    if system == "Windows":
        # Common Windows Chrome installation paths
        possible_paths = [
            os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
    elif system == "Darwin":  # macOS
        path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        if os.path.exists(path):
            return path
    elif system == "Linux":
        # Common Linux Chrome paths
        possible_paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/chromium-browser",
            "/usr/bin/chromium",
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
    
    return None


def _detect_chrome_version(chrome_path):
    """
    Detect Chrome version by running Chrome with --version flag or reading from installation.
    
    Args:
        chrome_path: Path to Chrome executable
        
    Returns:
        int: Major version number, or None if detection fails
    """
    if not chrome_path or not os.path.exists(chrome_path):
        return None
    
    # Try reading version from Windows registry first (faster)
    if platform.system() == "Windows":
        try:
            import winreg
            key_path = r"SOFTWARE\Google\Chrome\BLBeacon"
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path)
                version = winreg.QueryValueEx(key, "version")[0]
                winreg.CloseKey(key)
                match = re.search(r"(\d+)", version)
                if match:
                    return int(match.group(1))
            except (FileNotFoundError, OSError):
                # Try Local Machine key
                try:
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)
                    version = winreg.QueryValueEx(key, "version")[0]
                    winreg.CloseKey(key)
                    match = re.search(r"(\d+)", version)
                    if match:
                        return int(match.group(1))
                except (FileNotFoundError, OSError):
                    pass
        except ImportError:
            pass  # winreg not available
    
    # Fallback: try running Chrome with --version (may timeout)
    try:
        command = [chrome_path, "--version"]
        result = subprocess.run(command, capture_output=True, text=True, check=True, timeout=5)
        version_string = result.stdout.strip() or result.stderr.strip()
        match = re.search(r"(\d+)", version_string)
        if match:
            return int(match.group(1))
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, ValueError, Exception):
        pass
    
    # Last resort: try to use undetected_chromedriver's auto-detection
    try:
        import undetected_chromedriver as uc
        # This will raise an exception if it can't detect, but we can catch it
        # Actually, let's just return None and let undetected_chromedriver handle it
        return None
    except Exception:
        return None


def scholar_requests(scholar_pages, url, restrict, chrome_version, scholar_results=10, headless=True):
    """
    Fetch papers from Google Scholar using either Selenium or direct HTTP requests.
    
    Args:
        scholar_pages: Range or list of page numbers to fetch
        url: Google Scholar search URL template
        restrict: Restriction flag for Crossref lookup
        chrome_version: Chrome version number (None = auto-detect or use HTTP)
        scholar_results: Number of results per page (default: 10)
        headless: Whether to run Chrome in headless mode (default: True)
        
    Returns:
        list: List of lists containing Paper objects
    """
    javascript_error = "Sorry, we can't verify that you're not a robot when JavaScript is turned off"
    to_download = []
    driver = None

    # Auto-detect Chrome installation and version
    detected_version = None
    chrome_path = None
    use_selenium = False
    
    # Always try to detect Chrome, even if chrome_version is not provided
    chrome_path = _detect_chrome_path()
    
    if chrome_path is None:
        if chrome_version is not None:
            print("Warning: Chrome browser not found. Falling back to HTTP requests mode.")
            print("Please install Google Chrome or specify Chrome path manually.")
        chrome_version = None
        use_selenium = False
    else:
        # Try to detect version, but don't fail if we can't - let undetected_chromedriver handle it
        detected_version = _detect_chrome_version(chrome_path)
        
        if detected_version is not None:
            # Use detected version if chrome_version was not provided, or verify provided version
            if chrome_version is None:
                chrome_version = detected_version
                print(f"Auto-detected Chrome version {detected_version} at: {chrome_path}")
            elif chrome_version != detected_version:
                print(f"Warning: Specified Chrome version ({chrome_version}) differs from detected version ({detected_version}).")
                print(f"Using detected version: {detected_version}")
                chrome_version = detected_version
            else:
                print(f"Using Chrome version {detected_version} at: {chrome_path}")
            use_selenium = True
        else:
            # Version detection failed, but Chrome exists - let undetected_chromedriver auto-detect
            if chrome_version is not None:
                print(f"Using specified Chrome version {chrome_version} at: {chrome_path}")
                use_selenium = True
            else:
                print(f"Chrome found at {chrome_path}, but version detection failed.")
                print("Attempting to use Selenium with auto-detection...")
                use_selenium = True
                chrome_version = None  # Let undetected_chromedriver auto-detect

    for i in scholar_pages:
        while True:
            res_url = url % (scholar_results * (i - 1))

            if use_selenium and chrome_path:
                if driver is None:
                    print(f"Using Selenium driver (Headless={headless})")
                    try:
                        # Create driver with or without version_main depending on detection
                        driver_options = {
                            'headless': headless,
                            'use_subprocess': False,
                            'binary_location': chrome_path
                        }
                        if chrome_version is not None:
                            driver_options['version_main'] = chrome_version
                            print(f"Initializing Chrome driver with version {chrome_version}...")
                        else:
                            print("Initializing Chrome driver with auto-detection...")
                        
                        driver = uc.Chrome(**driver_options)
                        print("Chrome driver initialized successfully.")
                    except Exception as e:
                        print(f"Failed to initialize Chrome driver: {e}")
                        print("Falling back to HTTP requests mode.")
                        use_selenium = False
                        driver = None

                if driver is not None:
                    try:
                        print(f"Loading Google Scholar page: {res_url}")
                        driver.get(res_url)
                        
                        # Wait for page to load - Google Scholar uses JavaScript heavily
                        # Wait for specific elements that indicate results are loaded
                        try:
                            # Wait for search results container (up to 15 seconds)
                            # Try multiple selectors as Google Scholar structure may vary
                            wait = WebDriverWait(driver, 15)
                            try:
                                wait.until(EC.presence_of_element_located((By.CLASS_NAME, "gs_r")))
                                print("Search results loaded.")
                            except Exception:
                                # Try alternative selector
                                try:
                                    wait.until(EC.presence_of_element_located((By.ID, "gs_res_ccl")))
                                    print("Search results container found.")
                                except Exception:
                                    # Last resort: wait for any content
                                    wait.until(lambda d: len(d.page_source) > 10000)
                                    print("Page content loaded.")
                        except Exception as e:
                            # If all waits fail, wait a fixed time
                            print(f"Waiting for page to load (element detection failed: {type(e).__name__})...")
                            time.sleep(8)  # Increased wait time for headless mode
                        
                        html = driver.page_source
                        
                        # Verify we got actual content
                        if len(html) < 1000:
                            print("Warning: Received very short HTML response, page may not have loaded correctly.")
                    except Exception as e:
                        print(f"Error loading page: {e}")
                        html = None
                else:
                    html = None

            if not use_selenium or html is None or html == "":
                # Fallback to HTTP requests
                if use_selenium and html is None:
                    print("Selenium failed, falling back to HTTP requests mode.")
                    use_selenium = False
                
                try:
                    response = requests.get(res_url, headers=NetInfo.HEADERS, timeout=30)
                    html = response.text
                except Exception as e:
                    print(f"HTTP request failed: {e}")
                    html = ""

            if html and javascript_error in html:
                # Bot detection triggered - wait for user to change IP
                is_continue = waithIPchange()
                if not is_continue:
                    if driver:
                        driver.quit()
                    return to_download
            else:
                break

        papers = schoolarParser(html)
        
        # Limit to requested number of results per page
        if len(papers) > scholar_results:
            papers = papers[0:scholar_results]

        print("\nGoogle Scholar page {} : {} papers found".format(i, len(papers)))

        if len(papers) > 0:
            papersInfo = getPapersInfo(papers, url, restrict, scholar_results)
            info_valids = functools.reduce(lambda a, b: a + 1 if b.DOI is not None else a, papersInfo, 0)
            print("Papers found on Crossref: {}/{}\n".format(info_valids, len(papers)))

            to_download.append(papersInfo)
        else:
            print("No papers found on this page...")

    # Clean up driver if created
    if driver:
        driver.quit()

    return to_download


def parseSkipList(skip_words):
    skip_list = skip_words.split(",")
    print("Skipping results containing {}".format(skip_list))
    output_param = ""
    for skip_word in skip_list:
        skip_word = skip_word.strip()
        if " " in skip_word:
            output_param += '+-"' + skip_word + '"'
        else:
            output_param += '+-' + skip_word
    return output_param


def ScholarPapersInfo(query, scholar_pages, restrict, min_date=None, scholar_results=10, chrome_version=None,
                      cites=None, skip_words=None, headless=True):
    """
    Search Google Scholar and retrieve paper information.
    
    Args:
        query: Search query string or Google Scholar URL
        scholar_pages: Range or list of page numbers to fetch
        restrict: Restriction flag for Crossref lookup
        min_date: Minimum publication year filter
        scholar_results: Number of results per page (default: 10)
        chrome_version: Chrome version number for Selenium (None = auto-detect or HTTP)
        cites: Paper ID for citation search
        skip_words: Comma-separated words to exclude from results
        headless: Whether to run Chrome in headless mode (default: True)
        
    Returns:
        list: Flat list of Paper objects
    """
    url = r"https://scholar.google.com/scholar?hl=en&as_vis=1&as_sdt=1,5&start=%d"
    if query:
        if len(query) > 7 and (query.startswith("http://") or query.startswith("https://")):
            url = query
        else:
            url += f"&q={query}"
        if skip_words:
            url += parseSkipList(skip_words)
            print(url)
    if cites:
        url += f"&cites={cites}"
    if min_date:
        url += f"&as_ylo={min_date}"

    to_download = scholar_requests(scholar_pages, url, restrict, chrome_version, scholar_results, headless=headless)

    return [item for sublist in to_download for item in sublist]