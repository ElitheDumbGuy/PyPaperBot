import sys
import os

# Ensure src is in path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from models.paper import Paper
from analysis.citation_network import CitationProcessor
from core.filtering import FilterEngine

def run_manual_test():
    print("1. Creating seed papers (Simulating Google Scholar results)...")
    # We use titles of famous ML papers to test DOI resolution
    seeds = [
        Paper(title="Attention is all you need"),
        Paper(title="Deep Residual Learning for Image Recognition"),
        Paper(title="Adam: A Method for Stochastic Optimization"),
        Paper(title="Dropout: A Simple Way to Prevent Neural Networks from Overfitting"),
        Paper(title="Generative Adversarial Nets"),
        Paper(title="Batch Normalization: Accelerating Deep Network Training by Reducing Internal Covariate Shift"),
        Paper(title="ImageNet Classification with Deep Convolutional Neural Networks"),
        Paper(title="Very Deep Convolutional Networks for Large-Scale Image Recognition"),
        Paper(title="Mastering the game of Go with deep neural networks and tree search"),
        Paper(title="Learning to Forget: Continual Prediction with LSTM"),
        Paper(title="Neural Machine Translation by Jointly Learning to Align and Translate"),
        Paper(title="Playing Atari with Deep Reinforcement Learning"),
        Paper(title="XGBoost: A Scalable Tree Boosting System"),
        Paper(title="LightGBM: A Highly Efficient Gradient Boosting Decision Tree"),
        Paper(title="CatBoost: unbiased boosting with categorical features"),
        Paper(title="Random Forests"),
        Paper(title="Support-vector networks"),
        Paper(title="A decision-theoretic generalization of on-line learning and an application to boosting"),
        Paper(title="Long Short-Term Memory"),
        Paper(title="Gradient-based learning applied to document recognition")
    ]
    print(f"   Created {len(seeds)} seed papers.")

    print("\n2. Initializing Citation Processor...")
    processor = CitationProcessor(journal_csv_path='data/scimagojr 2024.csv')
    
    print("\n3. Building Network (This includes DOI resolution)...")
    # This triggers the new logic we added to resolve DOIs from Titles
    network = processor.build_network(seeds)
    
    print(f"\n4. Network Built. Total papers: {len(network)}")
    
    print("\n5. Applying Filters...")
    filter_engine = FilterEngine()
    
    # Calculate counts for each preset
    results = {}
    for key, config in filter_engine.FILTER_PRESETS.items():
        # We use the private _is_match method to test logic without user input
        filtered_papers = [p for p in network.values() if filter_engine._is_match(p, config)]
        print(f"   Preset: {config.get('name'):<30} | Count: {len(filtered_papers)}")

if __name__ == "__main__":
    run_manual_test()

