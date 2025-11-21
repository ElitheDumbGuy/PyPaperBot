import sys
import os
import logging

# Ensure src is in path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from core.aggregator import PubMedSource

def test_pubmed():
    print("=== Testing PubMed Source ===")
    pm = PubMedSource()
    # Search for something medical to ensure results
    query = "COVID-19 vaccine efficacy" 
    print(f"Searching for: {query}")
    
    results = pm.search(query, limit=3)
    
    if results:
        print(f"   SUCCESS: Found {len(results)} papers.")
        for i, p in enumerate(results):
            print(f"\n   Paper {i+1}:")
            print(f"   Title: {p.title}")
            print(f"   Year: {p.year}")
            print(f"   Authors: {p.authors[:50]}...") # Truncate authors
            print(f"   Journal: {p.jurnal}")
            print(f"   DOI: {p.DOI}")
    else:
        print("   FAILURE: No results found.")

if __name__ == "__main__":
    # Suppress connection logs
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    test_pubmed()

