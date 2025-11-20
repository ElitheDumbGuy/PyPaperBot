# AcademicArchiver

**AcademicArchiver** (formerly PyPaperBot) is a modernized, modular Python tool for downloading scientific papers and bibliographic data. It leverages **Google Scholar**, **Crossref**, **OpenAlex**, and **Sci-Hub** to provide a robust paper retrieval pipeline.

The tool is designed for researchers who need to build citation networks, analyze journal impact, and retrieve full-text PDFs efficiently.

---

## ✨ Key Features

- **📚 Multi-Source Retrieval**: intelligent fallback strategy (Google Scholar -> OpenAlex -> Sci-Hub).
- **🕸️ Citation Network Expansion**: Build citation graphs by discovering papers that cite or are cited by your seed papers.
- **🧠 Smart Filtering**: Filter papers by **Co-citation Count**, **Journal H-Index** (SJR), and **Citation Count**.
- **📊 Journal Impact Metrics**: Automatically links papers to Scimago Journal Rank (SJR) data for quality assessment.
- **🚀 Asynchronous Architecture**: optimized for speed and reliability.
- **🛡️ Resilience**: Handles rate limits, Cloudflare challenges, and proxies automatically.

---

## 🚀 Quick Start

### Windows
```bat
archiver.bat --query="machine learning" --scholar-pages=1 --dwn-dir="./output"
```

### Linux/macOS
```bash
chmod +x archiver.sh
./archiver.sh --query="machine learning" --scholar-pages=1 --dwn-dir="./output"
```

### Network Expansion Mode (New!)
To build a citation network from a seed query and filter by quality:

```bash
./archiver.sh --expand-network --query="attention is all you need" --dwn-dir="./network_output"
```
*This will find the paper, discover its references/citations, enrich them with metadata, and let you interactively filter the results before downloading.*

---

## 📖 Usage

### Basic Command Line Arguments

| Argument | Description |
|----------|-------------|
| `--query "..."` | Search query for Google Scholar. |
| `--doi "..."` | Download a specific DOI. |
| `--expand-network` | **(Flag)** Enable citation network building and interactive filtering. |
| `--dwn-dir "./path"` | **(Required)** Directory to save PDFs and metadata. |
| `--scholar-pages N` | Number of Scholar pages to scrape (e.g. `1` or `1-5`). |
| `--min-year 2020` | Filter by minimum publication year. |
| `--scihub-mirror "..."`| Manually specify a Sci-Hub mirror URL. |
| `--proxy "..."` | Use a proxy server. |

### Examples

**1. Download recent AI papers:**
```bash
python -m core.cli --query="generative ai" --min-year=2023 --scholar-pages=2 --dwn-dir="./ai_papers"
```

**2. Download a specific paper by DOI:**
```bash
python -m core.cli --doi="10.1038/nature14539" --dwn-dir="./single_paper"
```

---

## 🛠️ Project Structure

The codebase uses a modular `src` layout:

- **`src/core/`**: Main application logic (`cli.py`, `filtering.py`, `project_manager.py`).
- **`src/extractors/`**: Modules for fetching data (`scholar.py`, `scihub.py`, `downloader.py`).
- **`src/analysis/`**: Tools for network analysis (`citation_network.py`, `openalex.py`, `journal_metrics.py`).
- **`src/models/`**: Data structures (`paper.py`).
- **`src/utils/`**: Helper functions and configuration.

---

## 📦 Installation (Dev)

1. Clone the repository.
2. Create a virtual environment: `python -m venv venv`
3. Install dependencies: `pip install -r requirements.txt`
4. Run: `python -m core.cli ...`

---

## ⚠️ Disclaimer

This tool is for **educational and research purposes only**. Please respect copyright laws and terms of service for all platforms accessed. Use responsibly.
