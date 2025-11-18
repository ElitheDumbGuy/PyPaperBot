[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.me/ferru97)

# PyPaperBot

**PyPaperBot** is a professional Python tool for downloading scientific papers and bibliographic data using **Google Scholar**, **Crossref**, and **Sci-Hub**. The tool intelligently tries multiple sources to maximize download success rates while respecting rate limits and handling anti-bot measures gracefully.

### Join the [Telegram](https://t.me/pypaperbotdatawizards) channel to stay updated, report bugs, or request custom data mining scripts.

---

## ✨ Key Features

- 📚 **Multi-Source Downloads**: Automatically tries Google Scholar direct links, then falls back to Sci-Hub mirrors
- 🔍 **Flexible Search**: Download papers by query, DOI, DOI list, or citation tracking
- 📖 **BibTeX Generation**: Automatically generates bibliographic data for all papers
- 🎯 **Smart Filtering**: Filter by publication year, journal, or citation count
- 🚀 **Intelligent Fallback**: Hybrid HTTP/Selenium mode with automatic failover
- ✅ **PDF Validation**: Ensures downloaded files are valid PDFs, not error pages
- 🌐 **Multi-Mirror Support**: Uses multiple Sci-Hub mirrors with automatic retry on failure
- 🛡️ **Robust Error Handling**: Gracefully handles timeouts, blocks, and unavailable papers
- 📊 **Progress Tracking**: Real-time download progress with detailed source attribution
- 🔄 **Auto-Detection**: Automatically detects Chrome installation and version

## 📋 Requirements

- **Python 3.11+** (Python 3.12+ may have compatibility issues with some dependencies)
- **Google Chrome** (auto-detected on Windows, macOS, and Linux)
- **Internet connection**

## 🚀 Quick Start

### Windows
```bash
pypaperbot.bat --query="machine learning" --scholar-pages=1 --dwn-dir="./output" --restrict=1
```

### Linux/Mac
```bash
chmod +x pypaperbot.sh
./pypaperbot.sh --query="machine learning" --scholar-pages=1 --dwn-dir="./output" --restrict=1
```

**The wrapper scripts automatically:**
- ✅ Create a virtual environment if needed
- ✅ Install all dependencies
- ✅ Run PyPaperBot from source

**No manual installation required!**

---

## 📦 Manual Installation

If you prefer manual setup:

