import logging
import requests
import xml.etree.ElementTree as ET
from typing import List
from models.paper import Paper
from sources.base import BaseSource

class ArxivSource(BaseSource):
    BASE_URL = "http://export.arxiv.org/api/query"
    NS = {'atom': 'http://www.w3.org/2005/Atom', 'arxiv': 'http://arxiv.org/schemas/atom'}

    def search(self, query: str, limit: int) -> List[Paper]:
        logging.info(f"Searching ArXiv for '{query}'...")
        params = {
            'search_query': f'all:{query}',
            'start': 0,
            'max_results': limit
        }
        try:
            resp = requests.get(self.BASE_URL, params=params, timeout=15)
            if resp.status_code == 200:
                return self._parse_xml(resp.content)
            else:
                logging.error(f"ArXiv API error: {resp.status_code}")
                return []
        except Exception as e:
            logging.error(f"ArXiv connection failed: {e}")
            return []

    def _parse_xml(self, xml_content) -> List[Paper]:
        papers = []
        try:
            root = ET.fromstring(xml_content)
            for entry in root.findall('atom:entry', self.NS):
                p = self._convert_entry(entry)
                if p:
                    papers.append(p)
            logging.info(f"ArXiv returned {len(papers)} papers.")
        except Exception as e:
            logging.error(f"Error parsing ArXiv XML: {e}")
        return papers

    def _convert_entry(self, entry):
        title_elem = entry.find('atom:title', self.NS)
        title = title_elem.text.strip().replace('\n', ' ') if title_elem is not None else "Unknown Title"
        
        published_elem = entry.find('atom:published', self.NS)
        published = published_elem.text if published_elem is not None else ""
        year = published[:4] if published else None
        
        authors = []
        for author in entry.findall('atom:author', self.NS):
            name_elem = author.find('atom:name', self.NS)
            if name_elem is not None:
                authors.append(name_elem.text)
        author_str = ", ".join(authors)

        id_elem = entry.find('atom:id', self.NS)
        arxiv_id = id_elem.text.split('/')[-1] if id_elem is not None else None
        
        doi = None
        doi_elem = entry.find('arxiv:doi', self.NS)
        if doi_elem is not None:
            doi = doi_elem.text

        pdf_link = None
        for link in entry.findall('atom:link', self.NS):
            if link.get('title') == 'pdf':
                pdf_link = link.get('href')

        primary_cat = entry.find('arxiv:primary_category', self.NS)
        journal = f"ArXiv ({primary_cat.get('term')})" if primary_cat is not None else "ArXiv"

        p = Paper(title=title, year=year, authors=author_str, DOI=doi, jurnal=journal, link_pdf=pdf_link)
        p.arxiv_id = arxiv_id
        p.sources.add('arxiv')
        return p

