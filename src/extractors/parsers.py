# -*- coding: utf-8 -*-
"""
Created on Sun Jun  7 11:59:42 2020

@author: Vito
"""
import re
from bs4 import BeautifulSoup
from lxml import etree


def parse_scholar_results(html):
    """
    Parse Google Scholar search results HTML.
    Renamed from schoolarParser to snake_case.
    """
    result = []
    soup = BeautifulSoup(html, "html.parser")

    # ----- Core Modification -----
    #
    # Old finder (too strict):
    # for element in soup.findAll("div", class_="gs_r gs_or gs_scl"):
    #
    # New finder (using CSS selectors):
    # This finds all <div> tags that contain .gs_r, .gs_or, AND .gs_scl classes,
    # regardless of whether they contain other classes (like .gs_fmar).
    #
    for element in soup.select("div.gs_r.gs_or.gs_scl"):
        # ----- End Modification -----

        if not is_book(element):
            title = None
            link = None
            link_pdf = None
            cites = None
            year = None
            authors = None
            for h3 in element.findAll("h3", class_="gs_rt"):  # findAll is fine here
                found = False
                for a in h3.findAll("a"):
                    if not found:
                        title = a.text
                        link = a.get("href")
                        found = True
            
            # Ensure we found a title
            if not title:
                h3 = element.find("h3", class_="gs_rt")
                if h3:
                    title = h3.get_text()
            for a in element.findAll("a"):
                if "Cited by" in a.text:
                    try:  # Add try-except to avoid crash if "Cited by" is not followed by a number
                        cites = int(a.text[8:])
                    except ValueError:
                        cites = None
                if "[PDF]" in a.text:
                    link_pdf = a.get("href")
            for div in element.findAll("div", class_="gs_a"):
                try:
                    authors, source_and_year, _ = div.text.replace('\u00A0', ' ').split(" - ")
                except ValueError:
                    continue

                if not authors.strip().endswith('\u2026'):
                    # There is no ellipsis at the end so we know the full list of authors
                    authors = authors.replace(', ', ';')
                else:
                    authors = None
                try:
                    year = int(source_and_year[-4:])
                except ValueError:
                    continue
                if not (1000 <= year <= 3000):
                    year = None
                else:
                    year = str(year)
            if title is not None:
                result.append({
                    'title': title,
                    'link': link,
                    'cites': cites,
                    'link_pdf': link_pdf,
                    'year': year,
                    'authors': authors})
        else:
            # Log skipped books
            h3_tag = element.find("h3", class_="gs_rt")
            if h3_tag:
                print(f"  [Skipped Book] {h3_tag.get_text()}")
            
    return result


def is_book(tag):
    """Renamed from isBook to snake_case."""
    result = False
    for span in tag.findAll("span", class_="gs_ct2"):
        if span.text == "[B]":
            result = True
    return result


def getSchiHubPDF_fallback(html):
    """
    Extract PDF URL from Sci-Hub HTML page.
    Based on working example: check iframe -> embed -> object, in that order.
    """
    result = None
    soup = BeautifulSoup(html, "html.parser")

    # Working approach: iframe first
    iframe = soup.find('iframe')
    if iframe and iframe.has_attr('src'):
        result = iframe.get('src')

    # Then try embed
    if not result:
        embed = soup.find('embed')
        if embed and embed.has_attr('src'):
            result = embed.get('src')

    # Then try object
    if not result:
        obj = soup.find('object')
        if obj and obj.has_attr('data'):
            result = obj.get('data')

    # Fallback: plugin element
    if not result:
        plugin = soup.find(id='plugin')
        if plugin and plugin.has_attr('src'):
            result = plugin.get('src')

    # Fallback: scidb download link
    if not result:
        download_scidb = soup.find("a", text=lambda text: text and "Download" in text, href=re.compile(r"\.pdf$"))
        if download_scidb:
            result = download_scidb.get("href")

    # Handle relative URLs (prepend https:)
    if result and not result.startswith('http'):
        if result.startswith('//'):
            result = "https:" + result
        elif result.startswith('/'):
            # For absolute paths, we'd need base URL, but try https: first
            result = "https:" + result

    return result


def is_scihub_paper_not_available(html_content):
    """
    Check if Sci-Hub returned a "paper not available" page.
    Returns True if the paper is not in the database.

    Specifically looks for: "Alas, the following paper is not yet available in my database"
    """
    if not html_content:
        return False

    try:
        # Check for the specific "not yet available" message (most reliable)
        if b'not yet available in my database' in html_content:
            return True

        # Also check for the block-rounded message element with specific text
        soup = BeautifulSoup(html_content, "html.parser")
        message_block = soup.find('block-rounded', class_='message')
        if message_block:
            text = message_block.get_text().lower()
            # Only return True if it specifically mentions "not yet available" or "not available"
            if 'not yet available' in text or 'not available in my database' in text:
                return True

    except Exception:
        pass

    return False


def is_cloudflare_page(html_content):
    """
    Check if we hit a Cloudflare challenge page.
    """
    if not html_content:
        return False

    try:
        # Common Cloudflare indicators
        if b'Cloudflare' in html_content or b'cf-browser-verification' in html_content:
            return True
        if b'Just a moment' in html_content or b'Checking your browser' in html_content:
            return True
    except Exception:
        pass

    return False


def getSchiHubPDF_xpath(html_content):
    """
    Extract PDF URL from Sci-Hub HTML page using XPath.
    """
    if not html_content:
        return None

    try:
        html = etree.HTML(html_content)

        # XPath from SciHubEVA, looks for src attribute in elements with id="pdf" or inside id="article"
        pdf_xpath = '//*[@id="pdf"]/@src|//*[@id="article"]//iframe/@src'
        results = html.xpath(pdf_xpath)

        if results:
            return results[0]

    except Exception:
        # Fallback to BeautifulSoup if lxml fails, though it's less likely
        pass

    # Fallback logic from previous implementation
    result = None
    soup = BeautifulSoup(html_content, "html.parser")

    iframe = soup.find('iframe')
    if iframe and iframe.has_attr('src'):
        result = iframe.get('src')

    if not result:
        embed = soup.find('embed')
        if embed and embed.has_attr('src'):
            result = embed.get('src')

    if not result:
        obj = soup.find('object')
        if obj and obj.has_attr('data'):
            result = obj.get('data')

    return result


def get_scihub_urls(html):
    """Renamed from SciHubUrls to snake_case."""
    result = []
    soup = BeautifulSoup(html, "html.parser")

    for ul in soup.findAll("ul"):
        for a in ul.findAll("a"):
            link = a.get("href")
            if link.startswith("https://sci-hub.") or link.startswith("http://sci-hub."):
                result.append(link)

    return result
