[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.me/ferru97)

# NEWS: PyPaperBot development is back on track!
### Join the [Telegram](https://t.me/pypaperbotdatawizards) channel to stay updated, report bugs, or request custom data mining scripts.
---

# PyPaperBot

PyPaperBot is a Python tool for **downloading scientific papers and bibtex** using Google Scholar, Crossref, SciHub, and SciDB.
The tool tries to download papers from different sources such as PDF provided by Scholar, Scholar related links, and Scihub.
PyPaperbot is also able to download the **bibtex** of each paper.

## Features

- Download papers given a query
- Download papers given paper's DOIs
- Download papers given a Google Scholar link
- Generate Bibtex of the downloaded paper
- Filter downloaded paper by year, journal and citations number
- **Hybrid download mode**: Automatically falls back from HTTP to Selenium when encountering anti-bot measures
- **Improved Chrome detection**: Auto-detects Chrome installation and version on Windows, macOS, and Linux
- **PDF validation**: Validates downloaded files are actual PDFs, not HTML error pages

## Requirements

- Python 3.11 or higher (Python 3.12+ may have compatibility issues with some dependencies)
- Google Chrome browser (for Selenium-based downloads, auto-detected)
- Internet connection

## Installation

### Quick Start (Recommended)

**Windows:**
```bash
pypaperbot.bat --query="machine learning" --scholar-pages=1 --dwn-dir="./output" --restrict=1
```

**Linux/Mac:**
```bash
chmod +x pypaperbot.sh
./pypaperbot.sh --query="machine learning" --scholar-pages=1 --dwn-dir="./output" --restrict=1
```

The wrapper scripts automatically:
- Create a virtual environment if it doesn't exist
- Install all dependencies
- Run PyPaperBot from source

**No manual installation required!**

### Manual Installation (Alternative)

If you prefer to set up manually:

```bash
git clone <repository-url>
cd PyPaperBot
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m PyPaperBot --query="..." --scholar-pages=1 --dwn-dir="./output"
```

**Note**: The package includes `undetected-chromedriver` and `selenium` as dependencies. If you encounter issues with Python 3.12+, consider using Python 3.11.

