import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from core.aggregator import Aggregator

def verify_aggregator():
    print("\n[Aggregator Integration Verification]")
    print("Initializing Aggregator (this includes Google Scholar, so Chrome will launch)...")
    
    try:
        # We can't easily patch GoogleScholarSource inside Aggregator to be non-headless 
        # without modifying Aggregator code or using mocks.
        # For this test, we assume the Aggregator uses the defaults (headless=True).
        # If Scholar fails (likely in headless), it should just log an error and continue.
        
        agg = Aggregator()
        print("Searching for 'ensemble learning' across all sources (Limit=2)...")
        
        results = agg.search_all("ensemble learning", limit_per_source=2)
        
        print(f"\nTotal unique papers found: {len(results)}")
        
        sources_found = set()
        for p in results.values():
            sources_found.update(p.sources)
            
        print(f"Sources contributing: {sources_found}")
        
        # Check if we have at least some papers
        if len(results) > 0:
            print("[OK] Aggregator returned results.")
            
            # Check if we have mixed sources (ideal, but not strictly required if some fail)
            if len(sources_found) > 1:
                print(f"[OK] Multi-source aggregation working ({len(sources_found)} sources).")
            else:
                print(f"[WARN] Only one source contributed: {sources_found}")
        else:
            print("[FAIL] Aggregator returned 0 results.")

    except Exception as e:
        print(f"[FAIL] Aggregator crashed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_aggregator()

