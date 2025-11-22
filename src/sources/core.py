import logging
import requests
import time
from typing import List
from models.paper import Paper
from sources.base import BaseSource

class CoreSource(BaseSource):
    """
    Source implementation for CORE API (https://api.core.ac.uk/).
    """
    BASE_URL = "https://api.core.ac.uk/v3/search/works"
    
    def __init__(self, api_key=None):
        # CORE recommends an API key, but has limited free access without one?
        # Documentation suggests public access might be limited.
        # We'll leave API key as optional for now but it's highly recommended.
        self.api_key = api_key

    def search(self, query: str, limit: int) -> List[Paper]:
        logging.info(f"Searching CORE for '{query}'...")
        
        # Using POST search for better query handling
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
            
        payload = {
            "q": query,
            "limit": limit,
            "offset": 0
        }
        
        try:
            # According to documentation, unauthenticated access is allowed but rate limited.
            # However, if it fails with 500/403, we should handle it.
            resp = requests.post(self.BASE_URL, json=payload, headers=headers, timeout=15)
            
            if resp.status_code == 200:
                data = resp.json()
                results = data.get('results', [])
                papers = []
                for item in results:
                    p = self._convert_to_paper(item)
                    if p:
                        papers.append(p)
                logging.info(f"CORE returned {len(papers)} papers.")
                return papers
            elif resp.status_code == 429:
                logging.warning("CORE Rate Limit Hit.")
                return []
            elif resp.status_code == 500:
                # Specific handling for the 500 error we saw
                # It might be due to the query format or temporary server issue
                logging.warning(f"CORE API Server Error (500). Query might be malformed or server busy.")
                return []
            else:
                logging.error(f"CORE API error: {resp.status_code} - {resp.text[:100]}")
                return []
        except Exception as e:
            logging.error(f"CORE connection failed: {e}")
            return []

    def _convert_to_paper(self, item):
        title = item.get('title')
        if not title: return None
        
        year = item.get('yearPublished')
        
        authors = []
        for author in item.get('authors', []):
            if isinstance(author, str):
                authors.append(author)
            elif isinstance(author, dict):
                name = author.get('name')
                if name: authors.append(name)
        author_str = ", ".join(authors)
        
        # CORE often provides OAI identifiers, DOI might be in identifiers list
        doi = item.get('doi')
        if not doi and 'identifiers' in item:
            for ident in item['identifiers']:
                if ident and ident.startswith('doi:'):
                    doi = ident.replace('doi:', '')
                    break
                    
        # Links
        pdf_link = item.get('downloadUrl')
        
        # Publisher/Journal
        journal = None
        if item.get('publisher'):
            journal = item.get('publisher')
        elif item.get('journals') and len(item['journals']) > 0:
             journal = item['journals'][0]

        p = Paper(title=title, year=year, authors=author_str, DOI=doi, jurnal=journal, link_pdf=pdf_link)
        
        # CORE specific fields?
        p.core_id = item.get('id')
        p.sources.add('core')
        return p

