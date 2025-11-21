import logging
import requests
import xml.etree.ElementTree as ET
from typing import List
from models.paper import Paper
from sources.base import BaseSource

class PubMedSource(BaseSource):
    ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    ESUMMARY_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    
    def search(self, query: str, limit: int) -> List[Paper]:
        logging.info(f"Searching PubMed for '{query}'...")
        
        # Step 1: Search for IDs
        search_params = {
            'db': 'pubmed',
            'term': query,
            'retmax': limit,
            'retmode': 'json'
        }
        try:
            resp = requests.get(self.ESEARCH_URL, params=search_params, timeout=15)
            if resp.status_code != 200:
                logging.error(f"PubMed ESearch failed: {resp.status_code}")
                return []
            
            data = resp.json()
            id_list = data.get('esearchresult', {}).get('idlist', [])
            
            if not id_list:
                logging.info("PubMed found no matches.")
                return []
            
            # Step 2: Get Summary (Metadata) for IDs
            return self._get_summaries(id_list)
            
        except Exception as e:
            logging.error(f"PubMed search failed: {e}")
            return []

    def _get_summaries(self, id_list):
        ids_str = ",".join(id_list)
        summary_params = {
            'db': 'pubmed',
            'id': ids_str,
            'version': '2.0',
            'retmode': 'xml'
        }
        
        try:
            resp = requests.get(self.ESUMMARY_URL, params=summary_params, timeout=15)
            if resp.status_code != 200:
                return []
            
            return self._parse_xml(resp.content)
        except Exception as e:
            logging.error(f"PubMed summary fetch failed: {e}")
            return []
            
    def _parse_xml(self, xml_content) -> List[Paper]:
        papers = []
        try:
            root = ET.fromstring(xml_content)
            # ESummary 2.0 structure: <DocumentSummarySet><DocumentSummary uid="..."><Title>...</Title>...
            for doc in root.findall(".//DocumentSummary"):
                p = self._convert_doc(doc)
                if p:
                    papers.append(p)
            logging.info(f"PubMed returned {len(papers)} papers.")
        except Exception as e:
            logging.error(f"Error parsing PubMed XML: {e}")
        return papers

    def _convert_doc(self, doc):
        title = doc.findtext("Title")
        if not title: return None
        
        pub_date = doc.findtext("PubDate")
        year = pub_date[:4] if pub_date else None
        
        journal = doc.findtext("Source")
        
        # Authors (List within List)
        authors = []
        authors_elem = doc.find("Authors")
        if authors_elem is not None:
            for author in authors_elem.findall("Author"):
                name = author.findtext("Name")
                if name: authors.append(name)
        author_str = ", ".join(authors)
        
        # Extract DOI from ArticleIds (Child elements)
        # <ArticleIds><ArticleId><IdType>doi</IdType><Value>...</Value></ArticleId></ArticleIds>
        doi = None
        article_ids = doc.find("ArticleIds")
        if article_ids is not None:
            for aid in article_ids.findall("ArticleId"):
                id_type = aid.findtext("IdType")
                if id_type == "doi":
                    doi = aid.findtext("Value")
                    break
        
        # Fallback to ELocationID if needed, checking text content
        # <ELocationID EIdType="doi">10.1038/...</ELocationID>
        if not doi:
            elocations = doc.findall("ELocationID")
            for eloc in elocations:
                if eloc.get("EIdType") == "doi":
                    doi = eloc.text
                    # Some ELocationIDs include "doi: " prefix, strip it
                    if doi and doi.lower().startswith("doi:"):
                        doi = doi.split(":", 1)[1].strip()
                    break

        p = Paper(title=title, year=year, authors=author_str, DOI=doi, jurnal=journal)
        p.sources.add('pubmed')
        return p

