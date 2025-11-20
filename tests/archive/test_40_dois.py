#!/usr/bin/env python3
"""
Test Sci-Hub downloads with 40 specific DOIs.
ONLY tests Sci-Hub - does not involve Google Scholar.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from PyPaperBot.scihub_client import SciHubClient, SciHubDownloadError

# 40 DOIs to test
TEST_DOIS = [
    "10.1023/a:1020597026919",
    "10.1097/nmd.0000000000000685",
    "10.1016/j.amp.2019.08.014",
    "10.54079/jpmi.37.1.3087",
    "10.1016/j.concog.2016.03.017",
    "10.4103/ijsp.ijsp_227_21",
    "10.1097/nmd.0000000000000507",
    "10.1002/ijop.70027",
    "10.3389/fpsyt.2022.871041",
    "10.1080/15299732.2016.1160463",
    "10.3389/fpsyt.2018.00194",
    "10.1016/j.psychres.2020.112799",
    "10.1002/cpp.70104",
    "10.1037/cns0000114",
    "10.1192/bjp.2024.279",
    "10.1176/appi.prcp.20190050",
    "10.4324/9781003057314-41",
    "10.1016/j.paid.2023.112279",
    "10.1016/j.comppsych.2023.152441",
    "10.1016/j.paid.2021.111194",
    "10.3390/ijerph19010386",
    "10.1080/10400419.2023.2230022",
    "10.1016/j.paid.2021.111194",  # Duplicate
    "10.1016/j.aip.2018.12.004",
    "10.3389/fpsyg.2021.631979",
    "10.1556/2006.2020.00050",
    "10.1177/0276236619864277",
    "10.1080/00223891.2019.1594240",
    "10.1371/journal.pone.0225529",
    "10.1007/s11469-022-00938-3",
    "10.1556/2006.2020.00080",
    "10.1002/cpp.2844",
    "10.1002/jclp.23355",
    "10.1037/cns0000162",
    "10.1037/cns0000253",
    "10.1108/mhsi-01-2023-0014",
    "10.1556/2006.2023.00001",
    "10.1080/09540261.2025.2562185",
    "10.1007/s12144-024-06382-x",
    "10.7759/cureus.10776",
]

def test_scihub_40_dois():
    """Test downloading 40 papers from Sci-Hub"""
    
    print("="*70)
    print("SCI-HUB TEST: 40 DOIs")
    print("="*70)
    print(f"Testing {len(TEST_DOIS)} DOIs with 4 mirrors\n")
    
    # Initialize client with all 4 mirrors
    client = SciHubClient(
        preferred_mirrors=["https://sci-hub.mk", "https://sci-hub.vg", "https://sci-hub.al", "https://sci-hub.shop"],
        use_selenium=False,
        headless=False
    )
    
    results = {
        'success': [],
        'failed': []
    }
    
    # Test all DOIs
    for i, doi in enumerate(TEST_DOIS, 1):
        print(f"\n[{i}/{len(TEST_DOIS)}] DOI: {doi}")
        
        try:
            pdf_content, source_url, mirror = client.download(doi, is_doi=True)
            
            if pdf_content:
                # Save PDF
                filename = f"tests/test_40_downloads/{doi.replace('/', '_').replace(':', '_')}.pdf"
                os.makedirs("tests/test_40_downloads", exist_ok=True)
                with open(filename, 'wb') as f:
                    f.write(pdf_content)
                
                print(f"  [OK] {len(pdf_content):,} bytes from {mirror}")
                results['success'].append({
                    'doi': doi,
                    'mirror': mirror,
                    'size': len(pdf_content)
                })
            else:
                print(f"  [FAIL] No content returned")
                results['failed'].append({
                    'doi': doi,
                    'reason': 'No content'
                })
                
        except SciHubDownloadError as e:
            print(f"  [FAIL] {e}")
            results['failed'].append({
                'doi': doi,
                'reason': str(e)
            })
        except Exception as e:
            print(f"  [ERROR] {type(e).__name__}: {e}")
            results['failed'].append({
                'doi': doi,
                'reason': f"{type(e).__name__}: {e}"
            })
    
    # Summary
    print("\n" + "="*70)
    print("FINAL SUMMARY")
    print("="*70)
    print(f"Total tested: {len(TEST_DOIS)}")
    print(f"Successful: {len(results['success'])}")
    print(f"Failed: {len(results['failed'])}")
    print(f"Success rate: {len(results['success'])/len(TEST_DOIS)*100:.1f}%")
    
    # Mirror breakdown
    if results['success']:
        mirror_counts = {}
        for r in results['success']:
            mirror = r['mirror']
            mirror_counts[mirror] = mirror_counts.get(mirror, 0) + 1
        
        print("\nDownloads by mirror:")
        for mirror, count in sorted(mirror_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {mirror}: {count} papers")
    
    if results['failed']:
        print(f"\nFailed downloads: {len(results['failed'])}")
        # Show first 5 failures
        for r in results['failed'][:5]:
            print(f"  - {r['doi']}: {r['reason']}")
        if len(results['failed']) > 5:
            print(f"  ... and {len(results['failed']) - 5} more")
    
    client.close()
    
    return results

if __name__ == "__main__":
    test_scihub_40_dois()

