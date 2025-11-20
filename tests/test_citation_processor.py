# -*- coding: utf-8 -*-
"""
Created on Mon Jun  8 21:43:30 2020

@author: Vito
"""
from unittest import TestCase
from unittest.mock import Mock, patch

from analysis.citation_network import CitationProcessor
from models.paper import Paper

class TestCitationProcessor(TestCase):
    
    def setUp(self):
        # Mock the OpenAlex Client
        self.mock_client = Mock()
        
        # Mock the Journal Ranker
        self.mock_ranker = Mock()
        self.mock_ranker.get_metrics.return_value = {
            'SJR': 1.23, 'H index': 50, 'SJR Best Quartile': 'Q1'
        }
        
        self.processor = CitationProcessor(journal_csv_path='dummy.csv')
        self.processor.openalex_client = self.mock_client
        self.processor.journal_ranker = self.mock_ranker
        
        # Create seed paper
        self.seed = Paper(title="Seed Paper", DOI="10.1000/seed")
    
    def test_network_structure_and_size(self):
        """
        Test that network builds correctly with 1 seed, 2 refs, 1 citation.
        Structure:
            Seed -> Ref1 (referenced_ids_counter)
            Seed -> Ref2 (referenced_ids_counter)
            Cit1 -> Seed (citations)
        """
        # Setup Mock Returns
        # get_citations_and_references returns: (referenced_ids_counter, citations, seed_ids)
        self.mock_client.get_citations_and_references.return_value = (
            {'W111': 1, 'W222': 1}, # Referenced works (OpenAlex IDs) with count 1
            {'10.1000/cit1'},       # Citing works (DOIs)
            {'W000'}                # Seed ID
        )
        
        # Mock get_works_by_ids (for references)
        self.mock_client.get_works_by_ids.return_value = [
            {'id': 'https://openalex.org/W111', 'doi': 'https://doi.org/10.1000/ref1', 'title': 'Ref One'},
            {'id': 'https://openalex.org/W222', 'doi': 'https://doi.org/10.1000/ref2', 'title': 'Ref Two'}
        ]
        
        # Mock get_works_by_dois (for citations)
        self.mock_client.get_works_by_dois.return_value = [
             {'id': 'https://openalex.org/W333', 'doi': 'https://doi.org/10.1000/cit1', 'title': 'Cit One', 'cited_by_count': 5}
        ]
        
        # Run build_network
        network = self.processor.build_network([self.seed])
        
        # Assertions
        # Total network size: 1 (Seed) + 2 (Refs) + 1 (Cit) = 4
        self.assertEqual(len(network), 4)
        
        # Verify Seed is in network
        self.assertIn('10.1000/seed', network)
        self.assertTrue(network['10.1000/seed'].is_seed)
        
        # Verify References are in network
        self.assertIn('10.1000/ref1', network)
        self.assertIn('10.1000/ref2', network)
        
        # Verify Citations are in network
        self.assertIn('10.1000/cit1', network)
        
    def test_cocitation_calculation(self):
        """Test that co-citation count is correctly populated from OpenAlex data."""
        # 2 seeds cite the SAME reference W111
        seed1 = Paper(title="S1", DOI="10.1000/s1")
        seed2 = Paper(title="S2", DOI="10.1000/s2")
        
        self.mock_client.get_citations_and_references.return_value = (
            {'W111': 2}, # W111 cited by 2 seeds
            set(),
            {'W001', 'W002'}
        )
        
        self.mock_client.get_works_by_ids.return_value = [
             {'id': 'https://openalex.org/W111', 'doi': 'https://doi.org/10.1000/popular', 'title': 'Popular Ref'}
        ]
        self.mock_client.get_works_by_dois.return_value = []
        
        network = self.processor.build_network([seed1, seed2])
        
        # Check that the referenced paper has co-citation count of 2
        ref_paper = network['10.1000/popular']
        self.assertEqual(ref_paper.co_citation_count, 2)
        
    def test_paper_enrichment(self):
        """Test that papers are enriched with metadata and journal metrics."""
        self.mock_client.get_citations_and_references.return_value = ({}, {'10.1000/cit1'}, set())
        self.mock_client.get_works_by_ids.return_value = []
        
        self.mock_client.get_works_by_dois.return_value = [
             {
                 'id': 'https://openalex.org/W333', 
                 'doi': 'https://doi.org/10.1000/cit1', 
                 'title': 'Cit One',
                 'publication_year': 2023,
                 'primary_location': {'source': {'display_name': 'Nature'}},
                 'cited_by_count': 42,
                 'best_oa_location': {'pdf_url': 'http://pdf.com/1.pdf'}
             }
        ]
        
        network = self.processor.build_network([self.seed])
        
        cit_paper = network['10.1000/cit1']
        
        # Check Metadata
        self.assertEqual(cit_paper.title, 'Cit One')
        self.assertEqual(cit_paper.year, 2023)
        self.assertEqual(cit_paper.jurnal, 'Nature')
        self.assertEqual(cit_paper.citation_count, 42)
        self.assertEqual(cit_paper.pdf_link, 'http://pdf.com/1.pdf')
        self.assertEqual(cit_paper.download_source, 'OpenAlex/Unpaywall')
        
        # Check Journal Metrics (from mock_ranker)
        self.assertIsNotNone(cit_paper.journal_metrics)
        self.assertEqual(cit_paper.journal_metrics['SJR'], 1.23)
