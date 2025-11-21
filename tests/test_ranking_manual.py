import sys
import os
import logging

# Ensure src is in path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from models.paper import Paper
from analysis.ranking import RankingEngine

def test_ranking():
    print("=== Testing Ranking Engine ===")
    
    try:
        engine = RankingEngine()
    except Exception as e:
        print(f"Failed to initialize engine: {e}")
        return

    # 1. Create Dummy Papers
    
    # Paper A: "Nature" paper, Old, High Citations
    p1 = Paper(title="Deep Learning Nature", year=2015, jurnal="Nature")
    p1.citation_count = 50000
    p1.sources = {'google_scholar', 'openalex', 'semantic_scholar'} # Consensus 3
    
    # Paper B: "Unknown" journal, New, Low Citations
    p2 = Paper(title="New Algorithm 2024", year=2024, jurnal="Journal of Unknown Things")
    p2.citation_count = 5
    p2.sources = {'arxiv'} # Consensus 1
    
    # Paper C: "Review" paper (Medical)
    p3 = Paper(title="Systematic review of COVID-19 vaccines", year=2022, jurnal="The Lancet")
    p3.citation_count = 500
    p3.sources = {'pubmed', 'openalex'}
    
    papers = [p1, p2, p3]
    
    print("\n--- General Preset ---")
    for p in papers:
        score = engine.calculate_score(p, preset_name='general')
        print(f"\nTitle: {p.title}")
        print(f"  Composite Score: {score:.2f}")
        print(f"  Norm Citations: {p.citation_count_norm:.2f}")
        print(f"  Journal Metrics: {p.journal_metrics}")
    
    print("\n--- Medicine Preset (Should boost Paper C) ---")
    for p in papers:
        score = engine.calculate_score(p, preset_name='medicine')
        print(f"\nTitle: {p.title}")
        print(f"  Composite Score: {score:.2f}")

if __name__ == "__main__":
    test_ranking()

