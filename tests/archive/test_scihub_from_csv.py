#!/usr/bin/env python3
"""
Test Sci-Hub downloads using DOIs from result.csv
ONLY tests Sci-Hub - does not involve Google Scholar.
"""

import sys
import os
import csv

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from PyPaperBot.scihub_client import SciHubClient, SciHubDownloadError

def test_scihub_downloads():
    """Test downloading papers from Sci-Hub using DOIs from CSV"""
    
    # Read DOIs from CSV
    csv_path = "tests/test_files/test_maladaptive4/result.csv"
    dois = []
    
    print("Reading DOIs from CSV...")
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            doi = row.get('DOI', '').strip()
            if doi:
                dois.append({
                    'doi': doi,
                    'title': row.get('Title', 'Unknown')[:50]
                })
    
    print(f"Found {len(dois)} DOIs to test\n")
    
    # Test with Sci-Hub client
    client = SciHubClient(
        preferred_mirrors=["https://sci-hub.mk", "https://sci-hub.shop", "https://sci-hub.vg"],
        use_selenium=False,
        headless=False
    )
    
    results = {
        'success': [],
        'failed': []
    }
    
    # Test first 10 DOIs
    test_count = min(10, len(dois))
    print(f"Testing {test_count} DOIs...\n")
    
    for i, paper in enumerate(dois[:test_count], 1):
        doi = paper['doi']
        title = paper['title']
        
        print(f"\n[{i}/{test_count}] Testing: {title}")
        print(f"  DOI: {doi}")
        
        try:
            pdf_content, source_url, mirror = client.download(doi, is_doi=True)
            
            if pdf_content:
                # Save PDF to verify
                filename = f"tests/test_downloads/{doi.replace('/', '_')}.pdf"
                os.makedirs("tests/test_downloads", exist_ok=True)
                with open(filename, 'wb') as f:
                    f.write(pdf_content)
                
                print(f"  ✓ SUCCESS - Downloaded {len(pdf_content)} bytes from {mirror}")
                print(f"  Saved to: {filename}")
                results['success'].append({
                    'doi': doi,
                    'title': title,
                    'mirror': mirror,
                    'size': len(pdf_content)
                })
            else:
                print(f"  ✗ FAILED - No content returned")
                results['failed'].append({
                    'doi': doi,
                    'title': title,
                    'reason': 'No content'
                })
                
        except SciHubDownloadError as e:
            print(f"  ✗ FAILED - {e}")
            results['failed'].append({
                'doi': doi,
                'title': title,
                'reason': str(e)
            })
        except Exception as e:
            print(f"  ✗ ERROR - {type(e).__name__}: {e}")
            results['failed'].append({
                'doi': doi,
                'title': title,
                'reason': f"{type(e).__name__}: {e}"
            })
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total tested: {test_count}")
    print(f"Successful: {len(results['success'])}")
    print(f"Failed: {len(results['failed'])}")
    print(f"Success rate: {len(results['success'])/test_count*100:.1f}%")
    
    if results['success']:
        print("\n✓ Successful downloads:")
        for r in results['success']:
            print(f"  - {r['title'][:40]}... ({r['size']} bytes from {r['mirror']})")
    
    if results['failed']:
        print("\n✗ Failed downloads:")
        for r in results['failed']:
            print(f"  - {r['title'][:40]}... ({r['reason']})")
    
    client.close()
    
    return results

if __name__ == "__main__":
    test_scihub_downloads()

