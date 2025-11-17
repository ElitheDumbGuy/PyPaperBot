\### Factual Summary of PyPaperBot v1.4.1 Troubleshooting Session



\*\*Objective:\*\* This document outlines the observed behavior, errors, and logical deductions derived from the step-by-step execution and troubleshooting of `PyPaperBot` version 1.4.1. It is intended to serve as a factual brief for a code generation AI.



---



\*\*1. Dependency and Environment Findings\*\*



\*   \*\*Finding 1.1 (Missing Dependency):\*\* Executing `python -m PyPaperBot ...` immediately after a fresh `pip install PyPaperBot` in a new virtual environment resulted in `ModuleNotFoundError: No module named 'undetected\_chromedriver'`.

&nbsp;   \*   \*\*Deduction:\*\* The `PyPaperBot` v1.4.1 `pip` package does not declare `undetected\_chromedriver` as a required dependency, even though its source code at `PyPaperBot/Scholar.py` explicitly imports and uses it.

&nbsp;   \*   \*\*Fact:\*\* The error was resolved by manually executing `pip install undetected\_chromedriver`.



\*   \*\*Finding 1.2 (Python Version Incompatibility):\*\* On a system with Python 3.13.2, execution failed within the `undetected\_chromedriver` library with the error `ModuleNotFoundError: No module named 'distutils'`.

&nbsp;   \*   \*\*Factual Context:\*\* The `distutils` module was removed from Python's standard library in version 3.12.

&nbsp;   \*   \*\*Deduction:\*\* The version of `undetected\_chromedriver` and/or its sub-dependencies pulled by `pip` are not compatible with Python 3.12+.

&nbsp;   \*   \*\*Fact:\*\* All `distutils`-related errors were resolved by creating and using a new virtual environment with Python 3.11.0.



\*   \*\*Finding 1.3 (Browser Driver Mismatch):\*\* Execution with the argument `--selenium-chrome-version=126` failed with `selenium.common.exceptions.SessionNotCreatedException`.

&nbsp;   \*   \*\*Fact:\*\* The explicit error message was: `This version of ChromeDriver only supports Chrome version 126. Current browser version is 142.0.7444.163`.

&nbsp;   \*   \*\*Deduction:\*\* The browser automation component requires the version number specified in the `--selenium-chrome-version` argument to match the major version of the Google Chrome browser installed on the host operating system.

&nbsp;   \*   \*\*Fact:\*\* The exception was resolved by changing the argument to `--selenium-chrome-version=142`.



---



\*\*2. Analysis of Execution Paths and Point of Failure\*\*



Through testing, two distinct execution paths within `PyPaperBot` were identified with different networking mechanisms.



\*   \*\*Execution Path A: The `--query` Method\*\*

&nbsp;   \*   \*\*Observation:\*\* When the `--query` argument is used, the console output includes the line `Using Selenium driver`. A full browser instance is visibly launched.

&nbsp;   \*   \*\*Deduction:\*\* This path utilizes the `undetected\_chromedriver` library to perform a full browser-based scrape of the Google Scholar search results page.

&nbsp;   \*   \*\*Observed Outcome:\*\* This path successfully connects to Google Scholar, executes a search, and parses the results page, indicated by the output `Google Scholar page X : 10 papers found`.



\*   \*\*Execution Path B: The `--doi` Method\*\*

&nbsp;   \*   \*\*Observation:\*\* When the `--doi` argument is used, the console output does \*not\* include the line `Using Selenium driver`. No browser instance is launched.

&nbsp;   \*   \*\*Deduction:\*\* This path utilizes a direct, non-browser-based HTTP request to access the specified resource. The use of a simpler library like `requests` is inferred.



\*   \*\*Point of Failure: The Hand-off\*\*

&nbsp;   \*   \*\*Test 1 (DOI not in DB):\*\* Executing `--doi="10.1002/ijop.70027"` resulted in the output `Download 1 of 1...` but no PDF file was saved. Manual verification of the corresponding Sci-Hub URL revealed an HTML page with the text: "Alas, the following paper is not yet available in my database:".

&nbsp;       \*   \*\*Deduction:\*\* The downloader function does not parse the content of the HTTP response. It incorrectly interprets a valid HTTP 200 OK response (for an HTML page) as a successful PDF download.

&nbsp;   \*   \*\*Test 2 (DOI available in DB):\*\* Executing `--doi="10.1038/171737a0"` (a known-available paper) also resulted in a silent failure (no PDF saved).

&nbsp;       \*   \*\*Deduction:\*\* The simple, non-browser HTTP request used by the `--doi` path is being intercepted by an anti-bot service (e.g., Cloudflare) and is being served an HTML challenge page instead of the target PDF. The downloader function cannot handle this challenge.

&nbsp;   \*   \*\*Test 3 (Forcing the Hand-off):\*\* Executing `--query="10.1038/171737a0"` correctly used the Selenium driver to query Google Scholar, but then failed with `Paper not found...`.

&nbsp;       \*   \*\*Core Deduction:\*\* This test confirms the primary architectural flaw. `PyPaperBot` uses the robust, browser-based \*\*Path A\*\* \*only\* to scrape Google Scholar. Once it extracts a DOI, it hands that DOI off to the simple, non-browser-based, and failing download function from \*\*Path B\*\*. The entire end-to-end process fails at this hand-off.



---



\*\*3. Final Factual Summary\*\*



\*   `PyPaperBot` v1.4.1 has undeclared dependencies (`undetected\_chromedriver`).

\*   Its scraping component has a runtime dependency on a Python version older than 3.12.

\*   The tool contains two distinct network handlers: one robust (browser-based) and one simple (direct HTTP request).

\*   The simple download handler is ineffective against modern anti-bot measures and cannot correctly differentiate between a PDF and an HTML error/challenge page.

\*   The primary workflow (`--query`) is fundamentally broken because it uses the robust handler for scraping but then passes the results to the ineffective handler for the final download step. Any fix must address this flawed hand-off.

