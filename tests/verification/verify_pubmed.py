import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from sources.pubmed import PubMedSource

def verify_pubmed():
    print("\n[PubMed Verification]")
    try:
        source = PubMedSource()
        print("Searching for 'cancer immunotherapy'...")
        results = source.search("cancer immunotherapy", limit=3)
        print(f"Found {len(results)} papers.")
        
        if len(results) > 0:
            p = results[0]
            print(f"Sample Paper: {p.title} ({p.year})")
            print(f"Journal: {p.jurnal}")
            print("[OK] PubMed Works")
        else:
            print("[FAIL] PubMed returned no results")
    except Exception as e:
        print(f"[FAIL] PubMed Failed: {e}")

if __name__ == "__main__":
    verify_pubmed()

