import requests
import time
import logging
from urllib.parse import quote
from collections import Counter

class OpenAlexClient:
    """
    Client for the OpenAlex API to fetch paper metadata, citations, and references.
    Uses the 'Polite Pool' by providing an email and implements batching.
    """
    BASE_URL = "https://api.openalex.org/works"
    
    def __init__(self, email="pypaperbot@example.com"):
        self.email = email
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': f'PyPaperBot/1.4.1 (mailto:{email})'
        })
        
    def get_works_by_dois(self, dois, batch_size=50):
        """
        Fetches metadata for a list of DOIs using OpenAlex batch functionality.
        
        Args:
            dois (list): List of DOI strings.
            batch_size (int): Number of DOIs to fetch in one request (max 50).
            
        Yields:
            dict: OpenAlex work objects.
        """
        # Deduplicate and clean DOIs
        clean_dois = list(set(d.strip().lower().replace('https://doi.org/', '') for d in dois if d))
        total = len(clean_dois)
        
        for i in range(0, total, batch_size):
            batch = clean_dois[i:i + batch_size]
            
            # OpenAlex expects DOIs prefixed with 'https://doi.org/' or just 'doi:' in the filter
            # The filter syntax is: filter=doi:doi1|doi2|doi3
            formatted_batch = [f"https://doi.org/{doi}" if "doi.org" not in doi else doi for doi in batch]
            doi_filter = "|".join(formatted_batch)
            
            params = {
                'filter': f'doi:{doi_filter}',
                'per-page': batch_size,
                'mailto': self.email,
                'select': 'id,doi,title,publication_year,primary_location,authorships,cited_by_count,referenced_works,best_oa_location'
            }
            
            try:
                response = self.session.get(self.BASE_URL, params=params, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    results = data.get('results', [])
                    for work in results:
                        yield work
                elif response.status_code == 429:
                    print("  [OpenAlex] Rate limit hit. Sleeping for 2 seconds...")
                    time.sleep(2)
                else:
                    print(f"  [OpenAlex] Error {response.status_code}")
                    
            except Exception as e:
                print(f"  [OpenAlex] Request failed: {e}")
            
            # Polite delay between batches
            time.sleep(0.2)

    def get_citations_and_references(self, seed_dois):
        """
        Retrieves citations (incoming) and references (outgoing) for the given seed DOIs.
        
        Args:
            seed_dois (list): List of seed paper DOIs.
            
        Returns:
            tuple: (Counter of reference_dois, set of citation_dois)
        """
        # 1. Get Seed Works to find what they Reference
        # We use batch fetch to get the seed works themselves
        seed_works = list(self.get_works_by_dois(seed_dois))
        
        references = Counter() # Track how many seeds cite a specific paper
        seed_ids = []
        
        # To resolve OpenAlex IDs to DOIs without an extra fetch, we might be stuck.
        # OpenAlex 'referenced_works' gives IDs (W123). 
        # We can't know the DOI of W123 without fetching W123.
        # STRATEGY: We collect all W-IDs, then batch fetch them using get_works_by_dois (but passing IDs instead of DOIs? No, get_works_by_dois expects DOIs).
        
        # Modified Strategy: 
        # 1. Collect all referenced W-IDs.
        # 2. Collect all Seed W-IDs.
        # 3. Incoming Citations: Query works?filter=referenced_works:SEED_ID1|SEED_ID2...
        
        # Let's collect IDs first
        referenced_ids = Counter()
        
        for work in seed_works:
            if work.get('id'):
                seed_ids.append(work['id'])
            
            for ref_url in work.get('referenced_works', []):
                ref_id = ref_url.split('/')[-1]
                referenced_ids[ref_id] += 1

        # Now we need to resolve these referenced_ids to DOIs.
        # We can use a new method `get_works_by_ids`
        
        # 2. Incoming Citations
        citations = set()
        if seed_ids:
            batch_size = 25
            for i in range(0, len(seed_ids), batch_size):
                batch_ids = seed_ids[i:i+batch_size]
                id_filter = "|".join(batch_ids)
                
                params = {
                    'filter': f'referenced_works:{id_filter}',
                    'per-page': 200, 
                    'mailto': self.email,
                    'select': 'id,doi'
                }
                
                try:
                    response = self.session.get(self.BASE_URL, params=params, timeout=30)
                    if response.status_code == 200:
                        data = response.json()
                        for work in data.get('results', []):
                            if work.get('doi'):
                                citations.add(work['doi'].replace('https://doi.org/', ''))
                except Exception:
                    pass
                    
        return referenced_ids, citations, seed_ids

    def get_works_by_ids(self, ids, batch_size=50):
        """
        Fetches metadata for a list of OpenAlex IDs.
        """
        # Unique IDs only for fetching
        unique_ids = list(set(ids))
        total = len(unique_ids)
        
        for i in range(0, total, batch_size):
            batch = unique_ids[i:i + batch_size]
            id_filter = "|".join(batch)
            
            params = {
                'filter': f'openalex_id:{id_filter}',
                'per-page': batch_size,
                'mailto': self.email,
                'select': 'id,doi,title,publication_year,primary_location,authorships,cited_by_count,best_oa_location'
            }
            
            try:
                response = self.session.get(self.BASE_URL, params=params, timeout=30)
                if response.status_code == 200:
                    for work in response.json().get('results', []):
                        yield work
            except Exception:
                pass
            time.sleep(0.2)
