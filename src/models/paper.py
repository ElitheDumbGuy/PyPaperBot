# -*- coding: utf-8 -*-
"""
Paper model to store metadata and metrics.
"""
import urllib.parse
import re
import bibtexparser
import pandas as pd


class Paper:

    def __init__(self, title=None, scholar_link=None, scholar_page=None, cites=None, link_pdf=None, year=None,
                 authors=None, DOI=None, jurnal=None):
        self.title = title
        self.scholar_page = scholar_page
        self.scholar_link = scholar_link
        self.pdf_link = link_pdf
        self.year = year
        self.authors = authors
        self.jurnal = jurnal
        self.cites_num = None
        self.bibtex = None
        self.DOI = DOI
        
        # --- Sources & IDs ---
        self.sources = set()  # {'google_scholar', 'openalex', 'semantic_scholar', 'arxiv', 'core'}
        self.openalex_id = None
        self.semantic_scholar_id = None
        self.arxiv_id = None
        self.core_id = None
        
        # --- Metrics for Ranking ---
        self.citation_count = 0 # Raw citations (highest found across sources)
        self.citation_count_norm = 0.0 # Normalized per year
        self.influential_citation_count = 0 # From Semantic Scholar
        
        self.journal_metrics = None # {'H_index': int, 'SJR': float, 'Quartile': str}
        self.author_h_index = 0 # First author's H-Index
        
        self.network_centrality = 0.0 # PageRank score
        self.recency_score = 0.0 # 0.0 - 1.0 based on age
        self.consensus_score = 0.0 # Bonus for appearing in multiple sources
        
        self.composite_score = 0.0 # Final 0-100 rank
        
        # --- Network fields ---
        self.is_seed = False
        self.references = [] # List of DOIs or IDs
        self.citations = [] # List of DOIs or IDs
        self.co_citation_count = 0

        # --- Download Status ---
        self.downloaded = False
        self.downloadedFrom = 0  # 1-SciHub 2-scholar
        self.download_source = ""
        self.use_doi_as_filename = False 

    def getFileName(self):
        try:
            if self.use_doi_as_filename:
                return urllib.parse.quote(self.DOI, safe='') + ".pdf"
            else:
                # Include year in filename for better sorting
                prefix = f"({self.year}) " if self.year else ""
                safe_title = re.sub(r'[^\w\-_. ]', '_', self.title)
                return f"{prefix}{safe_title}.pdf"
        except Exception:
            return "none.pdf"

    def setBibtex(self, bibtex):
        x = bibtexparser.loads(bibtex, parser=None)
        x = x.entries
        self.bibtex = bibtex
        try:
            if "year" in x[0]:
                self.year = x[0]["year"]
            if 'author' in x[0]:
                self.authors = x[0]["author"]
            self.jurnal = x[0]["journal"].replace("\\", "") if "journal" in x[0] else None
            if self.jurnal is None:
                self.jurnal = x[0]["publisher"].replace("\\", "") if "publisher" in x[0] else None
        except Exception:
            pass

    def canBeDownloaded(self):
        return self.DOI is not None or self.scholar_link is not None or self.pdf_link is not None

    @staticmethod
    def generateReport(papers, path):
        columns = [
            "Rank Score", "Title", "Year", "Authors", "Journal", "DOI", 
            "Norm Citations", "Raw Citations", "SJR", "Journal H-Index", "Author H-Index",
            "Centrality", "Sources", 
            "Downloaded", "Download Source"
        ]

        data = []
        # Sort by composite score descending
        sorted_papers = sorted(papers, key=lambda x: x.composite_score, reverse=True)
        
        for p in sorted_papers:
            # Safe extraction of metrics
            sjr = 0.0
            j_h_index = 0
            if p.journal_metrics:
                sjr = p.journal_metrics.get('SJR', 0.0)
                j_h_index = p.journal_metrics.get('H_index', 0)
            
            # Format authors (truncate if too long)
            authors_str = str(p.authors)
            if len(authors_str) > 100:
                authors_str = authors_str[:97] + "..."

            data.append({
                "Rank Score": f"{p.composite_score:.2f}",
                "Title": p.title,
                "Year": p.year,
                "Authors": authors_str,
                "Journal": p.jurnal,
                "DOI": p.DOI,
                "Norm Citations": f"{p.citation_count_norm:.2f}",
                "Raw Citations": p.citation_count,
                "SJR": f"{sjr:.3f}",
                "Journal H-Index": j_h_index,
                "Author H-Index": p.author_h_index,
                "Centrality": f"{p.network_centrality:.4f}",
                "Sources": ", ".join(p.sources),
                "Downloaded": "Yes" if p.downloaded else "No",
                "Download Source": p.download_source
            })

        df = pd.DataFrame(data, columns=columns)
        df.to_csv(path, index=False, encoding='utf-8')

    @staticmethod
    def generateBibtex(papers, path):
        content = ""
        for p in papers:
            if p.bibtex is not None:
                content += p.bibtex + "\n"
        relace_list = ["\ast", "*", "#"]
        for c in relace_list:
            content = content.replace(c, "")
        with open(path, "w", encoding="latin-1", errors="ignore") as f:
            f.write(str(content))
