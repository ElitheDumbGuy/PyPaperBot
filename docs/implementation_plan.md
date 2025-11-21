# Academic Archiver: The "Aggregator" Architecture Implementation Plan

This document outlines the transformation of Academic Archiver from a Google Scholar scraper into a multi-source academic search and analysis engine.

## 1. Core Philosophy
*   **Aggregator First:** We query multiple high-quality APIs (OpenAlex, Semantic Scholar, ArXiv, PubMed) to get the best metadata coverage.
*   **Evidence-Based Ranking:** We rank papers not just by keyword match, but by a Composite Score derived from Journal Prestige (SJR), Author Authority (H-Index), Citation Impact (Norm Citations), and Consensus (Cross-Source Validation).
*   **Field-Specific Presets:** We adapt our search strategy (Sources + Recency Decay) based on the academic discipline.

---

## 2. New Architecture Components

### 2.1. Data Models (`src/models/`)
*   **`Paper` (Updated):**
    *   `sources`: Set of strings (e.g., `{'openalex', 'arxiv'}`).
    *   `composite_score`: Float (0-100).
    *   `citation_count_norm`: Float (Citations per year).
    *   `journal_metrics`: Dict (`{'SJR': 3.5, 'H_index': 150, 'quartile': 'Q1'}`).
    *   `author_h_index_avg`: Float (Average H-Index of key authors).
    *   `evidence_level`: String (`'meta-analysis'`, `'review'`, `'study'`).

### 2.2. The Aggregator (`src/core/aggregator.py`)
*   **`Aggregator` Class:** Orchestrates parallel queries to all configured sources.
*   **`BaseSource` Interface:**
    *   `GoogleScholarSource`: Scrapes titles/snippets.
    *   `OpenAlexSource`: Uses `https://api.openalex.org/works` (Best for Metadata/DOI).
    *   `SemanticScholarSource`: Uses `https://api.semanticscholar.org/graph/v1/paper/search` (Best for CS/Citations).
    *   `ArxivSource`: Uses `http://export.arxiv.org/api/query` (Best for Preprints/Physics/Math).
    *   `PubMedSource`: Uses `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi` (Best for Medicine).
    *   `CoreSource` (Optional): Uses `https://api.core.ac.uk/v3/search/works` (UK Open Access).

### 2.3. The Ranking Engine (`src/analysis/ranking.py`)
*   **`RankingEngine` Class:**
    *   `calculate_composite_score(paper, preset)`: The master formula.
    *   `_get_recency_multiplier(year, preset)`: Calculates decay.
    *   `_classify_evidence(title, abstract)`: Heuristic tagging (Meta-Analysis vs Study).

### 2.4. Presets Configuration (`config/presets.json`)
```json
{
  "medicine": {
    "sources": ["pubmed", "openalex", "scholar"],
    "recency_decay": "slow", // Medical knowledge lasts longer
    "evidence_boost": {"meta-analysis": 15, "review": 10}
  },
  "cs": {
    "sources": ["arxiv", "semanticscholar", "scholar"],
    "recency_decay": "fast", // AI moves fast
    "evidence_boost": {"survey": 10}
  },
  "humanities": {
    "sources": ["openalex", "scholar", "core"],
    "recency_decay": "none"
  }
}
```

---

## 3. Implementation Steps

### Phase 1: The Aggregator Engine (Source Integration)
1.  **Scaffold `Aggregator`:** Implement `search_all(query, preset)` method.
2.  **Implement Sources:**
    *   **ArXiv:** Parse Atom XML response (Namespace `http://arxiv.org/schemas/atom`). Map `arxiv:primary_category` to fields.
    *   **Semantic Scholar:** Use Graph API `v1/paper/search`. Fetch `influentialCitationCount` and `s2FieldsOfStudy`.
    *   **PubMed:** Use E-Utilities (`esearch` -> `esummary`). Parse XML DocSums.
    *   **OpenAlex:** Optimize query filters (e.g., `is_oa=true`).
3.  **Deduplication:** Refine the Merge logic.
    *   *Rule:* If `DOI` matches -> Merge.
    *   *Rule:* If `Title` (normalized) matches AND `Year` is within +/- 1 -> Merge.

### Phase 2: The Ranking Engine (Scoring Logic)
1.  **Journal Metrics:**
    *   Load `data/scimagojr 2024.csv` into a fast lookup dict.
    *   Implement fuzzy matching for Journal Names (e.g., "Nature Medicine" vs "Nat. Med.").
2.  **Author Metrics:**
    *   Query OpenAlex `authors` endpoint for the top author's H-Index.
3.  **Recency Curves:**
    *   Implement "Fast" (Sigmoid), "Medium" (Linear Clamped), and "Slow" (Flat) decay functions.
4.  **Composite Formula:**
    ```python
    score = (
        (norm_citations * 0.30) +
        (journal_score * 0.30) +  # (SJR_norm * 0.7 + Journal_H_norm * 0.3)
        (author_h_index * 0.15) +
        (consensus_bonus * 0.10) + # +10 if in 3+ sources
        (recency_multiplier * 0.15)
    )
    ```

### Phase 3: Network & Analysis
1.  **PageRank:**
    *   Build `networkx` DiGraph from the merged papers.
    *   Run `nx.pagerank(G)` and add `centrality` to the Composite Score (Optional 2nd Pass).

### Phase 4: CLI & UX
1.  **Update CLI:**
    *   `--preset [general|medicine|cs|humanities]`
    *   `--sources [list]` (Override presets).
2.  **Interactive Filter:**
    *   Display "Composite Score" instead of just "Citation Count".
    *   Allow filtering by Evidence Level ("Show only Meta-Analyses").

### Phase 5: Output & Archival
1.  **Metadata:** Save `results.json` (Schema-compliant metadata).
2.  **Downloads:**
    *   Priority: Open Access Link -> Scholar PDF Link -> Sci-Hub (Fallback).

---

## 4. API Specific Notes (From Documentation)

*   **ArXiv:** Respect the "3 second delay" rule mentioned in their docs if making multiple paging requests. Use `start` and `max_results`.
*   **Semantic Scholar:** Use `fields=title,year,authors,venue,externalIds,citationCount,influentialCitationCount,openAccessPdf` to minimize payload. Batch requests if possible.
*   **PubMed:** Requires `esearch.fcgi` to get IDs, then `esummary.fcgi` or `efetch.fcgi` to get details. `esummary` version 2.0 is preferred for XML parsing.
*   **OpenAlex:** Use the `mailto` parameter to get faster/polite pool access.

---

## 5. Timeline
1.  **Aggregator Setup** (Sources: ArXiv, Semantic, OpenAlex).
2.  **PubMed Integration** (XML Parsing).
3.  **Ranking Engine & Presets**.
4.  **CLI Integration & Testing**.

