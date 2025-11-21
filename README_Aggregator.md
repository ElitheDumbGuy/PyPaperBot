# Academic Archiver: The "Aggregator" Architecture

## Overview
Academic Archiver has been transformed from a simple Google Scholar scraper into a professional multi-source academic aggregator. It queries multiple high-quality APIs, merges the results, and ranks papers using a composite score based on journal prestige, author authority, and citation impact.

## Core Components

### 1. The Aggregator (`src/core/aggregator.py`)
*   **Multi-Source Search:** Queries 5 sources in parallel:
    *   **Google Scholar:** (Headless Selenium) - Best for broad search.
    *   **OpenAlex:** (API) - Best for metadata, DOIs, and Author metrics.
    *   **Semantic Scholar:** (API) - Best for CS papers and citation graphs.
    *   **ArXiv:** (API) - Best for preprints in Physics/CS/Math.
    *   **PubMed:** (E-Utilities) - Best for Medical/Life Sciences.
*   **Intelligent Deduplication:** Merges results based on DOI (primary) and Normalized Title (fallback).
*   **DOI Rescue:** Automatically resolves missing DOIs for papers found via title-only sources (like Google Scholar) by querying OpenAlex.

### 2. The Ranking Engine (`src/analysis/ranking.py`)
Calculates a **Composite Score (0-100)** for every paper to prioritize quality over quantity.

*   **Formula:**
    ```python
    Score = (w1 * NormCitations) + (w2 * JournalScore) + (w3 * Recency) + (w4 * Consensus) + (w5 * AuthorAuthority)
    ```
*   **Metrics:**
    *   **Journal Score:** Derived from **Scimago Journal Rank (SJR)** and **H-Index**. Includes fuzzy matching for journal names (e.g., matching "Eur. Spine J." to "European Spine Journal").
    *   **Norm Citations:** Citations per year (Logarithmic scale).
    *   **Author Authority:** First author's H-Index (fetched dynamically from OpenAlex).
    *   **Recency:** Decay function based on field (Fast/Medium/Slow).
    *   **Consensus:** Bonus points if a paper appears in multiple sources.

### 3. Presets (`config/presets.json`)
Field-specific configurations that adjust weights and sources.
*   **`general`:** Balanced approach.
*   **`medicine`:** Prioritizes PubMed, High Journal Score, and Evidence Levels (Meta-Analyses).
*   **`cs`:** Prioritizes ArXiv, Recency, and Citation Counts.
*   **`humanities`:** Prioritizes Journal Score and Lifetime Impact (No recency decay).

## Usage

### Command Line Interface
The CLI has been completely rewritten to support the new workflow.

```bash
# Basic Search (General Preset)
python -m core.cli --query "machine learning" --dwn-dir ./output

# Computer Science Mode (Fast-moving, ArXiv heavy)
python -m core.cli --query "large language models" --preset cs --limit 20 --dwn-dir ./llm_papers

# Medicine Mode (High Evidence, PubMed heavy)
python -m core.cli --query "covid vaccine efficacy" --preset medicine --dwn-dir ./med_papers

# Expand Citation Network (PageRank Analysis)
python -m core.cli --query "transformer attention" --expand-network --dwn-dir ./network_analysis
```

### Output
*   **`papers_ranked.csv`:** Full metadata including Composite Score, SJR, Journal H-Index, Author H-Index, and Download status.
*   **`bibtex.bib`:** BibTeX entries for all found papers.
*   **PDFs:** Downloaded files (named by Title or DOI).

## Implementation Status
*   [x] Multi-source Aggregator
*   [x] DOI Rescue & Deduplication
*   [x] Ranking Engine (SJR, Author H-Index)
*   [x] Field Presets
*   [x] PubMed & ArXiv Integration
*   [x] End-to-End CLI Workflow

