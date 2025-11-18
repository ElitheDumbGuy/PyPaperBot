from .Paper import Paper
from .JournalRanking import JournalRanker
from .OpenCitations import OpenCitationsClient
from .Crossref import getPapersInfoFromDOIs

class CitationProcessor:
    """
    Orchestrates the process of building and enriching a citation network.
    """
    def __init__(self, journal_csv_path='data/scimagojr 2024.csv', cache_path='opencitations_cache.json'):
        """
        Initializes the processor with clients for journal ranking and citation data.
        """
        self.journal_ranker = JournalRanker(csv_path=journal_csv_path)
        self.citations_client = OpenCitationsClient(cache_path=cache_path)
        self.network = {} # Using a dictionary to store Paper objects, keyed by DOI

    def _get_or_create_paper(self, doi):
        """Gets a paper from the network or creates a new placeholder if it doesn't exist."""
        doi = doi.lower()
        if doi not in self.network:
            paper = Paper()
            paper.DOI = doi
            self.network[doi] = paper
        return self.network[doi]

    def build_network(self, seed_papers: list[Paper]):
        """
        Takes a list of seed papers and builds the full 1-degree citation network.
        
        Args:
            seed_papers (list[Paper]): A list of Paper objects from the initial search.

        Returns:
            dict: The enriched citation network (dictionary of Paper objects).
        """
        print("Starting citation network expansion...")
        # 1. Add seed papers to the network
        for paper in seed_papers:
            if paper.DOI:
                doi = paper.DOI.lower()
                self.network[doi] = paper
                paper.is_seed = True # Add a flag to identify seed papers

        # 2. Expand the network by fetching references and citations for seed papers
        papers_to_query = list(self.network.values()) # Start with seed papers
        total_seeds = len(papers_to_query)
        seed_num = 1
        
        for paper in papers_to_query:
            print(f"  [{seed_num}/{total_seeds}] Fetching citations for: {paper.DOI}")
            seed_num += 1
            references = self.citations_client.get_references(paper.DOI)
            citations = self.citations_client.get_citations(paper.DOI)
            
            paper.references = references
            paper.citations = citations
            paper.api_queried = True # Mark as queried

            # Add new papers to the network as placeholders
            for ref_doi in references:
                self._get_or_create_paper(ref_doi)
            for cit_doi in citations:
                self._get_or_create_paper(cit_doi)
        
        # Check if any new papers were actually found
        if len(self.network) <= len(seed_papers):
            print("\nWarning: OpenCitations API did not return any citation or reference data for the seed papers.")
            print("         This could be a temporary API issue or a lack of data for this specific topic.")
            print("         Skipping filtering and download of expanded network.")
            return {} # Return an empty network to signal the calling function to stop
            
        print(f"Network expanded to {len(self.network)} total papers.")
        
        # 3. Fetch metadata for papers without titles (from OpenCitations)
        papers_needing_metadata = [p for p in self.network.values() if p.DOI and not p.title]
        if papers_needing_metadata:
            print(f"Fetching metadata from Crossref for {len(papers_needing_metadata)} papers...")
            for i, paper in enumerate(papers_needing_metadata):
                try:
                    crossref_paper = getPapersInfoFromDOIs(paper.DOI, restrict=1)
                    if crossref_paper and crossref_paper.title:
                        paper.title = crossref_paper.title
                        paper.jurnal = crossref_paper.jurnal
                        paper.bibtex = crossref_paper.bibtex
                except Exception:
                    # If Crossref fails, continue without metadata
                    pass
                
                if (i + 1) % 50 == 0 or (i + 1) == len(papers_needing_metadata):
                    print(f"  Fetched {i + 1}/{len(papers_needing_metadata)} metadata records...")
        
        # 4. Enrich all papers with journal and citation metrics
        print("Enriching papers with journal and citation metrics...")
        all_papers = list(self.network.values())
        for i, paper in enumerate(all_papers):
            # Enrich with Journal Metrics
            if paper.jurnal:
                metrics = self.journal_ranker.get_metrics(paper.jurnal)
                if metrics:
                    paper.journal_metrics = metrics
            
            # Enrich with citation counts (if not already queried)
            if paper.DOI and not getattr(paper, 'api_queried', False):
                paper.references = self.citations_client.get_references(paper.DOI)
                paper.citations = self.citations_client.get_citations(paper.DOI)
                paper.api_queried = True # Mark as queried
            elif not paper.DOI:
                paper.references = []
                paper.citations = []

            paper.citation_count = len(paper.citations) if paper.citations else 0
            paper.reference_count = len(paper.references) if paper.references else 0

            # 5. Calculate co-citation count for non-seed papers
            if not getattr(paper, 'is_seed', False):
                co_citation_count = 0
                for seed_paper in papers_to_query:
                    if paper.DOI in seed_paper.references:
                        co_citation_count += 1
                paper.co_citation_count = co_citation_count
            else:
                paper.co_citation_count = 0 # Seed papers don't have a co-citation count
            
            if (i + 1) % 20 == 0:
                print(f"  Enriched {i + 1}/{len(all_papers)} papers...")

        print("Enrichment complete.")
        return self.network