If on windows you get an error saying *error: Microsoft Visual C++ 14.0 is required..* try to install [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/it/visual-cpp-build-tools/) or [Visual Studio](https://visualstudio.microsoft.com/it/downloads/)

### For Termux users

Since numpy cannot be directly installed, set it up first:

```bash
pkg install wget
wget https://its-pointless.github.io/setup-pointless-repo.sh
pkg install numpy
export CFLAGS="-Wno-deprecated-declarations -Wno-unreachable-code"
pip install pandas
```

Then use the wrapper script:

```bash
git clone <repository-url>
cd PyPaperBot
chmod +x pypaperbot.sh
./pypaperbot.sh --query="..." --scholar-pages=1 --dwn-dir="./output"
```

## How to use

The easiest way is to use the wrapper scripts (see Installation section above). They handle everything automatically.

If you prefer to run manually with an activated virtual environment:

```bash
# Activate venv first
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Then run
python -m PyPaperBot --query="machine learning" --scholar-pages=1 --dwn-dir="./output" --restrict=1
```

### PyPaperBot Arguments

| Arguments                   | Description                                                                                                                                                                           | Type   |
|-----------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------|
| \-\-query                   | Query to make on Google Scholar or Google Scholar page link                                                                                                                           | string |
| \-\-skip-words              | List of comma separated words i.e. "word1,word2 word3,word4". Articles containing any of this word in the title or google scholar summary will be ignored                             | string |
| \-\-cites                   | Paper ID (from scholar address bar when you search cites) if you want get only citations of that paper                                                                                | string                              | string |
| \-\-doi                     | DOI of the paper to download (this option uses only SciHub to download)                                                                                                               | string |
| \-\-doi-file                | File .txt containing the list of paper's DOIs to download                                                                                                                             | string |
| \-\-scholar-pages           | Number or range of Google Scholar pages to inspect. Each page has a maximum of 10 papers                                                                                              | string |
| \-\-dwn-dir                 | Directory path in which to save the result                                                                                                                                            | string |
| \-\-min-year                | Minimal publication year of the paper to download                                                                                                                                     | int    |
| \-\-max-dwn-year            | Maximum number of papers to download sorted by year                                                                                                                                   | int    |
| \-\-max-dwn-cites           | Maximum number of papers to download sorted by number of citations                                                                                                                    | int    |
| \-\-journal-filter          | CSV file path of the journal filter (More info on github)                                                                                                                             | string |
| \-\-restrict                | 0:Download only Bibtex - 1:Download only papers PDF                                                                                                                                   | int    |
| \-\-scihub-mirror           | Mirror for downloading papers from sci-hub. If not set, it is selected automatically                                                                                                  | string |
| \-\-annas-archive-mirror    | Mirror for downloading papers from Annas Archive (SciDB). If not set, https://annas-archive.se is used                                                                                | string |
| \-\-scholar-results         | Number of scholar results to bedownloaded when \-\-scholar-pages=1                                                                                                                    | int    |
| \-\-proxy                   | Proxies to be used. Please specify the protocol to be used.                                                                                                                           | string |
| \-\-single-proxy            | Use a single proxy. Recommended if using --proxy gives errors.                                                                                                                        | string |
| \-\-selenium-chrome-version | Chrome version number (major version). If provided, Selenium will be used for scholar search. Auto-detected if Chrome is installed. | int    |
| \-\-use-doi-as-filename     | If provided, files are saved using the unique DOI as the filename rather than the default paper title                                                                                 | bool    |
| \-\-headless                | Run Chrome in headless mode (may trigger bot detection)                                                                                                                              | bool    |
| \-\-no-headless             | Run Chrome with visible browser window (default, more reliable)                                                                                                                      | bool    |
| \-\-scihub-mode             | Sci-Hub download mode: auto (HTTP then Selenium), http (HTTP only), selenium (Selenium only). Default: auto                                                                        | string |
| \-h                         | Shows the help                                                                                                                                                                        | --     |

### Note

You can use only one of the arguments in the following groups

- *\-\-query*, *\-\-doi-file*, and *\-\-doi* 
- *\-\-max-dwn-year* and *and max-dwn-cites*

One of the arguments *\-\-scholar-pages*, *\-\-query *, and* \-\-file* is mandatory
The arguments *\-\-scholar-pages* is mandatory when using *\-\-query *
The argument *\-\-dwn-dir* is mandatory

The argument *\-\-journal-filter* requires the path of a CSV file containing a list of journal names paired with a boolean (0: don't consider / 1: consider). Format: `journal_list;include_list` with semicolon separator.

The argument *\-\-doi-file* requires the path of a text file containing a list of paper DOIs to download, with one DOI per line.

Use the --proxy argument at the end of all other arguments and specify the protocol to be used. See the examples to understand how to use the option.

## SciHub access

If access to SciHub is blocked in your country, consider using a free VPN service like [ProtonVPN](https://protonvpn.com/) 
Also, you can use proxy option above.

## Example

Download a maximum of 30 papers from the first 3 pages given a query and starting from 2018 using the mirror https://sci-hub.do:

```bash
python -m PyPaperBot --query="Machine learning" --scholar-pages=3  --min-year=2018 --dwn-dir="C:\User\example\papers" --scihub-mirror="https://sci-hub.do"
```

Download papers from pages 4 to 7 (7th included) given a query and skip words:

```bash
python -m PyPaperBot --query="Machine learning" --scholar-pages=4-7 --dwn-dir="C:\User\example\papers" --skip-words="ai,decision tree,bot"
```

Download a paper given the DOI:

```bash
python -m PyPaperBot --doi="10.0086/s41037-711-0132-1" --dwn-dir="C:\User\example\papers" -use-doi-as-filename`
```

Download papers given a file containing the DOIs:

```bash
python -m PyPaperBot --doi-file="C:\User\example\papers\file.txt" --dwn-dir="C:\User\example\papers"`
```

If it doesn't work, try to use *py* instead of *python* i.e.

```bash
py -m PyPaperBot --doi="10.0086/s41037-711-0132-1" --dwn-dir="C:\User\example\papers"`
```

Search papers that cite another (find ID in scholar address bar when you search citations):

```bash
python -m PyPaperBot --cites=3120460092236365926
```

Using proxy

```
python -m PyPaperBot --query=rheumatoid+arthritis --scholar-pages=1 --scholar-results=7 --dwn-dir=/download --proxy="http://1.1.1.1::8080,https://8.8.8.8::8080"
```
```
python -m PyPaperBot --query=rheumatoid+arthritis --scholar-pages=1 --scholar-results=7 --dwn-dir=/download -single-proxy=http://1.1.1.1::8080
```

Using hybrid download mode (automatically falls back to Selenium if HTTP fails):

```bash
python -m PyPaperBot --query="machine learning" --scholar-pages=1 --dwn-dir="C:\User\example\papers" --scihub-mode=auto
```

Force Selenium-only mode for Sci-Hub downloads:

```bash
python -m PyPaperBot --query="machine learning" --scholar-pages=1 --dwn-dir="C:\User\example\papers" --scihub-mode=selenium
```

Run Chrome with visible window (for debugging):

```bash
python -m PyPaperBot --query="machine learning" --scholar-pages=1 --dwn-dir="C:\User\example\papers" --no-headless
```

In termux, you can directly use ```PyPaperBot``` followed by arguments...

## Contributions

Feel free to contribute to this project by proposing any change, fix, and enhancement on the **dev** branch

### To do

- Tests
- Code documentation
- General improvements

## Disclaimer

This application is for educational purposes only. I do not take responsibility for what you choose to do with this application.

## Donation

If you like this project, you can give me a cup of coffee :) 

[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.me/ferru97)

yeah, 我们接管啦~