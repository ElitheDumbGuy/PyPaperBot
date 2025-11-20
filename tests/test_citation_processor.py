import unittest
from unittest.mock import MagicMock, patch
from collections import Counter
from analysis.citation_network import CitationProcessor
from models.paper import Paper

class TestCitationProcessor(unittest.TestCase):

    def setUp(self):
        """Set up the processor with mocked dependencies."""
        self.mock_journal_ranker = MagicMock()
        self.mock_openalex_client = MagicMock()

        # Mock Journal Metrics
        def get_metrics_side_effect(title):
            if title == "Journal A": return {"H index": 100}
            if title == "Journal B": return {"H index": 200}
            return None
        self.mock_journal_ranker.get_metrics.side_effect = get_metrics_side_effect

        # Mock OpenAlex Data
        # Return: (referenced_ids_counter, citations_set, seed_ids_map)
        self.mock_openalex_client.get_citations_and_references.return_value = (
            Counter({"W_REF_1": 1, "W_REF_2": 2}), # W_REF_2 is co-cited by 2 seeds
            {"doi_cit_1"}, # Incoming citations (list of DOIs)
            {"doi_seed_1": "W_SEED_1", "doi_seed_2": "W_SEED_2"} # seed_ids map
        )

        # Mock get_works_by_ids (for references)
        # IDs: W_REF_1, W_REF_2
        self.mock_openalex_client.get_works_by_ids.return_value = [
            {
                "id": "https://openalex.org/W_REF_1", "doi": "https://doi.org/doi_ref_1", 
                "title": "Ref 1", "cited_by_count": 10,
                "primary_location": {"source": {"display_name": "Journal C"}}
            },
            {
                "id": "https://openalex.org/W_REF_2", "doi": "https://doi.org/doi_ref_2", 
                "title": "Ref 2", "cited_by_count": 20,
                "primary_location": {"source": {"display_name": "Journal A"}}
            }
        ]

        # Mock get_works_by_dois (for citations)
        # DOIs: doi_cit_1
        self.mock_openalex_client.get_works_by_dois.return_value = [
            {
                "id": "https://openalex.org/W_CIT_1", "doi": "https://doi.org/doi_cit_1", 
                "title": "Cit 1", "cited_by_count": 5,
                "primary_location": {"source": {"display_name": "Journal B"}}
            }
        ]

        self.journal_patcher = patch('analysis.citation_network.JournalRanker', return_value=self.mock_journal_ranker)
        self.openalex_patcher = patch('analysis.citation_network.OpenAlexClient', return_value=self.mock_openalex_client)
        
        self.journal_patcher.start()
        self.openalex_patcher.start()
        
        self.processor = CitationProcessor()

    def tearDown(self):
        self.journal_patcher.stop()
        self.openalex_patcher.stop()

    def test_network_structure_and_size(self):
        """Test if the network is built with the correct papers and size."""
        seed_paper_1 = Paper(DOI="doi_seed_1", jurnal="Journal A")
        seed_paper_2 = Paper(DOI="doi_seed_2", jurnal="Journal B")
        seed_papers = [seed_paper_1, seed_paper_2]

        network = self.processor.build_network(seed_papers)

        # Expected DOIs: seed_1, seed_2 (seeds) + ref_1, ref_2 (outgoing) + cit_1 (incoming)
        expected_dois = {"doi_seed_1", "doi_seed_2", "doi_ref_1", "doi_ref_2", "doi_cit_1"}
        
        self.assertEqual(len(network), 5)
        self.assertEqual(set(network.keys()), expected_dois)
        self.assertTrue(network["doi_seed_1"].is_seed)

    def test_paper_enrichment(self):
        """Test that papers in the network are correctly enriched with data."""
        seed_paper_1 = Paper(DOI="doi_seed_1", jurnal="Journal A")
        seed_papers = [seed_paper_1]

        network = self.processor.build_network(seed_papers)

        # Test seed paper enrichment (Journal Metrics come from JournalRanker via local lookup)
        enriched_seed = network["doi_seed_1"]
        self.assertEqual(enriched_seed.journal_metrics, {"H index": 100})
        
        # Test enrichment of a discovered paper (Ref 2 matches Journal A -> H index 100)
        enriched_ref = network["doi_ref_2"]
        self.assertEqual(enriched_ref.title, "Ref 2")
        self.assertEqual(enriched_ref.citation_count, 20)
        self.assertEqual(enriched_ref.journal_metrics, {"H index": 100})
    
    def test_cocitation_calculation(self):
        """Test that co-citation counts are calculated correctly."""
        seed_paper_1 = Paper(DOI="doi_seed_1", jurnal="Journal A")
        seed_paper_2 = Paper(DOI="doi_seed_2", jurnal="Journal B")
        seed_papers = [seed_paper_1, seed_paper_2]

        network = self.processor.build_network(seed_papers)

        # doi_ref_2 is referenced by 2 seeds (mocked in Counter)
        self.assertEqual(network["doi_ref_2"].co_citation_count, 2)
        
        # doi_ref_1 is referenced by 1 seed
        self.assertEqual(network["doi_ref_1"].co_citation_count, 1)

        # doi_cit_1 is an incoming citation, defaults to 1 (if not explicitly calculated as co-citation)
        # logic: if paper.co_citation_count == 0: paper.co_citation_count = 1
        self.assertEqual(network["doi_cit_1"].co_citation_count, 1)

        # Seed papers should have a co-citation count of 0 (default)
        self.assertEqual(network["doi_seed_1"].co_citation_count, 0)

if __name__ == '__main__':
    unittest.main()
