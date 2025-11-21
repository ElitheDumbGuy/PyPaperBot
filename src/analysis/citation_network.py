from models.paper import Paper
from analysis.journal_metrics import JournalRanker
from analysis.openalex import OpenAlexClient

class CitationProcessor:
    """
    Orchestrates the process of building and enriching a citation network using OpenAlex.
    """
    def __init__(self, journal_csv_path='data/scimagojr 2024.csv'):
        """
        Initializes the processor with clients for journal ranking and OpenAlex.
        """
        self.journal_ranker = JournalRanker(csv_path=journal_csv_path)
        self.openalex_client = OpenAlexClient()
        self.network = {} # Using a dictionary to store Paper objects, keyed by DOI

    def _get_or_create_paper(self, doi):
        """Gets a paper from the network or creates a new placeholder if it doesn't exist."""
        doi = doi.lower().replace('https://doi.org/', '')
        if doi not in self.network:
            paper = Paper()
            paper.DOI = doi
            self.network[doi] = paper
        return self.network[doi]

    def build_network(self, seed_papers: list[Paper]):
        """
        Takes a list of seed papers and builds the full 1-degree citation network using OpenAlex.
        """
        print("Starting citation network expansion using OpenAlex...")
        
        # Pre-process seed papers: resolve DOIs from Titles if missing
        for paper in seed_papers:
            if not paper.DOI and paper.title:
                print(f"  Resolving DOI for: {paper.title[:50]}...")
                doi = self.openalex_client.get_doi_from_title(paper.title)
                if doi:
                    paper.DOI = doi
                    print(f"    -> Found: {doi}")
                else:
                    print("    -> No match found.")

        seed_dois = [p.DOI for p in seed_papers if p.DOI]
        if not seed_dois:
            print("No valid DOIs found in seed papers. Skipping expansion.")
            return {}

        # 1. Add seed papers to the network
        for paper in seed_papers:
            if paper.DOI:
                doi = paper.DOI.lower().replace('https://doi.org/', '')
                self.network[doi] = paper
                paper.is_seed = True

        # 2. Expand Network
        print(f"Fetching citations and references for {len(seed_dois)} seed papers...")
        referenced_ids_counter, citations, seed_ids = self.openalex_client.get_citations_and_references(seed_dois)
        
        print(f"  Found {len(referenced_ids_counter)} references (outgoing).")
        print(f"  Found {len(citations)} citations (incoming).")
        
        # 3. Process References (Outgoing) - These are OpenAlex IDs
        # We need to fetch them to get their DOIs and Metadata
        ref_ids_to_fetch = list(referenced_ids_counter.keys())
        
        print(f"Fetching metadata for {len(ref_ids_to_fetch)} referenced papers...")
        count = 0
        for work in self.openalex_client.get_works_by_ids(ref_ids_to_fetch):
            if not work.get('doi'):
                continue
            
            doi = work['doi'].replace('https://doi.org/', '').lower()
            paper = self._get_or_create_paper(doi)
            
            # Set Co-citation count (how many seeds cited this paper)
            # referenced_ids_counter uses OpenAlex ID, work['id'] has the ID
            oa_id = work['id'].split('/')[-1]
            paper.co_citation_count = referenced_ids_counter.get(oa_id, 0)
            
            self._populate_paper_metadata(paper, work)
            count += 1
            if count % 50 == 0:
                print(f"  Processed {count}/{len(ref_ids_to_fetch)} references...")

        # 4. Process Citations (Incoming) - These are DOIs
        print(f"Fetching metadata for {len(citations)} citing papers...")
        citations_list = list(citations)
        count = 0
        for work in self.openalex_client.get_works_by_dois(citations_list):
            if not work.get('doi'):
                continue
                
            doi = work['doi'].replace('https://doi.org/', '').lower()
            paper = self._get_or_create_paper(doi)
            
            # Incoming citations don't strictly have "co-citation" in the same way,
            # but we can set it to 1 to indicate it's connected.
            if not getattr(paper, 'is_seed', False):
                if paper.co_citation_count == 0:
                     paper.co_citation_count = 1
            
            self._populate_paper_metadata(paper, work)
            count += 1
            if count % 50 == 0:
                 print(f"  Processed {count}/{len(citations_list)} citations...")

        print(f"Network expanded to {len(self.network)} total papers.")
        print("Linking Scimago Journal Metrics...")
        
        # 5. Link Scimago Metrics (Fast Local Lookup)
        for paper in self.network.values():
             if paper.jurnal:
                metrics = self.journal_ranker.get_metrics(paper.jurnal)
                if metrics:
                    paper.journal_metrics = metrics

        # Calculate simple centrality (normalized co-citation count)
        max_cocite = max((p.co_citation_count for p in self.network.values()), default=1)
        if max_cocite > 0:
            for p in self.network.values():
                p.network_centrality = p.co_citation_count / max_cocite

        print("Network processing complete.")
        return self.network

    def _populate_paper_metadata(self, paper, work):
        """Helper to populate paper object from OpenAlex work object."""
        paper.title = work.get('title')
        paper.year = work.get('publication_year')
        
        if work.get('authorships'):
            paper.authors = ", ".join([
                a['author']['display_name'] 
                for a in work['authorships'] 
                if a.get('author') and a['author'].get('display_name')
            ])
        
        if work.get('primary_location') and work['primary_location'].get('source'):
            paper.jurnal = work['primary_location']['source'].get('display_name')
        
        paper.citation_count = work.get('cited_by_count', 0)
        
        if work.get('best_oa_location') and work['best_oa_location'].get('pdf_url'):
            paper.pdf_link = work['best_oa_location']['pdf_url']
            paper.download_source = "OpenAlex/Unpaywall"
