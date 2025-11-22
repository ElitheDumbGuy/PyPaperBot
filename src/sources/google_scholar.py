import logging
from typing import List
from models.paper import Paper
from extractors.scholar import get_scholar_papers_info
from sources.base import BaseSource

class GoogleScholarSource(BaseSource):
    def __init__(self, headless=False):
        self.headless = headless

    def search(self, query: str, limit: int) -> List[Paper]:
        logging.info(f"Searching Google Scholar for '{query}'...")
        try:
            results = get_scholar_papers_info(
                query=query,
                scholar_pages=range(1, 2),
                restrict=0,
                scholar_results=limit,
                headless=self.headless
            )
            for p in results:
                p.sources.add('google_scholar')
            logging.info(f"Google Scholar returned {len(results)} papers.")
            return results
        except Exception as e:
            logging.error(f"Google Scholar search failed: {e}")
            return []

