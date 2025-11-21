import pandas as pd
import os
import json
import math
import requests
import logging
import time
import concurrent.futures
from datetime import datetime
from analysis.journal_metrics import JournalRanker

class RankingEngine:
    def __init__(self, presets_path='config/presets.json'):
        self.journal_loader = JournalRanker(csv_path='data/scimagojr 2024.csv')
        self.presets = self._load_presets(presets_path)
        self.current_year = datetime.now().year
        self.author_cache = {} # Cache author H-indices to save API calls

    def _load_presets(self, path):
        if os.path.exists(path):
            with open(path, 'r') as f:
                return json.load(f)
        return {}

    def process_papers(self, papers, preset_name='general'):
        """
        Process a list of papers: prefetch author metrics in parallel, then calculate scores.
        """
        # 1. Identify authors to fetch
        authors_to_fetch = set()
        for p in papers:
            if not p.authors: continue
            first_author = p.authors.split(',')[0].strip()
            if first_author and first_author not in self.author_cache:
                authors_to_fetch.add(first_author)
        
        # 2. Prefetch in parallel
        if authors_to_fetch:
            print(f"Fetching metrics for {len(authors_to_fetch)} authors...")
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                future_to_author = {executor.submit(self._fetch_author_h_index, author): author for author in authors_to_fetch}
                
                completed = 0
                total = len(authors_to_fetch)
                
                for future in concurrent.futures.as_completed(future_to_author):
                    author = future_to_author[future]
                    try:
                        h_index = future.result()
                        self.author_cache[author] = h_index
                    except Exception as e:
                        logging.warning(f"Error fetching author {author}: {e}")
                        self.author_cache[author] = 0
                    
                    completed += 1
                    if completed % 5 == 0:
                        print(f"  Progress: {completed}/{total} authors processed...", end='\r')
            print(f"  Done.                               ")

        # 3. Calculate scores
        for p in papers:
            self.calculate_score(p, preset_name)

    def calculate_score(self, paper, preset_name='general'):
        config = self.presets.get(preset_name, self.presets.get('general'))
        weights = config.get('weights', {})
        
        # 1. Journal Score (0-100)
        journal_score = self._calculate_journal_score(paper)
        
        # 2. Norm Citations Score (0-100)
        norm_citation_score = self._calculate_norm_citation_score(paper)
        
        # 3. Recency Score (0-100)
        recency_score = self._calculate_recency_score(paper, config.get('recency_decay', 'medium'))
        
        # 4. Consensus Score (0-100)
        consensus_score = self._calculate_consensus_score(paper)
        
        # 5. Author Authority (0-100)
        # We fetch this dynamically from OpenAlex
        author_score = self._calculate_author_score(paper)
        
        # Calculate Weighted Sum
        raw_score = (
            (norm_citation_score * weights.get('norm_citations', 0.3)) +
            (journal_score * weights.get('journal_score', 0.3)) +
            (recency_score * weights.get('recency', 0.1)) +
            (consensus_score * weights.get('consensus', 0.1)) +
            (author_score * weights.get('author_authority', 0.2))
        )
        
        # Apply Evidence Boost (Medicine specific)
        evidence_boost_map = config.get('evidence_boost', {})
        if evidence_boost_map:
            title_lower = paper.title.lower()
            for key, boost in evidence_boost_map.items():
                if key in title_lower:
                    raw_score += boost
                    break
        
        # Cap at 100
        paper.composite_score = min(100.0, raw_score)
        
        # Store metrics on paper for transparency
        paper.citation_count_norm = self._get_citations_per_year(paper)
        
        return paper.composite_score

    def _calculate_journal_score(self, paper):
        if not paper.jurnal:
            return 0
            
        metrics = self.journal_loader.get_metrics(paper.jurnal)
        if not metrics:
            return 0
            
        paper.journal_metrics = metrics
        
        sjr = metrics.get('SJR', 0.0)
        h_index = metrics.get('H_index', 0)
        
        sjr_norm = min(100, (sjr / 5.0) * 100)
        h_norm = min(100, (h_index / 200.0) * 100)
        
        return (sjr_norm * 0.7) + (h_norm * 0.3)

    def _get_citations_per_year(self, paper):
        if not paper.year:
            return 0
        try:
            age = max(1, self.current_year - int(paper.year))
            return paper.citation_count / age
        except:
            return 0

    def _calculate_norm_citation_score(self, paper):
        cpy = self._get_citations_per_year(paper)
        if cpy <= 0: return 0
        score = 25 * math.log(cpy + 1)
        return min(100, score)

    def _calculate_recency_score(self, paper, decay_type):
        if not paper.year:
            return 0
        try:
            age = max(0, self.current_year - int(paper.year))
        except:
            return 0
            
        if decay_type == 'none':
            return 100
        elif decay_type == 'slow':
            return max(0, 100 - (age * 5))
        elif decay_type == 'medium':
            return max(0, 100 - (age * 10))
        elif decay_type == 'fast':
            return 100 * math.exp(-0.5 * age)
        return 50

    def _calculate_consensus_score(self, paper):
        count = len(paper.sources)
        if count <= 1: return 0
        if count == 2: return 50
        if count >= 3: return 100
        return 0

    def _calculate_author_score(self, paper):
        """
        Fetches H-Index for the first author from OpenAlex.
        Score 0-100 (H=50 is 100 points).
        """
        if not paper.authors:
            return 0
            
        # Extract first author name (simple string split as fallback)
        first_author = paper.authors.split(',')[0].strip()
        if not first_author:
            return 0
            
        if first_author in self.author_cache:
            h_index = self.author_cache[first_author]
        else:
            # This fallback shouldn't be hit often if process_papers is used
            h_index = self._fetch_author_h_index(first_author)
            self.author_cache[first_author] = h_index
            
        # Normalize: H-Index 50 is considered "Star" level in many fields
        return min(100, (h_index / 50.0) * 100)

    def _fetch_author_h_index(self, author_name):
        """Query OpenAlex for author metrics."""
        url = "https://api.openalex.org/authors"
        params = {
            'search': author_name,
            'per-page': 1
        }
        try:
            # Respect rate limits (naive check)
            # time.sleep(0.1) # Removed sleep for parallel execution
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                results = response.json().get('results', [])
                if results:
                    # Get the most relevant author match
                    stats = results[0].get('summary_stats', {})
                    return stats.get('h_index', 0)
        except Exception as e:
            logging.warning(f"Failed to fetch author metrics for {author_name}: {e}")
        
        return 0
