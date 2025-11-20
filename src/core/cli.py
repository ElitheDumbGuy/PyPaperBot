# -*- coding: utf-8 -*-

import argparse
import sys
import os
import io
import warnings
from urllib.parse import urljoin

# Updated imports for new flat layout structure
from models.paper import Paper
from utils.papers_filters import filterJurnals, filter_min_date
from extractors.downloader import download_papers
from extractors.scholar import get_scholar_papers_info
from extractors.crossref import getPapersInfoFromDOIs
from utils.proxy import proxy
from core.project_manager import ProjectManager
from analysis.citation_network import CitationProcessor
from core.filtering import FilterEngine
from utils import suppress_errors

# Define version here if not available elsewhere immediately
# or import from a central config
__version__ = "2.0.0"  # AcademicArchiver


def check_version():
    try:
        print("AcademicArchiver v" + __version__)
    except Exception:
        pass


def start(query, scholar_results, scholar_pages, dwn_dir, proxy_list, min_date=None, num_limit=None, num_limit_type=None,
          filter_jurnal_file=None, restrict=None, DOIs=None, SciHub_URL=None, chrome_version=None, cites=None,
          use_doi_as_filename=False, SciDB_URL=None, skip_words=None, headless=True, scihub_mode='auto'):

    if SciDB_URL is not None and "/scidb" not in SciDB_URL:
        SciDB_URL = urljoin(SciDB_URL, "/scidb/")

    to_download = []
    if DOIs is None:
        print("Query: {}".format(query))
        print("Cites: {}".format(cites))
        to_download = get_scholar_papers_info(query, scholar_pages, restrict, min_date, scholar_results, chrome_version,
                                              cites, skip_words, headless=headless)
    else:
        print("Downloading papers from DOIs\n")
        num = 1
        i = 0
        while i < len(DOIs):
            DOI = DOIs[i]
            print("Searching paper {} of {} with DOI {}".format(num, len(DOIs), DOI))
            papersInfo = getPapersInfoFromDOIs(DOI, restrict)
            papersInfo.use_doi_as_filename = use_doi_as_filename
            to_download.append(papersInfo)

            num += 1
            i += 1

    # Save initial CSV report before downloads (so we don't lose data if it crashes)
    if to_download:
        Paper.generateReport(to_download, dwn_dir + "result.csv")
        Paper.generateBibtex(to_download, dwn_dir + "bibtex.bib")
        print("Initial report saved to {}\n".format(dwn_dir + "result.csv"))

    if restrict != 0 and to_download:
        if filter_jurnal_file is not None:
            to_download = filterJurnals(to_download, filter_jurnal_file)

        if min_date is not None:
            to_download = filter_min_date(to_download, min_date)

        if num_limit_type is not None and num_limit_type == 0:
            to_download.sort(key=lambda x: int(x.year) if x.year is not None else 0, reverse=True)

        if num_limit_type is not None and num_limit_type == 1:
            to_download.sort(key=lambda x: int(x.cites_num) if x.cites_num is not None else 0, reverse=True)

        # Create callback to update CSV periodically during downloads
        def update_csv():
            Paper.generateReport(to_download, dwn_dir + "result.csv")
            Paper.generateBibtex(to_download, dwn_dir + "bibtex.bib")

        download_papers(to_download, dwn_dir, num_limit, SciHub_URL,
                        headless=headless, scihub_mode=scihub_mode,
                        update_csv_callback=update_csv)

        # Final CSV update after downloads complete
        Paper.generateReport(to_download, dwn_dir + "result.csv")
        Paper.generateBibtex(to_download, dwn_dir + "bibtex.bib")

        print("\n" + "=" * 80)
        print("  Download Complete!")
        print("=" * 80)
        print("\n Results saved to: {}".format(dwn_dir))
        print("   * result.csv  - Download report with sources")
        print("   * bibtex.bib  - Bibliography entries")
        print("   * *.pdf       - Downloaded papers")
        print("=" * 80 + "\n")