```bash
git clone <repository-url>
cd PyPaperBot
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Windows Users
If you encounter *"Microsoft Visual C++ 14.0 is required"* errors, install:
- [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
- Or [Visual Studio](https://visualstudio.microsoft.com/downloads/)

### Termux Users
```bash
pkg install wget
wget https://its-pointless.github.io/setup-pointless-repo.sh
pkg install numpy
export CFLAGS="-Wno-deprecated-declarations -Wno-unreachable-code"
pip install pandas
chmod +x pypaperbot.sh
./pypaperbot.sh --query="..." --scholar-pages=1 --dwn-dir="./output"
```

---

## 📖 Usage

### Basic Usage
```bash
python -m PyPaperBot --query="machine learning" --scholar-pages=3 --dwn-dir="./papers" --restrict=1
```

### Command-Line Arguments

| Argument | Description | Type |
|----------|-------------|------|
| `--query` | Search query or Google Scholar page link | string |
| `--doi` | Single DOI to download | string |
| `--doi-file` | Text file with list of DOIs (one per line) | string |
| `--cites` | Paper ID to download citations for (from Scholar URL) | string |
| `--scholar-pages` | Pages to download (e.g., `3` or `4-7`) | string |
| `--scholar-results` | Results per page when `--scholar-pages=1` (max 10) | int |
| `--dwn-dir` | **[Required]** Output directory for downloads | string |
| `--min-year` | Minimum publication year filter | int |
| `--max-dwn-year` | Max papers to download, sorted by year | int |
| `--max-dwn-cites` | Max papers to download, sorted by citations | int |
| `--journal-filter` | CSV file for journal filtering | string |
| `--restrict` | `0`: BibTeX only, `1`: PDFs only | int |
| `--skip-words` | Comma-separated words to exclude from titles | string |
| `--scihub-mirror` | Custom Sci-Hub mirror (auto-selected if not set) | string |
| `--scihub-mode` | `auto`, `http`, or `selenium` (default: `auto`) | string |
| `--use-doi-as-filename` | Use DOI instead of title for filenames | flag |
| `--headless` | Run Chrome in headless mode (may trigger detection) | flag |
| `--no-headless` | **[Default]** Run Chrome with visible window | flag |
| `--proxy` | List of proxies (specify at end of command) | string |
| `--single-proxy` | Single proxy (recommended over `--proxy`) | string |

### Important Notes

**Mutually Exclusive Options:**
- Only one of: `--query`, `--doi`, `--doi-file`
- Only one of: `--max-dwn-year`, `--max-dwn-cites`

**Required Arguments:**
- `--dwn-dir` is always required
- `--scholar-pages` is required when using `--query`

**File Formats:**
- `--journal-filter`: CSV with format `journal_list;include_list` (semicolon separator, 0=exclude, 1=include)
- `--doi-file`: Plain text with one DOI per line

---

## 💡 Examples

### Download papers by query with year filter
```bash
python -m PyPaperBot --query="deep learning" --scholar-pages=3 --min-year=2020 --dwn-dir="./papers"
```

### Download specific page range with word exclusions
```bash
python -m PyPaperBot --query="neural networks" --scholar-pages=4-7 --skip-words="survey,review" --dwn-dir="./papers"
```

### Download single paper by DOI
```bash
python -m PyPaperBot --doi="10.1038/s41586-021-03819-2" --dwn-dir="./papers" --use-doi-as-filename
```

### Download papers from DOI list
```bash
python -m PyPaperBot --doi-file="dois.txt" --dwn-dir="./papers"
```

### Download citations of a specific paper
```bash
python -m PyPaperBot --cites=3120460092236365926 --scholar-pages=2 --dwn-dir="./papers"
```

### Use custom Sci-Hub mirror
```bash
python -m PyPaperBot --query="quantum computing" --scholar-pages=1 --scihub-mirror="https://sci-hub.st" --dwn-dir="./papers"
```

### Use proxy for downloads
```bash
python -m PyPaperBot --query="bioinformatics" --scholar-pages=1 --single-proxy="http://proxy.example.com:8080" --dwn-dir="./papers"
```

### Run with visible Chrome window (debugging)
```bash
python -m PyPaperBot --query="robotics" --scholar-pages=1 --no-headless --dwn-dir="./papers"
```

### Force HTTP-only mode (faster, no Selenium)
```bash
python -m PyPaperBot --query="machine learning" --scholar-pages=1 --scihub-mode=http --dwn-dir="./papers"
```

---

## 🔧 Advanced Features

### Download Strategy
PyPaperBot uses an intelligent multi-stage download strategy:

1. **Google Scholar Direct Link** - Fastest, tries first
2. **Sci-Hub Primary Mirror** (https://sci-hub.mk) - Most reliable
3. **Sci-Hub Fallback Mirrors** - Automatic retry on failure
4. **Smart Error Detection** - Identifies unavailable papers immediately

### Sci-Hub Mirror Management
- **Auto-Selection**: Uses working mirrors automatically
- **Cloudflare Retry**: Automatically retries once if blocked
- **Paper Availability Detection**: Stops immediately if paper not in database
- **Early Termination**: Stops after 5 consecutive failures to prevent endless loops

### Output Files
- **`result.csv`** - Download report with sources and metadata
- **`bibtex.bib`** - BibTeX entries for all papers
- **`[paper_title].pdf`** - Individual PDF files (or DOI-based names)

---

## 🌐 Sci-Hub Access

If Sci-Hub is blocked in your country:
- Use a VPN service like [ProtonVPN](https://protonvpn.com/)
- Use the `--single-proxy` or `--proxy` option
- Try different mirrors with `--scihub-mirror`

**Current Working Mirrors:**
- https://sci-hub.mk (primary)
- https://sci-hub.vg
- https://sci-hub.al
- https://sci-hub.shop

---

## 🤝 Contributing

Contributions are welcome! Please submit pull requests to the **dev** branch.

### To-Do List
- [ ] Comprehensive test suite
- [ ] Enhanced code documentation
- [ ] Performance optimizations
- [ ] Additional paper sources

---

## ⚠️ Disclaimer

This application is for **educational and research purposes only**. Users are responsible for complying with applicable laws and regulations regarding copyright and academic integrity. The developers do not take responsibility for misuse of this tool.

---

## ☕ Support the Project

If you find PyPaperBot useful, consider supporting the developer:

[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.me/ferru97)

---

## 📄 License

This project is open-source. See LICENSE file for details.

---

**Maintained by the PyPaperBot community** | [Telegram](https://t.me/pypaperbotdatawizards) | [Issues](https://github.com/your-repo/issues)
