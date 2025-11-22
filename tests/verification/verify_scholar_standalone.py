import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from sources.google_scholar import GoogleScholarSource

def verify_scholar():
    print("\n[Google Scholar Verification]")
    print("Note: This requires Chrome/Selenium and may fail if blocked.")
    try:
        # Try with headless=False to see if it helps with detection
        print("Initializing Google Scholar Source (Headless=False)...")
        source = GoogleScholarSource(headless=False)
        
        print("Searching for 'quantum computing'...")
        results = source.search("quantum computing", limit=3)
        print(f"Found {len(results)} papers.")
        
        if len(results) > 0:
            p = results[0]
            print(f"Sample Paper: {p.title} ({p.year})")
            print("[OK] Google Scholar Works")
        else:
            print("[FAIL] Google Scholar returned no results. Possible CAPTCHA or parsing error.")
            
    except Exception as e:
        print(f"[FAIL] Google Scholar Failed: {e}")

if __name__ == "__main__":
    verify_scholar()

