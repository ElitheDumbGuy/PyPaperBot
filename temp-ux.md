# User Experience Walkthrough (CLI)

This document outlines the current user journey when running the Academic Archiver via the command line interface.

## 1. Startup & Initialization
**Command:** `python -m core.cli --query "machine learning" --scholar-pages 2 --dwn-dir ./downloads`

**User Sees:**
1.  **Banner:** A text banner showing "Academic Archiver".
2.  **Configuration Check:** The system loads `config.json` (Sci-Hub mirrors, timeouts).
3.  **Arguments Summary:** Displays the query (`machine learning`), output directory, and page limit.

## 2. Phase I: Seed Paper Discovery (Google Scholar)
The system launches a browser (Selenium) to scrape Google Scholar.

**User Sees:**
```text
Searching Google Scholar for 'machine learning'...
Processing page 1...
Processing page 2...
Found 14 valid papers (excluding Books/Citations).
```
*Note: The system filters out entries labeled "[BOOK]" or "[CITATION]" automatically.*

## 3. Phase II: Network Expansion (OpenAlex)
The system uses the "seed" papers to build a citation graph.

**User Sees:**
```text
Building citation network...
Resolving DOIs for seed papers...
  [1/14] Resolving DOI for "Attention is all you need"... -> Found: 10.xxx
  ...
Fetching citations and references...
  Found 544 references (outgoing).
  Found 192 citations (incoming).
Network expanded to 541 total papers.
Linking Scimago Journal Metrics...
```
*Action:* The system queries OpenAlex to find:
1.  Papers that the seeds cite (References).
2.  Papers that cite the seeds (Citations).
3.  It then matches these papers to the Scimago Journal Rank (SJR) database to get H-Indices and Quartiles (Q1-Q4).

## 4. Phase III: Interactive Filtering
The user decides which papers are "worth" downloading based on quality metrics.

**User Sees:**
```text
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
               Citation Network Filter Options
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Found 541 total papers in the citation network.
Select a filtering mode to determine which papers to download:

  [1] High Quality (Strict)
      └─ Co-cited by >= 2 seed papers | Journal H-Index >= 60 | SJR Quartile in ['Q1']
      Result: 40 papers

  [2] Medium Quality (Balanced)
      └─ Co-cited by >= 1 seed papers | Journal H-Index >= 30 | SJR Quartile in ['Q1', 'Q2']
      Result: 120 papers

  [3] Broad Scope (Inclusive)
      └─ Journal H-Index >= 10 | SJR Quartile in ['Q1', 'Q2', 'Q3']
      Result: 400 papers

  [4] All (No filtering)
      Result: 541 papers

Enter choice [1/2/3/4]:
```

## 5. Phase IV: Downloading
The system attempts to download the PDF for every paper in the selected list.

**User Sees:**
```text
Sci-Hub mirrors order: https://sci-hub.mk -> ...
The downloader will try Google Scholar first, then Sci-Hub mirrors.

Download 1 of 40 -> Attention is all you need
  Downloaded from Google Scholar (direct link)

Download 2 of 40 -> Deep Residual Learning...
  Downloaded from Sci-Hub (DOI) via https://sci-hub.mk

...
```

## 6. Output Generation
**Location:** The directory specified in `--dwn-dir` (e.g., `./downloads`).

**Files Created:**
1.  **PDF Files:** The actual papers (e.g., `(2017) Attention is all you need.pdf`).
2.  **`papers.csv`** (Implied): A metadata file containing titles, authors, DOIs, and download status for all processed papers.

