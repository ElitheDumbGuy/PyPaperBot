import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from sources.core import CoreSource

def verify_core():
    print("\n[CORE Verification]")
    try:
        source = CoreSource() # No API key by default
        print("Searching for 'open access'...")
        results = source.search("open access", limit=3)
        print(f"Found {len(results)} papers.")
        
        if len(results) > 0:
            p = results[0]
            print(f"Sample Paper: {p.title} ({p.year})")
            print(f"CORE ID: {p.core_id}")
            print("[OK] CORE Works")
        else:
            print("[WARN] CORE returned no results (May require API Key)")
    except Exception as e:
        print(f"[FAIL] CORE Failed: {e}")

if __name__ == "__main__":
    verify_core()

