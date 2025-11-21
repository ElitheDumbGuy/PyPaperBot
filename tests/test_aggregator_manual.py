import sys
import os
import logging

# Ensure src is in path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from core.aggregator import Aggregator, ArxivSource, SemanticScholarSource, OpenAlexSource

def test_sources():
    print("=== Testing Individual Sources ===")
    
    # 1. Test ArXiv
    print("\n1. Testing ArXiv Source...")
    arxiv = ArxivSource()
    results = arxiv.search("machine learning", limit=3)
    if results:
        print(f"   SUCCESS: Found {len(results)} papers.")
        print(f"   Sample: {results[0].title} ({results[0].year})")
        print(f"   PDF: {results[0].pdf_link}")
    else:
        print("   FAILURE: No results found.")

    # 2. Test Semantic Scholar
    print("\n2. Testing Semantic Scholar Source...")
    sem = SemanticScholarSource()
    results = sem.search("machine learning", limit=3)
    if results:
        print(f"   SUCCESS: Found {len(results)} papers.")
        print(f"   Sample: {results[0].title} ({results[0].year})")
        print(f"   Citations: {results[0].citation_count}")
    else:
        print("   FAILURE: No results found.")

    # 3. Test OpenAlex
    print("\n3. Testing OpenAlex Source...")
    oa = OpenAlexSource()
    results = oa.search("machine learning", limit=3)
    if results:
        print(f"   SUCCESS: Found {len(results)} papers.")
        print(f"   Sample: {results[0].title} ({results[0].year})")
        print(f"   DOI: {results[0].DOI}")
    else:
        print("   FAILURE: No results found.")

def test_aggregator():
    print("\n=== Testing Aggregator (Merge Logic) ===")
    agg = Aggregator()
    # We search for a very specific paper to test deduplication
    query = "Attention is all you need"
    print(f"Searching all sources for: '{query}'")
    
    results = agg.search_all(query, limit_per_source=2)
    
    print(f"\nTotal Unique Papers: {len(results)}")
    for key, p in results.items():
        if "Attention is all you need" in p.title:
            print(f"\nTarget Paper Found: {p.title}")
            print(f"Sources: {p.sources}")
            print(f"DOI: {p.DOI}")
            print(f"Citations: {p.citation_count}")
            print(f"Merged Correctly? {'yes' if len(p.sources) > 1 else 'no'}")

if __name__ == "__main__":
    # Suppress connection logs for cleaner output
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    test_sources()
    test_aggregator()

