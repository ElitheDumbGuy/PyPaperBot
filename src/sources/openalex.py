import logging
import requests
from typing import List
from models.paper import Paper
from sources.base import BaseSource

class OpenAlexSource(BaseSource):
    BASE_URL = "https://api.openalex.org/works"
    
    def __init__(self, email="mail@example.com"):
        self.email = email

    def search(self, query: str, limit: int) -> List[Paper]:
        logging.info(f"Searching OpenAlex for '{query}'...")
        params = {
            'search': query,
            'per-page': limit,
            'mailto': self.email
        }
        try:
            resp = requests.get(self.BASE_URL, params=params, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                results = data.get('results', [])
                papers = []
                for item in results:
                    p = self._convert_to_paper(item)
                    if p:
                        papers.append(p)
                logging.info(f"OpenAlex returned {len(papers)} papers.")
                return papers
            else:
                logging.error(f"OpenAlex API error: {resp.status_code}")
                return []
        except Exception as e:
            logging.error(f"OpenAlex connection failed: {e}")
            return []

    def get_doi_from_title(self, title):
        """Helper to find DOI for a title."""
        if not title: return None
        params = {'filter': f'title.search:{title}', 'per-page': 1, 'mailto': self.email}
        try:
            resp = requests.get(self.BASE_URL, params=params, timeout=5)
            if resp.status_code == 200:
                results = resp.json().get('results', [])
                if results:
                    item = results[0]
                    doi = item.get('doi')
                    if doi:
                        return doi.replace('https://doi.org/', '')
        except:
            pass
        return None

    def _convert_to_paper(self, item):
        title = item.get('title')
        if not title: return None
        
        doi = item.get('doi')
        if doi:
            doi = doi.replace('https://doi.org/', '')
            
        year = item.get('publication_year')
        
        authors = []
        for ship in item.get('authorships', []):
            author_obj = ship.get('author', {})
            if author_obj and 'display_name' in author_obj:
                authors.append(author_obj['display_name'])
        author_str = ", ".join(authors)
        
        journal = None
        primary_loc = item.get('primary_location')
        if primary_loc:
            source = primary_loc.get('source')
            if source:
                journal = source.get('display_name')
        
        pdf_link = None
        best_oa = item.get('best_oa_location')
        if best_oa:
            pdf_link = best_oa.get('pdf_url')
        
        p = Paper(title=title, year=year, authors=author_str, DOI=doi, jurnal=journal, link_pdf=pdf_link)
        p.citation_count = item.get('cited_by_count', 0)
        p.openalex_id = item.get('id')
        p.sources.add('openalex')
        return p

