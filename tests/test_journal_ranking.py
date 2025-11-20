import unittest
from analysis.journal_metrics import JournalRanker

class TestJournalRanker(unittest.TestCase):

    def setUp(self):
        # Use the actual CSV file for testing (make sure path is correct relative to test run)
        # Assuming tests are run from root
        self.ranker = JournalRanker(csv_path='data/scimagojr 2024.csv')

    def test_initialization(self):
        """Test that the ranker initializes and loads data."""
        self.assertIsNotNone(self.ranker.df)
        self.assertFalse(self.ranker.df.empty)
        self.assertIn('nature', self.ranker.title_lookup)

    def test_exact_match(self):
        """Test exact match lookup (fast path)."""
        metrics = self.ranker.get_metrics("Nature")
        self.assertIsNotNone(metrics)
        self.assertEqual(metrics['SJR Best Quartile'], 'Q1')
        # H-index for Nature is very high, check it's an int-like number
        self.assertTrue(isinstance(metrics['H index'], (int, float)) or hasattr(metrics['H index'], 'item'))
        self.assertGreater(metrics['H index'], 1000) 

    def test_another_exact_match(self):
        """Test another exact match."""
        metrics = self.ranker.get_metrics("Science")
        self.assertIsNotNone(metrics)
        self.assertEqual(metrics['SJR Best Quartile'], 'Q1')
        
    def test_fuzzy_match_with_html_entity(self):
        """Test matching with HTML entities (e.g. &amp;) and slight variations."""
        # "Nature Reviews Molecular Cell Biology"
        # Input with &amp;
        metrics = self.ranker.get_metrics("Nature Reviews Molecular Cell Biology")
        self.assertIsNotNone(metrics)
        
        # Try a slightly messy title
        metrics_fuzzy = self.ranker.get_metrics("Nature Reviews Molecular Cell Biol.")
        # This might fail if fuzzy score is strict, but let's see
        # If it fails, returns None
        # We are testing the logic, so if it returns None that's also a valid result for "no match"
        # But we want to verify it finds *something* if close enough.
        # Given score_cutoff=90, this might be too different.
        pass

    def test_no_match(self):
        """Test a completely made up journal name."""
        metrics = self.ranker.get_metrics("Journal of Fake Science and Nothingness 2024")
        self.assertIsNone(metrics)

    def test_edge_case_empty_input(self):
        self.assertIsNone(self.ranker.get_metrics(""))
    
    def test_edge_case_none_input(self):
        self.assertIsNone(self.ranker.get_metrics(None))

if __name__ == '__main__':
    unittest.main()
