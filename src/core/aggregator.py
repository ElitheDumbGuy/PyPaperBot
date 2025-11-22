import logging
from typing import Dict
import time
from models.paper import Paper
from sources.google_scholar import GoogleScholarSource
from sources.openalex import OpenAlexSource
from sources.semanticscholar import SemanticScholarSource
from sources.arxiv import ArxivSource
from sources.pubmed import PubMedSource
from sources.core import CoreSource

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Aggregator:
    def __init__(self):
        # Initialize all sources
        self.sources = [
            GoogleScholarSource(headless=False), # Explicitly non-headless
            OpenAlexSource(),
            SemanticScholarSource(),
            ArxivSource(),
            PubMedSource(),
            CoreSource()
        ]
    
    def search_all(self, query: str, limit_per_source: int = 10) -> Dict[str, Paper]:
        """
        Queries all sources, merges results by DOI/Title, and returns a unified dict.
        """
        all_papers = {}
        
        for source in self.sources:
            try:
                papers = source.search(query, limit_per_source)
                for p in papers:
                    self._merge_paper(all_papers, p)
            except Exception as e:
                # Catch-all for any source failure to ensure graceful degradation
                logging.error(f"Source {type(source).__name__} failed unexpectedly: {e}")
                continue
                
        # After initial merge, try to rescue missing DOIs
        self._rescue_missing_dois(all_papers)
        
        return all_papers

    def _merge_paper(self, unique_papers: Dict[str, Paper], new_paper: Paper):
        """
        Smart merge: uses DOI if available, otherwise normalized title.
        Updates existing paper with new info (e.g. if OpenAlex has DOI but Scholar didn't).
        """
        # 1. Try to find by DOI
        if new_paper.DOI:
            if new_paper.DOI in unique_papers:
                existing = unique_papers[new_paper.DOI]
                self._update_existing(existing, new_paper)
                return
            
        # 2. Try to find by Title (Normalized)
        norm_title = self._normalize_title(new_paper.title)
        
        # Check if any existing paper matches this title
        title_matched_key = None
        for key, existing in unique_papers.items():
            if self._normalize_title(existing.title) == norm_title:
                title_matched_key = key
                break
        
        if title_matched_key:
            existing = unique_papers[title_matched_key]
            self._update_existing(existing, new_paper)
            
            # Critical: If the NEW paper has a DOI but the EXISTING key was a Title,
            # we should migrate the entry to the DOI key.
            if new_paper.DOI and not existing.DOI:
                existing.DOI = new_paper.DOI
                del unique_papers[title_matched_key]
                unique_papers[new_paper.DOI] = existing
            elif new_paper.DOI and existing.DOI and new_paper.DOI != existing.DOI:
                # Edge case: different DOIs for same title? Keep existing but log warning.
                pass
            elif not existing.DOI and new_paper.DOI:
                 # Existing has no DOI, new has DOI. Update existing object with DOI.
                 existing.DOI = new_paper.DOI
                 # Re-key
                 del unique_papers[title_matched_key]
                 unique_papers[new_paper.DOI] = existing
            return

        # 3. If new, add it
        key = new_paper.DOI if new_paper.DOI else norm_title
        unique_papers[key] = new_paper

    def _update_existing(self, existing: Paper, new: Paper):
        """Merges metadata from 'new' into 'existing'."""
        # Add Source
        existing.sources.update(new.sources)
        
        # Prefer DOI if missing
        if not existing.DOI and new.DOI:
            existing.DOI = new.DOI
            
        # Prefer PDF link if missing
        if not existing.pdf_link and new.pdf_link:
            existing.pdf_link = new.pdf_link
            
        # Maximize citation counts
        if new.citation_count > existing.citation_count:
            existing.citation_count = new.citation_count
            
        # Add Influential Citations (unique to Semantic Scholar)
        if new.influential_citation_count > existing.influential_citation_count:
            existing.influential_citation_count = new.influential_citation_count
            
        # Fill IDs
        if new.openalex_id: existing.openalex_id = new.openalex_id
        if new.semantic_scholar_id: existing.semantic_scholar_id = new.semantic_scholar_id
        if new.arxiv_id: existing.arxiv_id = new.arxiv_id

    def _rescue_missing_dois(self, papers_map: Dict[str, Paper]):
        """
        Iterates through papers without DOIs and tries to find them via OpenAlex title search.
        Updates the map in place (re-keying if necessary).
        """
        keys_to_update = []
        
        # Find papers needing rescue
        for key, p in papers_map.items():
            if not p.DOI and p.title:
                keys_to_update.append(key)
        
        if not keys_to_update:
            return

        logging.info(f"Attempting DOI rescue for {len(keys_to_update)} papers...")
        
        # Use OpenAlex source helper
        oa_source = None
        for s in self.sources:
            if isinstance(s, OpenAlexSource):
                oa_source = s
                break
        
        if not oa_source: return

        count = 0
        processed = 0
        total = len(keys_to_update)
        
        for key in keys_to_update:
            processed += 1
            print(f"  DOI Rescue: {processed}/{total}...", end='\r')
            
            p = papers_map[key]
            found_doi = oa_source.get_doi_from_title(p.title)
            
            if found_doi:
                p.DOI = found_doi
                # We need to re-key this entry from Title-Key to DOI-Key
                # to prevent duplicates if we run this again or merge later
                del papers_map[key]
                papers_map[found_doi] = p
                count += 1
                time.sleep(0.1) # Polite rate limit
        
        print(f"  DOI Rescue: Done. Rescued {count} DOIs.       ")
        
        if count > 0:
            logging.info(f"Rescued {count} DOIs.")

    def _normalize_title(self, title):
        if not title: return ""
        return "".join(e for e in title if e.isalnum()).lower()
