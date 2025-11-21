import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from sources.arxiv import ArxivSource

def verify_arxiv():
    print("\n[ArXiv Verification]")
    try:
        source = ArxivSource()
        print("Searching for 'neural networks'...")
        results = source.search("neural networks", limit=3)
        print(f"Found {len(results)} papers.")
        
        if len(results) > 0:
            p = results[0]
            print(f"Sample Paper: {p.title} ({p.year})")
            print(f"ArXiv ID: {p.arxiv_id}")
            print("[OK] ArXiv Works")
        else:
            print("[FAIL] ArXiv returned no results")
    except Exception as e:
        print(f"[FAIL] ArXiv Failed: {e}")

if __name__ == "__main__":
    verify_arxiv()

