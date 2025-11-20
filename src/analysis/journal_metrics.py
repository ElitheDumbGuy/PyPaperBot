import pandas as pd
from rapidfuzz import process, fuzz
import html

class JournalRanker:
    """
    A class to load Scimago journal ranks and provide fuzzy matching to find
    journal metrics like H-Index and SJR score.
    """
    def __init__(self, csv_path='data/scimagojr 2024.csv'):
        """
        Initializes the JournalRanker by loading and processing the journal data.

        Args:
            csv_path (str): The path to the scimagojr CSV file.
        """
        try:
            self.df = pd.read_csv(csv_path, sep=';')
            # Clean up column names
            self.df.columns = [col.strip() for col in self.df.columns]
            # Ensure 'Title' is string type for matching
            self.df['Title'] = self.df['Title'].astype(str)
            # Create a list of choices for fuzzy matching
            self.journal_titles = self.df['Title'].tolist()
            
            # Create a fast lookup dictionary for exact matches (lowercased)
            self.title_lookup = {title.lower(): i for i, title in enumerate(self.journal_titles)}
            
        except FileNotFoundError:
            print(f"Error: The journal ranking file was not found at {csv_path}")
            self.df = None
            self.journal_titles = []
        except Exception as e:
            print(f"An error occurred while loading the journal ranking data: {e}")
            self.df = None
            self.journal_titles = []

    def get_metrics(self, journal_title: str, score_cutoff=90) -> dict | None:
        """
        Finds the best match for a journal title and returns its metrics.
        """
        if self.df is None or not journal_title:
            return None

        # Pre-process the input string to handle HTML entities
        cleaned_title = html.unescape(journal_title).strip()
        
        # 1. FAST PATH: Exact match (case-insensitive)
        if cleaned_title.lower() in self.title_lookup:
            index = self.title_lookup[cleaned_title.lower()]
            journal_data = self.df.iloc[index]
            return {
                'SJR': journal_data.get('SJR'),
                'H index': journal_data.get('H index'),
                'SJR Best Quartile': journal_data.get('SJR Best Quartile')
            }

        # 2. SLOW PATH: Fuzzy matching
        best_match = process.extractOne(cleaned_title, self.journal_titles, scorer=fuzz.token_sort_ratio, score_cutoff=score_cutoff)

        if not best_match:
            return None

        # Retrieve the full row from the DataFrame for the best match
        matched_title, score, index = best_match
        journal_data = self.df.iloc[index]

        metrics = {
            'SJR': journal_data.get('SJR'),
            'H index': journal_data.get('H index'),
            'SJR Best Quartile': journal_data.get('SJR Best Quartile')
        }
        return metrics
