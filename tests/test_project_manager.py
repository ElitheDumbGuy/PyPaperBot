import unittest
import os
import shutil
import json
import numpy as np
from core.project_manager import ProjectManager
from models.paper import Paper

class TestProjectManager(unittest.TestCase):
    TEST_DIR = "test_project_output"

    def setUp(self):
        os.makedirs(self.TEST_DIR, exist_ok=True)
        self.manager = ProjectManager(self.TEST_DIR)

    def tearDown(self):
        if os.path.exists(self.TEST_DIR):
            shutil.rmtree(self.TEST_DIR)

    def test_initialization_new_project(self):
        """Test initializing a new project folder."""
        self.assertTrue(os.path.exists(self.TEST_DIR))
        self.assertFalse(self.manager.is_existing_project())
        self.assertEqual(self.manager.state['version'], "1.0")

    def test_save_and_load_state(self):
        """Test saving state and reloading it."""
        # Create some dummy data
        paper = Paper(title="Test Paper", DOI="10.1000/test")
        paper.journal_metrics = {"H index": np.int64(100)} # Test numpy serialization
        network = {"10.1000/test": paper}
        cache = {"10.1000/test": {"citations": []}}

        self.manager.save_state(network, cache)
        
        # Verify file exists
        self.assertTrue(os.path.exists(self.manager.state_file))

        # Reload
        new_manager = ProjectManager(self.TEST_DIR)
        self.assertTrue(new_manager.is_existing_project())
        
        loaded_network = new_manager.get_network(Paper)
        self.assertIn("10.1000/test", loaded_network)
        self.assertEqual(loaded_network["10.1000/test"].title, "Test Paper")
        
        # Check if numpy int was converted to int (JSON doesn't support int64)
        h_index = loaded_network["10.1000/test"].journal_metrics["H index"]
        self.assertIsInstance(h_index, int) 
        self.assertEqual(h_index, 100)

    def test_state_updates(self):
        """Test updating existing state."""
        # Save initial
        self.manager.save_state(network={"p1": Paper(title="P1")})
        
        # Update
        new_manager = ProjectManager(self.TEST_DIR)
        new_manager.save_state(network={"p2": Paper(title="P2")})
        
        # Verify overwrite (save_state overwrites network key)
        final_manager = ProjectManager(self.TEST_DIR)
        net = final_manager.get_network(Paper)
        self.assertIn("p2", net)
        self.assertNotIn("p1", net)

    def test_handling_corrupted_state_file(self):
        """Test resilience against bad JSON."""
        with open(self.manager.state_file, 'w') as f:
            f.write("{ invalid json ")
            
        new_manager = ProjectManager(self.TEST_DIR)
        # Should not crash, should start fresh
        self.assertFalse(new_manager.is_existing_project())
        self.assertEqual(new_manager.state['version'], "1.0")

if __name__ == '__main__':
    unittest.main()
