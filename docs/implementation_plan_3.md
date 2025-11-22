# Implementation Plan 2.0: Reliability, Consistency & UX Overhaul

This document outlines the corrective roadmap for Academic Archiver v2.0. The primary goals are to fix data integrity issues (missing DOIs/metrics), unify inconsistent logic (journal ranking), and robustify the download/reporting pipeline.

---

## Phase 1: Architecture & Consistency Fixes (Immediate Priority)

### 1.1. Unify Journal Metrics Logic
**Problem:** We currently have `JournalMetricLoader` (using `difflib`) in `src/analysis/ranking.py` and `JournalRanker` (using `rapidfuzz`) in `src/analysis/journal_metrics.py`. This causes inconsistent scoring and wasted memory.
**Task:**
*   [ ] Delete `JournalMetricLoader` from `ranking.py`.
*   [ ] Update `RankingEngine` to use `JournalRanker`.
*   [ ] Ensure `JournalRanker` correctly parses the European number format in the CSV (`145,004` -> `145.004`).

### 1.2. Connect Interactive Filtering
**Problem:** The `FilterEngine` exists but is never called in the CLI. Users search, and then *everything* is downloaded.
**Task:**
*   [ ] In `src/core/cli.py`, inject the `FilterEngine.get_filtered_list()` step after Ranking/Network Expansion and before Downloading.
*   [ ] Allow users to skip filtering with a `--no-interactive` flag.

### 1.3. Google Scholar as "Best Effort"
**Problem:** If Google Scholar detects a bot/CAPTCHA, it can crash the `Aggregator` or hang the process.
**Task:**
*   [ ] Wrap `GoogleScholarSource.search` in a robust try/except block that returns an empty list on failure, logging a warning instead of crashing.
*   [ ] Add a `--skip-scholar` flag to completely bypass it if the user knows they are blocked.

---

## Phase 2: Data Enrichment & Integrity

### 2.1. Batch Author Metrics (Fix "Missing H-Indices")
**Problem:** `ranking.py` fetches Author H-Indices one by one (`_fetch_author_h_index`). This hits rate limits immediately for search results >10 papers.
**Task:**
*   [ ] Refactor `RankingEngine` to collect all unique first authors from the paper list.
*   [ ] Implement `OpenAlexClient.get_authors_batch(names)` to fetch metrics in chunks (OpenAlex supports `filter=display_name:A|B|C`).
*   [ ] Map results back to papers in one pass.

### 2.2. "DOI Rescue" Optimization
**Problem:** Papers from Scholar often lack DOIs. The current rescue is serial and slow.
**Task:**
*   [ ] Implement parallel or batched "Title -> DOI" lookup.
*   [ ] Use a progress bar (`tqdm`) for this step so the user knows the app hasn't frozen.
*   [ ] Fallback: If OpenAlex fails to find a DOI, try Crossref API (optional, low priority).

### 2.3. Scimago CSV Parsing
**Problem:** The parser might be misinterpreting the CSV format.
**Task:**
*   [ ] Create a unit test `tests/test_journal_parsing.py` that loads `data/scimagojr 2024.csv` and asserts that "Nature" has a high SJR and H-Index.
*   [ ] Verify the decimal separator handling (`,` vs `.`).

---

## Phase 3: Network Analysis & Centrality

### 3.1. Fix Zero Centrality
**Problem:** Centrality is 0 for all papers unless `--expand-network` is run. Even when run, it might not update the original objects.
**Task:**
*   [ ] If `--expand-network` is NOT run, hide the "Centrality" column in the final report (it's misleading).
*   [ ] If it IS run, ensure the `network_map` results (which contain centrality) properly replace the original `papers_list` in the CLI flow.

### 3.2. Graph Persistence
**Problem:** If the app crashes during expansion, all graph data is lost.
**Task:**
*   [ ] Integrate `ProjectManager` to save the `network` state to `project_state.json` after expansion.
*   [ ] Add a `--resume` flag to load the network from disk instead of starting over.

---

## Phase 4: Download & Reporting Reliability

### 4.1. Download Status Tracking
**Problem:** "Downloaded" column often shows False even if successful?
**Task:**
*   [ ] Audit `downloader.py`. Ensure that when `save_file` succeeds, `paper.downloaded` is set to `True` **on the exact object instance** that is later passed to `generateReport`.
*   [ ] Verify that `scihub_mode='auto'` correctly falls back to Selenium if HTTP fails.

### 4.2. Intermediate Saving
**Problem:** If the download loop crashes on paper #99 of 100, we lose the report for the first 99.
**Task:**
*   [ ] Call `Paper.generateReport` *incrementally* (e.g., every 10 papers) or catch exceptions in the download loop to ensure the final report is always generated for whatever was processed.

---

## Testing Strategy

### Stage 1: Unit Tests (Fast)
1.  **Journal Parsing:** Verify correct SJR floats.
2.  **Filter Engine:** Verify logic filters correctly.
3.  **Paper Model:** Verify `canBeDownloaded()` logic.

### Stage 2: Integration Tests (Live APIs)
1.  **OpenAlex Batching:** Test fetching 10 authors at once.
2.  **Scholar Fallback:** Disconnect internet/block Scholar and ensure app continues with other sources.
3.  **DOI Rescue:** Feed a list of titles (no DOIs) and verify DOIs are found.

### Stage 3: End-to-End Smoke Test
Run:
```bash
python src/core/cli.py --query "machine learning fairness" --limit 5 --preset cs --expand-network
```
*   Expect: ~5-10 papers.
*   Expect: DOIs found.
*   Expect: SJR populated.
*   Expect: Downloads attempted.
*   Expect: CSV report generated.

