import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from sources.openalex import OpenAlexSource

def verify_openalex():
    print("\n[OpenAlex Verification]")
    try:
        source = OpenAlexSource()
        print("Searching for 'machine learning'...")
        results = source.search("machine learning", limit=3)
        print(f"Found {len(results)} papers.")
        
        if len(results) > 0:
            p = results[0]
            print(f"Sample Paper: {p.title} ({p.year})")
            print(f"DOI: {p.DOI}")
            print("[OK] OpenAlex Works")
        else:
            print("[FAIL] OpenAlex returned no results")
    except Exception as e:
        print(f"[FAIL] OpenAlex Failed: {e}")

if __name__ == "__main__":
    verify_openalex()