def main():
    # Force unbuffered output for immediate feedback
    sys.stdout.reconfigure(line_buffering=True) if hasattr(sys.stdout, 'reconfigure') else None
    
    # Ensure UTF-8 output on Windows
    if sys.platform == 'win32':
        # This might fail if stdout is redirected or not a console, so we wrap it
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass

    # Suppress OSError from undetected_chromedriver cleanup
    warnings.filterwarnings("ignore", category=DeprecationWarning)

    # Use simple ASCII characters for Windows compatibility
    print("\n" + "=" * 80, flush=True)
    print("  AcademicArchiver v{}".format(__version__))
    print("  Professional Scientific Paper Downloader")
    print("=" * 80)
    print("\n Multi-source downloads: Google Scholar -> Sci-Hub mirrors")
    print(" Smart filtering and validation")
    print(" Real-time progress tracking\n")
    print("=" * 80 + "\n")
    parser = argparse.ArgumentParser(
        description='AcademicArchiver is python tool to search and dwonload scientific papers using Google Scholar, Crossref and SciHub')
    parser.add_argument('--query', type=str, default=None,
                        help='Query to make on Google Scholar or Google Scholar page link')
    parser.add_argument('--skip-words', type=str, default=None,
                        help='List of comma separated works. Papers from Scholar containing this words on title or summary will be skipped')
    parser.add_argument('--cites', type=str, default=None,
                        help='Paper ID (from scholar address bar when you search citations) if you want get only citations of that paper')
    parser.add_argument('--doi', type=str, default=None,
                        help='DOI of the paper to download (this option uses only SciHub to download)')
    parser.add_argument('--doi-file', type=str, default=None,
                        help='File .txt containing the list of paper\'s DOIs to download')
    parser.add_argument('--scholar-pages', type=str,
                        help='If given in %%d format, the number of pages to download from the beginning. '
                             'If given in %%d-%%d format, the range of pages (starting from 1) to download (the end is included). '
                             'Each page has a maximum of 10 papers (required for --query)')
    parser.add_argument('--dwn-dir', type=str, help='Directory path in which to save the results')
    parser.add_argument('--min-year', default=None, type=int, help='Minimal publication year of the paper to download')
    parser.add_argument('--max-dwn-year', default=None, type=int,
                        help='Maximum number of papers to download sorted by year')
    parser.add_argument('--max-dwn-cites', default=None, type=int,
                        help='Maximum number of papers to download sorted by number of citations')
    parser.add_argument('--journal-filter', default=None, type=str,
                        help='CSV file path of the journal filter (More info on github)')
    parser.add_argument('--restrict', default=None, type=int, choices=[0, 1],
                        help='0:Download only Bibtex - 1:Down load only papers PDF')
    parser.add_argument('--scihub-mirror', default=None, type=str,
                        help='Mirror for downloading papers from sci-hub. If not set, it is selected automatically')
    parser.add_argument('--annas-archive-mirror', default=None, type=str,
                        help='Mirror for downloading papers from Annas Archive (SciDB). If not set, https://annas-archive.se is used')
    parser.add_argument('--scholar-results', default=10, type=int, choices=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                        help='Downloads the first x results for each scholar page(default/max=10)')
    parser.add_argument('--proxy', nargs='+', default=[],
                        help='Use proxychains, provide a seperated list of proxies to use.Please specify the argument al the end')
    parser.add_argument('--single-proxy', type=str, default=None,
                        help='Use a single proxy. Recommended if using --proxy gives errors')
    parser.add_argument('--selenium-chrome-version', type=int, default=None,
                        help='Chrome version number (major version). If provided, Selenium will be used for scholar search. Auto-detected if Chrome is installed.')
    parser.add_argument('--use-doi-as-filename', action='store_true', default=False,
                        help='Use DOIs as output file names')
    parser.add_argument('--headless', action='store_true', default=False,
                        help='Run Chrome in headless mode')
    parser.add_argument('--no-headless', dest='headless', action='store_false',
                        help='Run Chrome with visible browser window (default)')
    parser.add_argument('--scihub-mode', type=str, default='auto', choices=['auto', 'http', 'selenium'],
                        help='Sci-Hub download mode: auto (HTTP then Selenium), http (HTTP only), selenium (Selenium only). Default: auto')

    # --- New arguments for citation analysis ---
    parser.add_argument('--expand-network', action='store_true', default=False,
                        help='Enable citation network analysis and expansion.')
    parser.add_argument('--verbose', action='store_true', default=False,
                        help='Enable verbose debug output')
    # --- End new arguments ---

    args = parser.parse_args()

    if args.single_proxy is not None:
        os.environ['http_proxy'] = args.single_proxy
        os.environ['HTTP_PROXY'] = args.single_proxy
        os.environ['https_proxy'] = args.single_proxy
        os.environ['HTTPS_PROXY'] = args.single_proxy
        print("Using proxy: ", args.single_proxy)
    else:
        pchain = []
        pchain = args.proxy
        proxy(pchain)

    if args.query is None and args.doi_file is None and args.doi is None and args.cites is None:
        print("\n Error: Missing required argument")
        print("   Please provide one of: --query, --doi, --doi-file, or --cites")
        print("   Example: python -m core.cli --query=\"machine learning\" --scholar-pages=1 --dwn-dir=\"./output\"\n")
        sys.exit(1)

    if (args.query is not None and args.doi_file is not None) or (args.query is not None and args.doi is not None) or (
            args.doi is not None and args.doi_file is not None):
        print("\n Error: Conflicting arguments")
        print("   Only one of --query, --doi-file, or --doi can be used at a time\n")
        sys.exit(1)

    if args.dwn_dir is None:
        print("\n Error: Missing required argument --dwn-dir")
        print("   Please specify output directory: --dwn-dir=\"./output\"\n")
        sys.exit(1)

    if args.scholar_results != 10 and args.scholar_pages != 1:
        print("Scholar results best applied along with --scholar-pages=1")

    dwn_dir = args.dwn_dir.replace('\\', '/')
    if dwn_dir[-1] != '/':
        dwn_dir += "/"
    if not os.path.exists(dwn_dir):
        os.makedirs(dwn_dir, exist_ok=True)

    # --- New Citation Analysis Workflow ---
    if args.expand_network:
        print("\n--- Running in Citation Network Expansion Mode ---")
        project_manager = ProjectManager(dwn_dir)

        # TODO: Implement resume logic here

        # 1. Get Seed Papers
        print("\nStep 1: Acquiring seed papers from Google Scholar...")
        if args.query is None and args.doi_file is None and args.doi is None and args.cites is None:
            print("Error: For network expansion, provide an initial query, doi, or doi-file.")
            sys.exit(1)

        DOIs = None
        to_download = []
        if args.doi_file is not None or args.doi is not None:
            if args.doi:
                DOIs = [args.doi]
            else:
                DOIs = []
                f = args.doi_file.replace('\\', '/')
                with open(f, encoding='utf-8') as file_in:
                    for line in file_in:
                        DOIs.append(line.strip())

            for doi in DOIs:
                paper_info = getPapersInfoFromDOIs(doi, args.restrict)
                to_download.append(paper_info)
        else:  # Query or Cites
            scholar_pages = _get_scholar_pages(args)
            to_download = get_scholar_papers_info(args.query, scholar_pages, args.restrict, args.min_year,
                                                  args.scholar_results, args.selenium_chrome_version, args.cites,
                                                  args.skip_words, headless=args.headless)

        print(f"Acquired {len(to_download)} seed papers.")

        # 2. Build and Enrich Network
        processor = CitationProcessor(
            journal_csv_path='data/scimagojr 2024.csv'
        )
        network = processor.build_network(to_download)

        # 3. Interactive Filtering
        filter_engine = FilterEngine()
        papers_to_download_filtered = filter_engine.get_filtered_list(network)

        # 4. Download Filtered Papers
        if papers_to_download_filtered:
            print(f"\nProceeding to download {len(papers_to_download_filtered)} papers...")
            # Setup for downloader
            max_dwn, max_dwn_type = _get_max_dwn_args(args)

            def update_csv():
                Paper.generateReport(papers_to_download_filtered, os.path.join(dwn_dir, "result.csv"))
                Paper.generateBibtex(papers_to_download_filtered, os.path.join(dwn_dir, "bibtex.bib"))

            download_papers(papers_to_download_filtered, dwn_dir, max_dwn, args.scihub_mirror,
                            headless=args.headless, scihub_mode=args.scihub_mode,
                            update_csv_callback=update_csv)

            # Final report generation
            update_csv()
            print(f"\nFinal report updated: {os.path.join(dwn_dir, 'result.csv')}")

        else:
            print("No papers selected for download based on the chosen filter.")

        # 5. Save Project State
        # project_manager.save_state(network=network, cache=processor.citations_client.cache)
        project_manager.save_state(network=network)
        print(f"\nProject state saved to {project_manager.state_file}")

        # Exit after the new workflow is complete
        sys.exit()
    # --- End New Workflow ---

    if args.max_dwn_year is not None and args.max_dwn_cites is not None:
        print("\n Error: Conflicting arguments")
        print("   Only one of --max-dwn-year or --max-dwn-cites can be used at a time\n")
        sys.exit(1)

    scholar_pages = _get_scholar_pages(args)

    DOIs = None
    if args.doi_file is not None:
        DOIs = []
        f = args.doi_file.replace('\\', '/')
        with open(f, encoding='utf-8') as file_in:
            for line in file_in:
                if line[-1] == '\n':
                    DOIs.append(line[:-1])
                else:
                    DOIs.append(line)

    if args.doi is not None:
        DOIs = [args.doi]

    max_dwn = None
    max_dwn_type = None
    if args.max_dwn_year is not None:
        max_dwn = args.max_dwn_year
        max_dwn_type = 0
    if args.max_dwn_cites is not None:
        max_dwn = args.max_dwn_cites
        max_dwn_type = 1

    start(args.query, args.scholar_results, scholar_pages, dwn_dir, proxy, args.min_year, max_dwn, max_dwn_type,
          args.journal_filter, args.restrict, DOIs, args.scihub_mirror, args.selenium_chrome_version, args.cites,
          args.use_doi_as_filename, args.annas_archive_mirror, args.skip_words, args.headless, args.scihub_mode)


