from os import path
import requests
import sys
import io
import urllib.parse
from ..utils.net_info import NetInfo
from .scihub import SciHubClient, SciHubDownloadError

def safe_print(text):
    """Print text safely handling Unicode characters on Windows."""
    try:
        print(text)
    except UnicodeEncodeError:
        # Fallback: replace problematic characters with ASCII equivalents
        if isinstance(text, str):
            safe_text = text.encode('ascii', errors='replace').decode('ascii')
        else:
            safe_text = str(text).encode('ascii', errors='replace').decode('ascii')
        try:
            print(safe_text)
        except Exception:
            # Last resort: just print a placeholder
            print("[Title contains unsupported characters]")


ALLOWED_SCIHUB_MIRRORS = ["https://sci-hub.mk", "https://sci-hub.vg", "https://sci-hub.al", "https://sci-hub.shop"]


def _normalize_mirror(url):
    if not url:
        return None
    return url.rstrip('/')


def get_preferred_scihub_mirrors(custom_url=None):
    mirrors = []
    normalized_allowed = [_normalize_mirror(url) for url in ALLOWED_SCIHUB_MIRRORS]
    custom_normalized = _normalize_mirror(custom_url)

    if custom_normalized:
        if custom_normalized in normalized_allowed:
            mirrors.append(custom_normalized)
        else:
            print("Warning: Custom Sci-Hub mirror '{}' is not supported. Using defaults: {}".format(
                custom_url, ", ".join(ALLOWED_SCIHUB_MIRRORS)))

    for url in normalized_allowed:
        if url not in mirrors:
            mirrors.append(url)

    # Ensure we always have at least the default mirrors
    if not mirrors:
        mirrors = normalized_allowed

    return mirrors


def getSaveDir(folder, fname):
    dir_ = path.join(folder, fname)
    n = 1
    while path.exists(dir_):
        n += 1
        dir_ = path.join(folder, f"({n}){fname}")

    return dir_


def saveFile(file_name, content, paper, dwn_source, source_label=None):
    f = open(file_name, 'wb')
    f.write(content)
    f.close()

    paper.downloaded = True
    paper.downloadedFrom = dwn_source
    if source_label:
        paper.download_source = source_label
    elif dwn_source == 1:
        paper.download_source = "SciDB"
    elif dwn_source == 2:
        paper.download_source = "Sci-Hub"
    elif dwn_source == 3:
        paper.download_source = "Google Scholar"


def _format_scihub_label(mirror_url):
    parsed = urllib.parse.urlparse(mirror_url)
    host = parsed.netloc or mirror_url
    return "Sci-Hub ({})".format(host)


