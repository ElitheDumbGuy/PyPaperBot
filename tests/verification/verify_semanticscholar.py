import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from sources.semanticscholar import SemanticScholarSource

def verify_semanticscholar():
    print("\n[Semantic Scholar Verification]")
    try:
        source = SemanticScholarSource()
        print("Searching for 'deep learning'...")
        results = source.search("deep learning", limit=3)
        print(f"Found {len(results)} papers.")
        
        if len(results) > 0:
            p = results[0]
            print(f"Sample Paper: {p.title} ({p.year})")
            print(f"Citations: {p.citation_count}")
            print("[OK] Semantic Scholar Works")
        else:
            print("[FAIL] Semantic Scholar returned no results")
    except Exception as e:
        print(f"[FAIL] Semantic Scholar Failed: {e}")

if __name__ == "__main__":
    verify_semanticscholar()

