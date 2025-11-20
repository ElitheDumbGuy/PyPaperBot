#!/usr/bin/env python3
"""
Test and compare different Sci-Hub mirrors to determine which are reliable.
Tests: sci-hub.mk, sci-hub.vg, sci-hub.al, sci-hub.shop
"""

import sys
import os
import requests
import urllib3
from lxml import etree
from urllib.parse import urlparse

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Test DOIs - known to exist in Sci-Hub
TEST_DOIS = [
    "10.1023/a:1020597026919",  # Successfully downloaded in previous test
    "10.1097/nmd.0000000000000685",  # Successfully downloaded
    "10.1016/j.amp.2019.08.014",  # Successfully downloaded
]

MIRRORS_TO_TEST = [
    "https://sci-hub.mk",
    "https://sci-hub.vg",
    "https://sci-hub.al",
    "https://sci-hub.shop",
]

def test_mirror_with_doi(mirror, doi):
    """Test a single mirror with a single DOI"""
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0'})
    
    result = {
        'mirror': mirror,
        'doi': doi,
        'post_works': False,
        'get_works': False,
        'pdf_found': False,
        'pdf_size': 0,
        'error': None
    }
    
    # Try POST first
    try:
        response = session.post(mirror, data={'request': doi}, verify=False, timeout=15)
        
        if response.status_code == 200:
            result['post_works'] = True
            
            # Try to extract PDF URL
            html = etree.HTML(response.content)
            pdf_xpath = '//*[@id="pdf"]/@src|//*[@id="article"]//iframe/@src'
            results = html.xpath(pdf_xpath)
            
            if results:
                pdf_url = results[0]
                # Normalize URL
                if not pdf_url.startswith('http'):
                    pdf_url = 'https:' + pdf_url if pdf_url.startswith('//') else f"https:{pdf_url}"
                
                # Download PDF
                pdf_response = session.get(pdf_url, verify=False, timeout=15)
                if pdf_response.content[:4] == b'%PDF':
                    result['pdf_found'] = True
                    result['pdf_size'] = len(pdf_response.content)
                    return result
        elif response.status_code == 405:
            result['error'] = '405 Method Not Allowed (POST)'
        else:
            result['error'] = f'POST returned {response.status_code}'
            
    except requests.exceptions.Timeout:
        result['error'] = 'POST Timeout'
    except Exception as e:
        result['error'] = f'POST Error: {type(e).__name__}'
    
    # Try GET if POST failed
    if not result['pdf_found']:
        try:
            url = f"{mirror.rstrip('/')}/{doi}"
            response = session.get(url, verify=False, timeout=15)
            
            if response.status_code == 200:
                result['get_works'] = True
                
                # Try to extract PDF URL
                html = etree.HTML(response.content)
                pdf_xpath = '//*[@id="pdf"]/@src|//*[@id="article"]//iframe/@src'
                results = html.xpath(pdf_xpath)
                
                if results:
                    pdf_url = results[0]
                    # Normalize URL
                    if not pdf_url.startswith('http'):
                        pdf_url = 'https:' + pdf_url if pdf_url.startswith('//') else f"https:{pdf_url}"
                    
                    # Download PDF
                    pdf_response = session.get(pdf_url, verify=False, timeout=15)
                    if pdf_response.content[:4] == b'%PDF':
                        result['pdf_found'] = True
                        result['pdf_size'] = len(pdf_response.content)
                        if not result['error']:
                            result['error'] = 'POST failed, GET worked'
            else:
                if not result['error']:
                    result['error'] = f'GET returned {response.status_code}'
                    
        except requests.exceptions.Timeout:
            if not result['error']:
                result['error'] = 'GET Timeout'
        except Exception as e:
            if not result['error']:
                result['error'] = f'GET Error: {type(e).__name__}'
    
    return result

def main():
    print("="*70)
    print("SCI-HUB MIRROR COMPARISON TEST")
    print("="*70)
    print(f"\nTesting {len(MIRRORS_TO_TEST)} mirrors with {len(TEST_DOIS)} DOIs\n")
    
    # Store results by mirror
    mirror_stats = {mirror: {'success': 0, 'total': 0, 'errors': []} for mirror in MIRRORS_TO_TEST}
    
    for doi_idx, doi in enumerate(TEST_DOIS, 1):
        print(f"\n{'='*70}")
        print(f"DOI {doi_idx}/{len(TEST_DOIS)}: {doi}")
        print(f"{'='*70}")
        
        for mirror in MIRRORS_TO_TEST:
            result = test_mirror_with_doi(mirror, doi)
            mirror_stats[mirror]['total'] += 1
            
            if result['pdf_found']:
                mirror_stats[mirror]['success'] += 1
                print(f"  [OK] {mirror:25s} - SUCCESS ({result['pdf_size']:,} bytes)")
                if result['error']:
                    print(f"    Note: {result['error']}")
            else:
                mirror_stats[mirror]['errors'].append(result['error'])
                print(f"  [FAIL] {mirror:25s} - FAILED: {result['error']}")
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY - MIRROR RELIABILITY")
    print("="*70)
    
    sorted_mirrors = sorted(mirror_stats.items(), 
                           key=lambda x: x[1]['success'], 
                           reverse=True)
    
    for mirror, stats in sorted_mirrors:
        success_rate = (stats['success'] / stats['total'] * 100) if stats['total'] > 0 else 0
        status = "[RELIABLE]" if success_rate >= 66 else "[UNRELIABLE]" if success_rate > 0 else "[DEAD]"
        
        print(f"\n{mirror}")
        print(f"  Status: {status}")
        print(f"  Success: {stats['success']}/{stats['total']} ({success_rate:.0f}%)")
        if stats['errors']:
            unique_errors = list(set(stats['errors']))
            print(f"  Errors: {', '.join(unique_errors)}")
    
    # Recommendation
    print("\n" + "="*70)
    print("RECOMMENDATION")
    print("="*70)
    
    reliable_mirrors = [m for m, s in sorted_mirrors if s['success'] >= 2]
    if reliable_mirrors:
        print("\nUse these mirrors in order:")
        for i, mirror in enumerate(reliable_mirrors, 1):
            success_rate = mirror_stats[mirror]['success'] / mirror_stats[mirror]['total'] * 100
            print(f"  {i}. {mirror} ({success_rate:.0f}% success)")
    else:
        print("\n[WARNING] No reliable mirrors found!")

if __name__ == "__main__":
    main()