def downloadPapers(papers, dwnl_dir, num_limit, SciHub_URL=None, SciDB_URL=None,
                    use_selenium=True, headless=True, selenium_driver=None, scihub_mode='auto',
                    update_csv_callback=None):

    preferred_mirrors = get_preferred_scihub_mirrors(SciHub_URL)
    NetInfo.SciHub_URL = preferred_mirrors[0]

    print("\nSci-Hub mirrors order: {}".format(" -> ".join(preferred_mirrors[:4])))
    print("The downloader will try Google Scholar first, then Sci-Hub mirrors.\n")

    # Initialize hybrid Sci-Hub client (don't pass selenium_driver - let it create its own if needed)
    scihub_client = None
    if scihub_mode in ('auto', 'selenium'):
        scihub_client = SciHubClient(
            scihub_url=NetInfo.SciHub_URL,
            use_selenium=(scihub_mode == 'selenium'),
            headless=headless,
            selenium_driver=None,  # Don't reuse Scholar's driver
            preferred_mirrors=preferred_mirrors
        )

    num_downloaded = 0
    paper_number = 1
    consecutive_failures = 0
    MAX_CONSECUTIVE_FAILURES = 5
    
    try:
        for p in papers:
            if p.canBeDownloaded() and (num_limit is None or num_downloaded < num_limit):
                try:
                    safe_print("Download {} of {} -> {}".format(paper_number, len(papers), p.title))
                    paper_number += 1

                    pdf_dir = getSaveDir(dwnl_dir, p.getFileName())

                    downloaded = False
                    download_error = None
                    paper_failed = False
                    
                    # Attempt 1: Direct PDF link (Google Scholar or OpenAlex/Unpaywall)
                    if not downloaded and p.pdf_link is not None:
                        try:
                            r = requests.get(p.pdf_link, headers=NetInfo.HEADERS, timeout=15)
                            if r.content[:4] == b'%PDF':
                                # Determine source label
                                source_label = "Direct Link"
                                if p.download_source == "OpenAlex/Unpaywall":
                                    source_label = "OpenAlex/Unpaywall"
                                elif "scholar" in p.pdf_link:
                                    source_label = "Google Scholar (direct link)"
                                    
                                saveFile(pdf_dir, r.content, p, 3, source_label)
                                downloaded = True
                                num_downloaded += 1
                                consecutive_failures = 0  # Reset on success
                                safe_print(f"  Downloaded from {source_label}")
                        except Exception:
                            pass
                    
                    # Attempt 2: Direct PDF link from scholar (if link ends with pdf)
                    if not downloaded and p.scholar_link is not None and p.scholar_link[-3:].lower() == "pdf":
                        try:
                            r = requests.get(p.scholar_link, headers=NetInfo.HEADERS, timeout=15)
                            if r.content[:4] == b'%PDF':
                                saveFile(pdf_dir, r.content, p, 3, "Google Scholar (PDF link)")
                                downloaded = True
                                num_downloaded += 1
                                consecutive_failures = 0  # Reset on success
                                safe_print("  Downloaded from Google Scholar PDF link")
                        except Exception:
                            pass

                    # Attempt 3: Sci-Hub via hybrid client (mirrors: .mk, .shop, .vg)
                    if not downloaded and p.DOI is not None and scihub_client:
                        try:
                            pdf_content, source_url, mirror_url = scihub_client.download(p.DOI, is_doi=True)
                            saveFile(
                                pdf_dir,
                                pdf_content,
                                p,
                                2,
                                _format_scihub_label(mirror_url)
                            )
                            downloaded = True
                            num_downloaded += 1
                            consecutive_failures = 0  # Reset on success
                            safe_print("  Downloaded from Sci-Hub (DOI) via {}".format(mirror_url))
                        except SciHubDownloadError as e:
                            error_msg = str(e)
                            if "not available" in error_msg.lower():
                                safe_print("  Sci-Hub: Paper not available in database")
                                download_error = "Not available in Sci-Hub"
                            else:
                                safe_print("  Sci-Hub: Download failed - {}".format(error_msg))
                                download_error = "Sci-Hub error: " + error_msg[:50]
                            paper_failed = True
                        except Exception as e:
                            error_type = type(e).__name__
                            safe_print("  Sci-Hub: Download failed ({})".format(error_type))
                            download_error = "Sci-Hub error: " + error_type
                            paper_failed = True
                    
                    # Attempt 4: Sci-Hub via hybrid client (using scholar link if no DOI)
                    if not downloaded and p.scholar_link is not None and scihub_client:
                        try:
                            pdf_content, source_url, mirror_url = scihub_client.download(p.scholar_link, is_doi=False)
                            saveFile(
                                pdf_dir,
                                pdf_content,
                                p,
                                2,
                                _format_scihub_label(mirror_url)
                            )
                            downloaded = True
                            num_downloaded += 1
                            safe_print("  Downloaded from Sci-Hub (Scholar link) via {}".format(mirror_url))
                        except SciHubDownloadError as e:
                            error_msg = str(e)
                            if "not available" in error_msg.lower():
                                safe_print("  Sci-Hub: Paper not available in database")
                                if not download_error:
                                    download_error = "Not available in Sci-Hub"
                            else:
                                safe_print("  Sci-Hub: Download failed - {}".format(error_msg))
                                if not download_error:
                                    download_error = "Sci-Hub error: " + error_msg[:50]
                        except Exception as e:
                            error_type = type(e).__name__
                            safe_print("  Sci-Hub: Download failed ({})".format(error_type))
                            if not download_error:
                                download_error = "Sci-Hub error: " + error_type
                    
                    if not downloaded:
                        safe_print("  Failed to download: {}".format(p.title))
                        if download_error:
                            safe_print("  Error: {}".format(download_error))
                        # Mark as failed in paper object (for CSV reporting)
                        p.downloaded = False
                        p.downloadedFrom = 0
                        p.download_source = ""
                        
                        # Track consecutive failures
                        if paper_failed:
                            consecutive_failures += 1
                        
                        # Early termination check
                        if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                            print("\n[STOP] {} consecutive download failures.".format(MAX_CONSECUTIVE_FAILURES))
                            print("This may indicate Sci-Hub is down or blocking requests.")
                            print("Successfully downloaded {} papers before stopping.\n".format(num_downloaded))
                            break
                    
                    # Update CSV every 10 papers to avoid losing progress
                    if update_csv_callback and paper_number % 10 == 0:
                        try:
                            update_csv_callback()
                        except Exception:
                            pass  # Don't fail downloads if CSV update fails
                
                except Exception as e:
                    # Catch any unexpected errors during paper processing
                    safe_print("  ERROR processing paper: {} - {}".format(p.title[:50] if p.title else "Unknown", type(e).__name__))
                    p.downloaded = False
                    p.downloadedFrom = 0
                    # Continue with next paper
                    continue
    
    finally:
        # Clean up Sci-Hub client resources
        if scihub_client:
            scihub_client.close()
