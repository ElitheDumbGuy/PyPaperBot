# PyPaperBot Citation Network Expansion - Usage Guide

## Overview

PyPaperBot now includes powerful citation network analysis capabilities that allow you to:
- Start with a small set of seed papers from a Google Scholar query
- Automatically discover papers that cite your seeds (forward citations)
- Automatically discover papers cited by your seeds (backward references)
- Filter the expanded network by journal quality (H-Index, SJR Quartile)
- Filter by co-citation frequency (papers cited by multiple seeds)
- Download only the most relevant, high-quality papers

This transforms PyPaperBot from a simple downloader into an intelligent literature review assistant.

---

## Quick Start

```bash
python -m PyPaperBot --query="machine learning" \
                     --scholar-pages=1 \
                     --dwn-dir="./output" \
                     --expand-network
```

This will:
1. Search Google Scholar for "machine learning" (first page, ~10 papers)
2. Query OpenCitations API to find all papers citing or cited by those 10 seeds
3. Enrich all papers with journal metrics from the Scimago database
4. Present an interactive menu with filtering options
5. Download the papers you select

---

## Command-Line Arguments

### New Arguments for Citation Network Analysis

| Argument | Description | Required |
|----------|-------------|----------|
| `--expand-network` | Enable citation network expansion mode | Yes (for this feature) |

### Existing Arguments (Still Apply)

All existing PyPaperBot arguments work in combination with `--expand-network`:
- `--query`: Your search term
- `--scholar-pages`: Number of Google Scholar pages to scrape for seed papers
- `--scholar-results`: Number of results per page (max 10)
- `--doi` or `--doi-file`: Start with specific DOIs instead of a query
- `--dwn-dir`: Output directory (required)
- `--restrict`: 0 for bibtex only, 1 for PDFs only
- `--scihub-mirror`: Preferred Sci-Hub mirror
- `--headless` / `--no-headless`: Browser visibility

---

## Interactive Filtering Menu

After the network is built and enriched, you'll see:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
               Citation Network Filter Options
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Found 132 total papers in the citation network.
Select a filtering mode to determine which papers to download:

  [1] High Quality (Strict)
      └─ Co-cited by >= 3 seed papers | Journal H-Index >= 100
      └─ | SJR Quartile in ['Q1'] | Cited by >= 20 papers
      Result: 15 papers

  [2] Medium Quality (Balanced)
      └─ Co-cited by >= 2 seed papers | Journal H-Index >= 50 |
      └─ SJR Quartile in ['Q1', 'Q2'] | Cited by >= 10 papers
      Result: 42 papers

  [3] Broad Scope (Inclusive)
      └─ Co-cited by >= 1 seed papers | Journal H-Index >= 20 |
      └─ SJR Quartile in ['Q1', 'Q2', 'Q3'] | Cited by >= 5
      └─ papers
      Result: 78 papers

  [4] All (No filtering)
      Result: 132 papers

Enter choice [1/2/3/4]:
```

### Filter Mode Explanations

**[1] High Quality (Strict)**
- Best for: Comprehensive literature reviews where only the most impactful papers are needed
- Criteria: Papers must be cited by at least 3 of your seed papers, published in top-tier journals (H-Index ≥100, Q1 quartile), and have significant citations (≥20)
- Trade-off: Smallest set, highest confidence

**[2] Medium Quality (Balanced)** ⭐ *Recommended for most users*
- Best for: Standard academic research projects
- Criteria: Papers cited by 2+ seeds, good journals (H-Index ≥50, Q1-Q2), moderate citations (≥10)
- Trade-off: Good balance of quality and coverage

**[3] Broad Scope (Inclusive)**
- Best for: Exploratory research, discovering emerging topics
- Criteria: Papers cited by 1+ seeds, decent journals (H-Index ≥20, Q1-Q3), some citations (≥5)
- Trade-off: Larger set, may include less-established work

**[4] All (No filtering)**
- Best for: Maximum coverage, manual filtering later
- Downloads everything discovered in the network
- Use with caution for large networks (100+ papers)

---

## Understanding Co-Citation Count

**Co-citation count** is the number of your seed papers that cite a given paper. This is the most powerful signal for relevance:

- **Co-cited by 3+ seeds**: Very likely to be a foundational paper in your topic
- **Co-cited by 2 seeds**: Probably relevant, worth investigating
- **Co-cited by 1 seed**: Could be relevant or could be tangential
- **Co-cited by 0**: Paper cites your seeds (forward citation), not cited by them

Papers with high co-citation counts are **essential reading** for understanding your research area.

---

## Example Workflows

### Workflow 1: Start with a Broad Query

```bash
python -m PyPaperBot --query="BERT language model" \
                     --scholar-pages=1 \
                     --scholar-results=5 \
                     --dwn-dir="./bert_review" \
                     --expand-network
