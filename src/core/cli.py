# -*- coding: utf-8 -*-

import argparse
import sys
import os
import io
import warnings
from urllib.parse import urljoin

from models.paper import Paper
from utils.papers_filters import filterJurnals, filter_min_date
from extractors.downloader import download_papers
from extractors.scholar import get_scholar_papers_info
from extractors.crossref import getPapersInfoFromDOIs
from utils.proxy import proxy
from core.project_manager import ProjectManager
from analysis.citation_network import CitationProcessor
from core.filtering import FilterEngine
from core.aggregator import Aggregator
from analysis.ranking import RankingEngine
from utils import suppress_errors

__version__ = "2.0.0"  # AcademicArchiver


def check_version():
    try:
        print("AcademicArchiver v" + __version__)
    except Exception:
        pass


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
            # Default to 1 page if not specified
            return range(1, 2)
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


def main():
    # Force unbuffered output for immediate feedback
    sys.stdout.reconfigure(line_buffering=True) if hasattr(sys.stdout, 'reconfigure') else None
    
    # Ensure UTF-8 output on Windows
    if sys.platform == 'win32':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass

    # Suppress OSError from undetected_chromedriver cleanup
    warnings.filterwarnings("ignore", category=DeprecationWarning)

    print("\n" + "=" * 80, flush=True)
    print("  AcademicArchiver v{}".format(__version__))
    print("  Professional Scientific Paper Downloader & Aggregator")
    print("=" * 80)
    print("\n Multi-source Search: Google Scholar, OpenAlex, Semantic Scholar, ArXiv, PubMed")
    print(" Advanced Ranking: Journal SJR, Author H-Index, Citation Impact")
    print(" Smart Filtering: Consensus detection & Evidence-based ranking\n")
    print("=" * 80 + "\n")
    
    parser = argparse.ArgumentParser(
        description='AcademicArchiver is a professional tool to search, rank, and download scientific papers.')
    
    # Core Arguments
    parser.add_argument('--query', type=str, default=None,
                        help='Search query (e.g. "machine learning")')
    parser.add_argument('--doi', type=str, default=None,
                        help='Single DOI to download')
    parser.add_argument('--doi-file', type=str, default=None,
                        help='File containing list of DOIs')
    parser.add_argument('--dwn-dir', type=str, required=True,
                        help='Directory path to save results')
    
    # Search Configuration
    parser.add_argument('--preset', type=str, default='general', choices=['general', 'medicine', 'cs', 'humanities'],
                        help='Search preset for specific fields (default: general)')
    parser.add_argument('--limit', type=int, default=10,
                        help='Number of results to fetch per source (default: 10)')
    parser.add_argument('--scholar-pages', type=str, default="1",
                        help='Number of Google Scholar pages to scrape (default: 1)')
    
    # Advanced Config
    parser.add_argument('--min-year', default=None, type=int, help='Minimal publication year')
    parser.add_argument('--scihub-mirror', default=None, type=str,
                        help='Custom Sci-Hub mirror URL')
    parser.add_argument('--scihub-mode', type=str, default='auto', choices=['auto', 'http', 'selenium'],
                        help='Sci-Hub download mode (default: auto)')
    parser.add_argument('--headless', action='store_true', default=True,
                        help='Run Chrome in headless mode (default: True)')
    parser.add_argument('--no-headless', dest='headless', action='store_false',
                        help='Show Chrome browser window')
    parser.add_argument('--expand-network', action='store_true', default=False,
                        help='Enable citation network expansion (PageRank analysis)')
    parser.add_argument('--no-interactive', action='store_true', default=False,
                        help='Skip interactive filtering and download all results')
    
    # Legacy/Compatibility Arguments (kept to prevent breaking existing scripts)
    parser.add_argument('--skip-words', type=str, default=None, help='(Legacy) Skip words in title')
    parser.add_argument('--cites', type=str, default=None, help='(Legacy) Google Scholar Cited By ID')
    parser.add_argument('--restrict', default=None, type=int, help='(Legacy) 0:Bibtex, 1:PDF')
    parser.add_argument('--max-dwn-year', default=None, type=int, help='(Legacy)')
    parser.add_argument('--max-dwn-cites', default=None, type=int, help='(Legacy)')
    parser.add_argument('--journal-filter', default=None, type=str, help='(Legacy)')
    parser.add_argument('--proxy', nargs='+', default=[], help='(Legacy) Proxy list')
    parser.add_argument('--single-proxy', type=str, default=None, help='(Legacy) Single proxy')
    parser.add_argument('--selenium-chrome-version', type=int, default=None, help='(Legacy)')
    parser.add_argument('--use-doi-as-filename', action='store_true', default=False, help='(Legacy)')
    parser.add_argument('--annas-archive-mirror', default=None, type=str, help='(Legacy)')
    parser.add_argument('--scholar-results', default=10, type=int, help='(Legacy)')

    args = parser.parse_args()

    # Setup Directories
    dwn_dir = args.dwn_dir.replace('\\', '/')
    if dwn_dir[-1] != '/':
        dwn_dir += "/"
    if not os.path.exists(dwn_dir):
        os.makedirs(dwn_dir, exist_ok=True)

    # --- Phase 1: Aggregation ---
    print("\n[Phase 1] Aggregating papers from multiple sources...")
    
    papers_map = {}
    
    # Case A: DOI List (Direct Download)
    if args.doi or args.doi_file:
        print("  > Mode: Direct DOI Retrieval")
        dois = []
        if args.doi:
            dois.append(args.doi)
        if args.doi_file:
            with open(args.doi_file, 'r', encoding='utf-8') as f:
                dois.extend([line.strip() for line in f if line.strip()])
        
        # We can use OpenAlexSource or Crossref to get metadata for these DOIs
        # For now, we use the legacy getPapersInfoFromDOIs which works well
        for doi in dois:
            print(f"  Fetching metadata for DOI: {doi}")
            p = getPapersInfoFromDOIs(doi, args.restrict)
            if p:
                papers_map[doi] = p
                
    # Case B: Search Query (The Aggregator)
    elif args.query:
        print(f"  > Mode: Search Query '{args.query}' (Preset: {args.preset})")
        aggregator = Aggregator()
        # We use args.limit for per-source limit
        papers_map = aggregator.search_all(args.query, limit_per_source=args.limit)
        
    else:
        print("Error: Please provide --query or --doi/--doi-file.")
        sys.exit(1)

    papers_list = list(papers_map.values())
    print(f"\n  > Found {len(papers_list)} unique papers.")

    # --- Phase 2: Ranking ---
    print("\n[Phase 2] Ranking and Scoring...")
    ranking_engine = RankingEngine()
    
    for p in papers_list:
        ranking_engine.calculate_score(p, preset_name=args.preset)
        
    # Sort by Score Descending
    papers_list.sort(key=lambda x: x.composite_score, reverse=True)
    
    # --- Phase 3: Network Expansion (Optional) ---
    if args.expand_network:
        print("\n[Phase 3] Expanding Citation Network...")
        # Take top N papers as seeds (e.g., top 20)
        seeds = papers_list[:20]
        
        processor = CitationProcessor(journal_csv_path='data/scimagojr 2024.csv')
        network_map = processor.build_network(seeds)
        
        # Re-Rank the expanded network
        print("  Re-ranking expanded network...")
        papers_list = list(network_map.values())
        for p in papers_list:
            # Only calc score if not already done (optimization)
            if p.composite_score == 0:
                ranking_engine.calculate_score(p, preset_name=args.preset)
        
        papers_list.sort(key=lambda x: x.composite_score, reverse=True)
        print(f"  Total papers after expansion: {len(papers_list)}")

    # --- Phase 4: Display & Filtering ---
    print("\n" + "="*80)
    print(f" {'Rank':<5} | {'Score':<5} | {'Year':<4} | {'Title'}")
    print("-" * 80)
    
    # Show top 20 results
    display_limit = min(len(papers_list), 20)
    for i in range(display_limit):
        p = papers_list[i]
        title_short = (p.title[:75] + '..') if len(p.title) > 75 else p.title
        print(f" #{i+1:<4} | {p.composite_score:>5.1f} | {p.year if p.year else '????'} | {title_short}")
        
    print("="*80 + "\n")
    
    # Interactive Filter
    if not args.no_interactive:
        filter_engine = FilterEngine()
        papers_list = filter_engine.get_filtered_list(papers_list)
    
    # --- Phase 5: Download ---
    print("\n[Phase 5] Downloading PDFs...")
    
    download_papers(
        papers_list, 
        dwn_dir, 
        num_limit=None, 
        scihub_mode=args.scihub_mode, 
        headless=args.headless
    )

    # --- Phase 6: Final Report ---
    # Generate report AFTER download to capture "Downloaded" status
    print("\n[Phase 6] Generating Report...")
    report_path = os.path.join(dwn_dir, "papers_ranked.csv")
    Paper.generateReport(papers_list, report_path)
    Paper.generateBibtex(papers_list, os.path.join(dwn_dir, "bibtex.bib"))
    print(f"  > Report saved to: {report_path}")

    print("\nDone.")


if __name__ == "__main__":
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
        import traceback
        traceback.print_exc()
        sys.exit(1)
