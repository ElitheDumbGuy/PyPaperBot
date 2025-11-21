import logging
import requests
import time
from typing import List
from models.paper import Paper
from sources.base import BaseSource

class SemanticScholarSource(BaseSource):
    BASE_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
    
    def search(self, query: str, limit: int) -> List[Paper]:
        logging.info(f"Searching Semantic Scholar for '{query}'...")
        params = {
            'query': query,
            'limit': limit,
            'fields': 'title,year,authors,venue,externalIds,citationCount,influentialCitationCount,openAccessPdf'
        }
        try:
            resp = requests.get(self.BASE_URL, params=params, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                results = data.get('data', [])
                papers = []
                if results:
                    for item in results:
                        p = self._convert_to_paper(item)
                        if p:
                            papers.append(p)
                logging.info(f"Semantic Scholar returned {len(papers)} papers.")
                return papers
            elif resp.status_code == 429:
                logging.warning("Semantic Scholar Rate Limit Hit. Waiting 2 seconds...")
                time.sleep(2)
                try:
                    resp = requests.get(self.BASE_URL, params=params, timeout=15)
                    if resp.status_code == 200:
                         data = resp.json()
                         results = data.get('data', [])
                         papers = []
                         if results:
                             for item in results:
                                 p = self._convert_to_paper(item)
                                 if p:
                                     papers.append(p)
                         logging.info(f"Semantic Scholar returned {len(papers)} papers (after retry).")
                         return papers
                except:
                    pass
                return []
            else:
                logging.error(f"Semantic Scholar API error: {resp.status_code}")
                return []
        except Exception as e:
            logging.error(f"Semantic Scholar connection failed: {e}")
            return []

    def _convert_to_paper(self, item):
        title = item.get('title')
        if not title: return None
        year = item.get('year')
        authors = [a.get('name') for a in item.get('authors', [])]
        author_str = ", ".join(authors)
        journal = item.get('venue')
        ext_ids = item.get('externalIds', {})
        doi = ext_ids.get('DOI') if ext_ids else None
        pdf_info = item.get('openAccessPdf')
        pdf_link = pdf_info.get('url') if pdf_info else None

        p = Paper(title=title, year=year, authors=author_str, DOI=doi, jurnal=journal, link_pdf=pdf_link)
        p.citation_count = item.get('citationCount', 0)
        p.influential_citation_count = item.get('influentialCitationCount', 0)
        p.semantic_scholar_id = item.get('paperId')
        p.sources.add('semantic_scholar')
        return p

