import unittest
from unittest.mock import MagicMock
from core.filtering import FilterEngine
from models.paper import Paper

class TestFilterEngine(unittest.TestCase):
    
    def setUp(self):
        self.engine = FilterEngine()
    
    def test_high_quality_filter(self):
        """Test filtering with High Quality preset."""
        config = self.engine.FILTER_PRESETS['1'] # High Quality
        
        # Match case
        paper_good = Paper(title="Good Paper")
        paper_good.co_citation_count = 5
        paper_good.journal_metrics = {"H index": 150, "SJR Best Quartile": "Q1"}
        paper_good.citation_count = 100
        
        self.assertTrue(self.engine._is_match(paper_good, config))
        
        # Fail case (low citations)
        paper_bad = Paper(title="Bad Paper")
        paper_bad.co_citation_count = 0
        paper_bad.citation_count = 0
        
        self.assertFalse(self.engine._is_match(paper_bad, config))

    def test_medium_quality_filter(self):
        """Test filtering with Medium Quality preset."""
        config = self.engine.FILTER_PRESETS['2'] # Medium Quality
        
        # Match case (Q2 journal, moderate metrics)
        paper_ok = Paper(title="OK Paper")
        paper_ok.co_citation_count = 2
        paper_ok.journal_metrics = {"H index": 60, "SJR Best Quartile": "Q2"}
        paper_ok.citation_count = 15
        
        self.assertTrue(self.engine._is_match(paper_ok, config))
        
        # Fail case (Q3 journal)
        paper_q3 = Paper(title="Q3 Paper")
        paper_q3.journal_metrics = {"H index": 60, "SJR Best Quartile": "Q3"}
        # Assuming Q3 is not allowed in Medium (usually Q1, Q2)
        self.assertFalse(self.engine._is_match(paper_q3, config))

    def test_broad_scope_filter(self):
        """Test filtering with Broad Scope preset."""
        config = self.engine.FILTER_PRESETS['3'] # Broad Scope
        
        # Match case (minimal requirements)
        paper_broad = Paper(title="Broad Paper")
        paper_broad.co_citation_count = 1
        paper_broad.journal_metrics = {"H index": 25, "SJR Best Quartile": "Q3"}
        paper_broad.citation_count = 5
        
        self.assertTrue(self.engine._is_match(paper_broad, config))

    def test_all_filter(self):
        """Test filtering with All preset."""
        config = self.engine.FILTER_PRESETS['4'] # All
        
        paper_junk = Paper(title="Junk Paper")
        paper_junk.co_citation_count = 0
        
        self.assertTrue(self.engine._is_match(paper_junk, config))

    def test_interactive_flow(self):
        """Test the interactive selection flow (mocked input)."""
        network = {
            "doi1": Paper(title="P1"),
            "doi2": Paper(title="P2")
        }
        
        # Mock input to select '4' (All)
        with unittest.mock.patch('builtins.input', return_value='4'):
            selected_papers = self.engine.get_filtered_list(network)
            self.assertEqual(len(selected_papers), 2)
            
    def test_interactive_flow_with_invalid_input(self):
         network = { "doi1": Paper(title="P1") }
         # Mock input: first 'invalid', then '4'
         with unittest.mock.patch('builtins.input', side_effect=['invalid', '4']):
             # We also need to mock print to avoid cluttering output
             with unittest.mock.patch('builtins.print'):
                 selected_papers = self.engine.get_filtered_list(network)
                 self.assertEqual(len(selected_papers), 1)

if __name__ == '__main__':
    unittest.main()
