import os
import json
from datetime import datetime

class ProjectManager:
    """
    Handles saving and loading the state of a citation analysis project
    to enable resume functionality.
    """
    STATE_FILENAME = 'project_state.json'

    def __init__(self, project_path):
        """
        Initializes the manager for a specific project directory.

        Args:
            project_path (str): The directory where project files are stored.
        """
        self.project_path = project_path
        self.state_file = os.path.join(project_path, self.STATE_FILENAME)
        self.state = self._load_state()

    def _get_default_state(self):
        """Returns a new, empty state dictionary."""
        return {
            "version": "1.0",
            "created": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "seed_papers": [],
            "network": {}, # Will store serialized Paper objects
            "opencitations_cache": {}
        }

    def _load_state(self):
        """Loads the project state from the JSON file."""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                print("Warning: Could not read project state file. Starting fresh.")
                return self._get_default_state()
        return self._get_default_state()

    def save_state(self, network=None, cache=None):
        """
        Saves the current project state to the JSON file.

        Args:
            network (dict, optional): The current citation network of Paper objects.
            cache (dict, optional): The current OpenCitations API cache.
        """
        self.state['last_updated'] = datetime.now().isoformat()
        
        if network:
            # Serialize the network of Paper objects into a JSON-friendly format
            self.state['network'] = {doi: self._serialize_paper(paper) for doi, paper in network.items()}
        
        if cache:
            self.state['opencitations_cache'] = cache
            
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=4)
        except IOError:
            print(f"Error: Could not save project state to {self.state_file}")
    
    def _serialize_paper(self, paper):
        """Convert a Paper object to a JSON-serializable dict, handling numpy types."""
        paper_dict = {}
        for key, value in paper.__dict__.items():
            # Convert numpy int64/float64 to native Python types
            if hasattr(value, 'item'):  # numpy scalar types have .item() method
                paper_dict[key] = value.item()
            elif isinstance(value, list):
                # Handle lists that might contain numpy types
                paper_dict[key] = [v.item() if hasattr(v, 'item') else v for v in value]
            elif isinstance(value, dict):
                # Handle dicts that might contain numpy types (like journal_metrics)
                paper_dict[key] = {k: v.item() if hasattr(v, 'item') else v for k, v in value.items()}
            else:
                paper_dict[key] = value
        return paper_dict

    def is_existing_project(self):
        """Checks if a project state file already exists."""
        return os.path.exists(self.state_file) and self.state.get('network')

    def get_network(self, paper_class):
        """
        Deserializes the network from the state file back into Paper objects.

        Args:
            paper_class: The Paper class to use for instantiation.

        Returns:
            dict: A dictionary of Paper objects, or an empty dict if none.
        """
        network_data = self.state.get('network', {})
        network = {}
        for doi, paper_data in network_data.items():
            # Create a Paper instance and populate it from the dictionary
            paper = paper_class()
            paper.__dict__.update(paper_data)
            network[doi] = paper
        return network

    def get_cache(self):
        """Returns the OpenCitations cache from the state."""
        return self.state.get('opencitations_cache', {})
