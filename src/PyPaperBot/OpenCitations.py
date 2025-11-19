import requests
import re
import os
import json
import time

class OpenCitationsClient:
    """
    A client for the OpenCitations Index API v2, with file-based caching.
    """
    BASE_URL = "https://api.opencitations.net/index/v2/"

    def __init__(self, cache_path='opencitations_cache.json', api_token=None):
        """
        Initializes the client, loads the cache, and sets up the API token.

        Args:
            cache_path (str): Path to the JSON file for caching API responses.
            api_token (str, optional): Your OpenCitations access token.
        """
        self.api_token = api_token
        self.headers = {"authorization": api_token} if api_token else {}
        self.cache_path = cache_path
        self.cache = self._load_cache()

    def _load_cache(self):
        """Loads the API response cache from a JSON file."""
        if os.path.exists(self.cache_path):
            try:
                with open(self.cache_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def _save_cache(self):
        """Saves the in-memory cache to a JSON file."""
        try:
            with open(self.cache_path, 'w') as f:
                json.dump(self.cache, f, indent=4)
        except IOError:
            print(f"Warning: Could not save OpenCitations cache to {self.cache_path}")

    def _get_from_api(self, endpoint: str, doi: str):
        """
        Internal method to fetch data from the API or cache.
        The cache key is a combination of the endpoint and the DOI.
        """
        cache_key = f"{endpoint}/{doi}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        full_url = f"{self.BASE_URL}{endpoint}/doi:{doi}"
        try:
            response = requests.get(full_url, headers=self.headers, timeout=10)
            response.raise_for_status()  # Raises HTTPError for bad responses (4xx or 5xx)
            
            data = response.json()
            self.cache[cache_key] = data
            self._save_cache()
            return data

        except requests.exceptions.HTTPError as e:
            # For 404 Not Found, cache an empty list to avoid re-querying
            if e.response.status_code == 404:
                self.cache[cache_key] = []
                self._save_cache()
            # For other errors, we don't cache so it can be retried later
            return []
        except (requests.exceptions.RequestException, json.JSONDecodeError):
            # For network errors or bad JSON, don't cache and return empty
            return []

    @staticmethod
    def _extract_doi_from_pid_string(pid_string: str) -> str | None:
        """
        Extracts a DOI from the complex PID string provided by the API.
        Example: "omid:br/06101801781 doi:10.7717/peerj-cs.421 pmid:33817056" -> "10.7717/peerj-cs.421"
        """
        if not isinstance(pid_string, str):
            return None
        match = re.search(r'doi:([^\s]+)', pid_string)
        return match.group(1).lower() if match else None

    def get_references(self, doi: str) -> list[str]:
        """
        Gets all DOIs of papers referenced by the given DOI.

        Args:
            doi (str): The DOI of the citing paper.

        Returns:
            list[str]: A list of cited DOIs.
        """
        api_data = self._get_from_api("references", doi)
        dois = [self._extract_doi_from_pid_string(item.get('cited', '')) for item in api_data]
        return [d for d in dois if d]

    def get_citations(self, doi: str) -> list[str]:
        """
        Gets all DOIs of papers that cite the given DOI.

        Args:
            doi (str): The DOI of the cited paper.

        Returns:
            list[str]: A list of citing DOIs.
        """
        api_data = self._get_from_api("citations", doi)
        dois = [self._extract_doi_from_pid_string(item.get('citing', '')) for item in api_data]
        return [d for d in dois if d]