def _get_scholar_pages(args):
    """Helper function to parse scholar pages argument."""
    if args.query is not None or args.cites is not None:
        if args.scholar_pages:
            try:
                split = args.scholar_pages.split('-')
                if len(split) == 1:
                    return range(1, int(split[0]) + 1)
                elif len(split) == 2:
                    start_page, end_page = [int(x) for x in split]
                    return range(start_page, end_page + 1)
                else:
                    raise ValueError
            except Exception:
                print(
                    r"Error: Invalid format for --scholar-pages option. Expected: %d or %d-%d, got: " + args.scholar_pages)
                sys.exit()
        else:
            print("Error: with --query provide also --scholar-pages")
            sys.exit()
    return 0


def _get_max_dwn_args(args):
    """Helper function to parse max download arguments."""
    max_dwn = None
    max_dwn_type = None
    if args.max_dwn_year is not None:
        max_dwn = args.max_dwn_year
        max_dwn_type = 0
    if args.max_dwn_cites is not None:
        max_dwn = args.max_dwn_cites
        max_dwn_type = 1
    return max_dwn, max_dwn_type


if __name__ == "__main__":

    # Set UTF-8 encoding for stdout/stderr on Windows
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

    # Install custom exception hook to suppress Chrome cleanup errors
    suppress_errors.install()

    try:
        check_version()
        main()
    except KeyboardInterrupt:
        print("\n\n  Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n Fatal error: {e}")
        sys.exit(1)
