import textwrap
import sys

class FilterEngine:
    """
    Handles the logic for scoring papers in a network and presenting interactive
    filtering options to the user.
    """
    FILTER_PRESETS = {
        '1': {
            'name': 'High Quality (Strict)',
            'min_cocitations': 3,
            'min_h_index': 100,
            'allowed_quartiles': {'Q1'},
            'min_citations': 20,
        },
        '2': {
            'name': 'Medium Quality (Balanced)',
            'min_cocitations': 2,
            'min_h_index': 50,
            'allowed_quartiles': {'Q1', 'Q2'},
            'min_citations': 10,
        },
        '3': {
            'name': 'Broad Scope (Inclusive)',
            'min_cocitations': 1,
            'min_h_index': 20,
            'allowed_quartiles': {'Q1', 'Q2', 'Q3'},
            'min_citations': 5,
        },
        '4': {
            'name': 'All (No filtering)',
        },
    }

    def _get_h_index(self, paper):
        """Safely retrieves the H-index from a paper's journal metrics."""
        if hasattr(paper, 'journal_metrics') and paper.journal_metrics:
            return paper.journal_metrics.get('H index', 0)
        return 0

    def _get_quartile(self, paper):
        """Safely retrieves the SJR Best Quartile from a paper's journal metrics."""
        if hasattr(paper, 'journal_metrics') and paper.journal_metrics:
            return paper.journal_metrics.get('SJR Best Quartile')
        return None

    def _is_match(self, paper, config):
        """Checks if a single paper matches a given filter configuration."""
        if not config or 'name' in config and config['name'] == 'All (No filtering)':
            return True

        # Check co-citation count
        if getattr(paper, 'co_citation_count', 0) < config.get('min_cocitations', 0):
            return False
        
        # Check citation count
        if getattr(paper, 'citation_count', 0) < config.get('min_citations', 0):
            return False

        # Only apply journal-based filters if the paper has metric data
        if hasattr(paper, 'journal_metrics') and paper.journal_metrics:
            # Check H-index
            if self._get_h_index(paper) < config.get('min_h_index', 0):
                return False

            # Check SJR Quartile
            quartile = self._get_quartile(paper)
            allowed_quartiles = config.get('allowed_quartiles')
            if allowed_quartiles and quartile not in allowed_quartiles:
                return False

        return True

    def get_filtered_list(self, network: dict) -> list:
        """
        Applies presets to the network, prints an interactive menu, and returns
        the user's selected list of papers.
        
        Args:
            network (dict): The citation network of Paper objects.
        
        Returns:
            list: A list of Paper objects matching the user's selected filter.
        """
        paper_list = list(network.values())
        
        # Calculate the results for each preset
        results = {}
        for key, config in self.FILTER_PRESETS.items():
            filtered_papers = [p for p in paper_list if self._is_match(p, config)]
            results[key] = {
                'config': config,
                'papers': filtered_papers,
                'count': len(filtered_papers)
            }
        
        # --- Display Interactive Menu ---
        print("\n" + "━" * 60)
        print(" " * 15 + "Citation Network Filter Options")
        print("━" * 60)
        print(f"Found {len(paper_list)} total papers in the citation network.")

        # Add a helpful message if the network did not expand
        seed_paper_count = len([p for p in paper_list if getattr(p, 'is_seed', False)])
        if len(paper_list) == seed_paper_count:
            print("\nNote: The citation network could not be expanded for the seed papers.")
            print("This may be due to a lack of data in OpenCitations for this topic.")
            print("Filtering will be applied only to the initial seed papers.\n")
        else:
            print("Select a filtering mode to determine which papers to download:\n")

        for key, data in results.items():
            config = data['config']
            name = config.get('name', 'Unknown')
            count = data['count']
            
            print(f"  [{key}] {name}")
            details = []
            if 'min_cocitations' in config:
                details.append(f"Co-cited by >= {config['min_cocitations']} seed papers")
            if 'min_h_index' in config:
                details.append(f"Journal H-Index >= {config['min_h_index']}")
            if 'allowed_quartiles' in config:
                details.append(f"SJR Quartile in {sorted(list(config['allowed_quartiles']))}")
            if 'min_citations' in config:
                details.append(f"Cited by >= {config['min_citations']} papers")
            
            if details:
                wrapped_details = textwrap.wrap(" | ".join(details), width=54)
                for line in wrapped_details:
                    print(f"      └─ {line}")
            
            print(f"      Result: {count} papers\n")
            
        # --- Get User Input ---
        while True:
            try:
                choice = input(f"Enter choice [{'/'.join(results.keys())}]: ")
                if choice in results:
                    print(f"\nSelected '{results[choice]['config']['name']}'. Preparing {results[choice]['count']} papers for download.")
                    return results[choice]['papers']
                print("Invalid choice. Please try again.")
            except (EOFError, KeyboardInterrupt):
                # Graceful exit if input stream closes or user cancels
                print("\nInput cancelled. Defaulting to 'All (No filtering)'.")
                return results['4']['papers']