```

**Expected result:** 5 seed papers → ~50-200 papers in network → Select Medium Quality → Download ~30 papers

---

### Workflow 2: Start with Specific DOIs

```bash
# Create a file with DOIs (one per line)
echo "10.18653/v1/n19-1423" > dois.txt
echo "10.1162/tacl_a_00298" >> dois.txt

python -m PyPaperBot --doi-file="dois.txt" \
                     --dwn-dir="./my_papers" \
                     --expand-network
```

**Use case:** You already have a few key papers; expand from there.

---

### Workflow 3: Bibtex Only (No PDFs)

```bash
python -m PyPaperBot --query="quantum computing" \
                     --scholar-pages=1 \
                     --dwn-dir="./quantum" \
                     --expand-network \
                     --restrict=0
```

**Use case:** You just want the citation metadata and bibtex, not the actual papers.

---

## Output Files

After running with `--expand-network`, your output directory will contain:

```
./output/
├── result.csv                      # Main CSV with all paper metadata
├── bibtex.bib                      # Bibtex entries for all papers
├── project_state.json              # Project state (for resume functionality)
├── opencitations_cache.json        # Cached API responses
├── paper1.pdf                      # Downloaded PDFs
├── paper2.pdf
└── ...
```

### Enhanced CSV Columns

The `result.csv` now includes citation analysis columns:

| Column | Description |
|--------|-------------|
| Name | Paper title |
| DOI | Digital Object Identifier |
| Journal | Journal name |
| Year | Publication year |
| Authors | Author list |
| **Citation Count** | Number of papers citing this paper (from OpenCitations) |
| **Reference Count** | Number of papers this paper cites |
| **Journal H-Index** | Journal impact metric from Scimago |
| **SJR Score** | SCImago Journal Rank score |
| **SJR Quartile** | Q1 (best) through Q4 |
| Downloaded | Whether PDF was downloaded |
| Downloaded from | Source (Sci-Hub, Google Scholar, etc.) |

---

## Data Sources

### OpenCitations
- **What it is:** Open database of scholarly citation data
- **Coverage:** 2+ billion citations from Crossref, PubMed, DataCite, and more
- **API:** Free, no authentication required
- **Limitations:** Not all papers are indexed; newer papers may have incomplete data
- **URL:** https://opencitations.net

### Scimago Journal & Country Rank
- **What it is:** Database of journal quality metrics
- **Data file:** `data/scimagojr 2024.csv` (included in PyPaperBot)
- **Metrics:** H-Index, SJR score, Quartile rankings
- **Coverage:** 31,000+ journals
- **URL:** https://www.scimagojr.com

---

## Troubleshooting

### "Network could not be expanded" Message

**Symptom:** Network stays at the same size as seed papers (no expansion)

**Possible causes:**
1. **Niche topic:** OpenCitations may not have data for your specific research area
2. **Very new papers:** Recently published papers (< 1 year) may not be indexed yet
3. **API issue:** Temporary problem with OpenCitations service
4. **DOI format:** Check that your seed papers have valid DOIs

**Solutions:**
- Try a more mainstream topic to test (e.g., "machine learning", "CRISPR")
- Use older seed papers (published 2-3+ years ago)
- Check OpenCitations status at https://opencitations.net
- Review the OpenCitations cache file to see what the API returned

### All Filter Results Show "0 papers"

**Cause:** Expanded papers don't meet the quality/co-citation thresholds

**Solutions:**
- Select option [4] "All (No filtering)" to download everything
- Use a broader query to get more seed papers
- Lower the scholar-results to get fewer, more focused seeds

### JSON Serialization Error

**Symptom:** Error about `int64` not being JSON serializable

**Status:** This was a known bug that has been fixed in the current version. Update to the latest code.

---

## Performance Notes

- **Network expansion:** ~5-10 seconds per seed paper (depends on OpenCitations API)
- **Journal enrichment:** ~0.1 seconds per paper (local CSV lookup)
- **Typical runtime:** 2-5 minutes for 10 seeds expanding to 100 papers
- **API caching:** Subsequent runs reuse cached data (much faster)

---

## Future Enhancements (Not Yet Implemented)

- Resume functionality: Continue a previous session
- Depth control: Expand 2+ degrees (citations of citations)
- Custom filter thresholds: Define your own criteria
- Graph visualization: Export citation network to Gephi/Cytoscape
- Temporal analysis: Track citation trends over time

---

## Support

- **Telegram:** https://t.me/pypaperbotdatawizards
- **Issues:** Report bugs or request features on GitHub
- **Donate:** https://www.paypal.com/paypalme/ferru97

---

**Happy researching! 📚🔬**

