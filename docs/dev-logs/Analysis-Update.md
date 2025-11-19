# PyPaperBot - Citation Analysis & Journal Ranking Feature Implementation Plan

## 🎉 IMPLEMENTATION STATUS: COMPLETE

All core modules have been implemented, tested, and integrated into the main application. The citation network expansion feature is now fully functional.

---

## 1. Introduction & High-Level Goal

This document outlines the implementation plan for a major new feature in PyPaperBot: **Citation Network Analysis and Journal Quality Filtering**. The goal is to transform PyPaperBot from a simple paper downloader into a smart literature review assistant.

**✅ STATUS: Successfully implemented and tested on 2025-11-18**

The core idea is to move beyond a flat list of papers from a search query and instead build a rich, interconnected network of academic literature, allowing users to intelligently discover and download the most relevant and impactful papers.

### Confirmed User Workflow

The final user workflow will be as follows:

1.  **Seed Paper Acquisition**: The user provides a query, and the tool scrapes Google Scholar to get an initial list of "seed" papers.
2.  **Enrichment Phase**: The tool automatically enriches this seed list by:
    *   Querying the **OpenCitations API** to find all papers that *cite* the seed papers (forward citations) and all papers *cited by* the seed papers (references/backward citations).
    *   Querying a local copy of the **Scimago Journal & Country Rank** database (`scimagojr 2024.csv`) to get quality metrics (H-Index, SJR score, Quartile) for the journal of every paper in the network.
3.  **Interactive Filtering**: The tool calculates a "quality score" for every paper in the expanded network based on co-citation frequency and journal rank. It then presents the user with simple, interactive filtering modes:
    *   `High Quality (Strict)`: Shows a small number of highly relevant, high-impact papers.
    *   `Medium Quality (Balanced)`: A good mix of relevance and discovery.
    *   `Broad Scope (Inclusive)`: A larger set for comprehensive reviews.
4.  **User Selection & Download**: The user selects a quality level. The tool then downloads only the papers that pass this filter. The seed papers themselves are not guaranteed to be downloaded if they don't meet the quality criteria.
5.  **Resumable Projects**: The entire state of the network (discovered papers, downloaded papers, API caches) is saved, allowing the user to resume a project later, expand the network deeper, or re-filter with different criteria.

---

## 2. Phase 1: Core Data Modules (Independent Components)

Each task in this phase will be developed in a separate module and will have its own dedicated test suite. Components will not be integrated into the main application until they are fully tested and validated.

### Task 1.1: Journal Metrics Module

-   **Goal**: Create a module that can efficiently look up journal quality metrics (SJR, H-Index) from the `scimagojr 2024.csv` file using fuzzy string matching.
-   **New Files**:
    -   `PyPaperBot/JournalRanking.py`
    -   `tests/test_journal_ranking.py`
-   **Dependencies**: `pandas`, `rapidfuzz`
-   **Implementation Steps**:
    1.  Create a `JournalRanker` class in `JournalRanking.py`.
    2.  The constructor (`__init__`) will load `data/scimagojr 2024.csv` into a pandas DataFrame. This should only happen once. The key columns (`Title`, `SJR`, `H index`, `SJR Best Quartile`) should be processed and cleaned.
    3.  Implement a public method `get_metrics(self, journal_title: str) -> dict | None`.
    4.  This method will use `rapidfuzz.process.extractOne` to find the best match for `journal_title` in the `Title` column of the DataFrame. A matching score threshold of ~85 should be used.
    5.  If a good match is found, it will return a dictionary containing the SJR score, H-index, and Quartile. Otherwise, it will return `None`.
-   **Testing Strategy (`tests/test_journal_ranking.py`)**:
    1.  The test suite will initialize `JournalRanker` once.
    2.  **Test Case 1 (Exact Match)**: Use a journal title directly from `@tests/test_final_fixed/result.csv`, like `"Consciousness and Cognition"`, and assert that the correct H-Index and SJR are returned.
    3.  **Test Case 2 (Fuzzy Match)**: Test the title `"Journal of Nervous &amp; Mental Disease"`. The test should assert that it correctly matches `"Journal of Nervous and Mental Disease"` in the CSV and returns the correct metrics.
    4.  **Test Case 3 (No Match)**: Test with a fake journal title like `"Journal of Fictional Studies"` and assert that the method returns `None`.
    5.  **Test Case 4 (Edge Cases)**: Test with an empty string or `None` as input.

### Task 1.2: OpenCitations API Client ✅

-   **Goal**: Create a robust, reusable client for the OpenCitations API that includes error handling, rate-limiting awareness, and file-based caching to prevent redundant API calls.
-   **New Files**:
    -   `PyPaperBot/OpenCitations.py` ✅
    -   `tests/test_opencitations_client.py` ✅
-   **Dependencies**: `requests`
-   **Critical Implementation Note**: The OpenCitations API v2 requires DOIs to be prefixed with `doi:` in the URL path (e.g., `/references/doi:10.1234/example`).
-   **Implementation Steps**:
    1.  Create an `OpenCitationsClient` class in `OpenCitations.py`.
    2.  The constructor will accept an optional API token and a cache file path. It will load the cache from the JSON file if it exists.
    3.  Implement public methods: `get_references(self, doi: str)` and `get_citations(self, doi: str)`.
    4.  These methods will first check the in-memory cache for the DOI. If found, they return the cached data instantly.
    5.  If not in the cache, they will make a `GET` request to the `https://api.opencitations.net/index/v2/` endpoint. The request should include the API token in the `authorization` header if provided.
    6.  Implement robust error handling (e.g., for 404 Not Found, 429 Too Many Requests). Use a simple retry mechanism for transient network errors.
    7.  Implement a helper method `_extract_doi_from_pid_string(pid_string: str)` to parse the DOI from the complex PID string returned by the API (e.g., `"omid:br/06101801781 doi:10.7717/peerj-cs.421 pmid:33817056"`).
    8.  Upon a successful API response, store the result in the cache and save the cache to the JSON file.
-   **Testing Strategy (`tests/test_opencitations_client.py`)**:
    1.  Use `requests-mock` to avoid hitting the live API during tests.
    2.  **Test Case 1 (Successful Fetch)**:
        -   Use a DOI from `@tests/test_final_fixed/result.csv`, like `10.1016/j.concog.2016.03.017`.
        -   Mock a successful API response for both `/references/{doi}` and `/citations/{doi}`.
        -   Call the client methods and assert that they return the correctly parsed list of DOIs.
    3.  **Test Case 2 (Caching Logic)**:
        -   Call `get_references` for a DOI. The `requests-mock` adapter should register one call.
        -   Call `get_references` for the same DOI again. Assert that the mock adapter registered *no new calls* and the data returned is the same.
    4.  **Test Case 3 (API Error)**: Mock a 404 response and assert that the client method handles it gracefully (e.g., returns an empty list).
    5.  **Test Case 4 (DOI Parsing)**: Test the `_extract_doi_from_pid_string` helper with various valid and invalid input strings.

---

## 3. Phase 2: Core Logic & Orchestration

### Task 2.1: Data Enrichment & Network Building

-   **Goal**: Create an orchestrator that takes a list of seed papers and uses the modules from Phase 1 to build a complete, enriched citation network.
-   **New Files**:
    -   `PyPaperBot/CitationProcessor.py`
    -   `tests/test_citation_processor.py`
-   **Implementation Steps**:
    1.  Create a `CitationProcessor` class.
    2.  Implement a main method `build_network(self, seed_papers: list)`.
    3.  This method will initialize the `JournalRanker` and `OpenCitationsClient`.
    4.  It will iterate through the seed papers, calling the OpenCitations client to get all references and citations, creating a set of all unique DOIs in the 1-degree network.
    5.  It will then iterate through the complete set of DOIs. For each one, it creates a `Paper` object and enriches it with journal metrics from the `JournalRanker`.
    6.  It will calculate the **co-citation count** for each paper (i.e., how many of the *seed papers* cite it).
    7.  The final output will be a dictionary of `Paper` objects, keyed by DOI, representing the complete, enriched network.
-   **Testing Strategy (`tests/test_citation_processor.py`)**:
    1.  Use `unittest.mock` to create mock versions of `JournalRanker` and `OpenCitationsClient` that return predictable data.
    2.  Create a list of mock `Paper` objects based on the first few rows of `@tests/test_final_fixed/result.csv`.
    3.  **Test Case 1 (Network Structure)**: Run the processor and assert that the output network contains the seed papers plus the mock references and citations.
    4.  **Test Case 2 (Enrichment)**: Assert that every paper in the output network has been enriched with the mock journal and citation data.
    5.  **Test Case 3 (Co-citation Calculation)**: Configure the mock OpenCitations client so that a specific DOI is returned as a reference by multiple seed papers. Assert that this paper has the correct co-citation count in the final network.

### Task 2.2: Interactive Filtering Engine

-   **Goal**: Create a module that takes the enriched network data, applies configurable filter presets, and prompts the user for a selection.
-   **New Files**:
    -   `PyPaperBot/FilterEngine.py`
    -   `tests/test_filter_engine.py`
-   **Implementation Steps**:
    1.  Create a `FilterEngine` class.
    2.  Define the filter presets (High, Medium, Low) as dictionaries of thresholds (e.g., `{'min_cocitations': 3, 'min_h_index': 100}`).
    3.  Implement a method `get_filtered_list(self, network: dict) -> list`.
    4.  This method will iterate through the presets, apply them to the network, and count the number of resulting papers.
    5.  It will then print the formatted, interactive menu to the console.
    6.  It will capture user input and return the final list of `Paper` objects that match the selected filter.
-   **Testing Strategy (`tests/test_filter_engine.py`)**:
    1.  Create a sample network dictionary with a variety of papers designed to pass or fail specific filter criteria.
    2.  **Test Case 1 (Filtering Logic)**: For each preset, call a non-interactive version of the filter logic and assert that it returns the correct subset of papers.
    3.  **Test Case 2 (Interactive Flow)**: Use `unittest.mock.patch` to mock the `builtins.input` function to simulate a user selecting "1", "2", etc. Assert that the final returned list is correct for each simulated choice.

---

## 4. Phase 3: Integration into Main Application

### Task 3.1: Project State Management

-   **Goal**: Implement logic to save and load the entire state of a session to a JSON file to enable resume functionality.
-   **New Files**:
    -   `PyPaperBot/ProjectManager.py`
    -   `tests/test_project_manager.py`
-   **Implementation Steps**:
    1.  Define a clear JSON schema for the project state (`project_state.json`), including API cache, list of downloaded DOIs, discovered DOIs, etc.
    2.  Create `save_state` and `load_state` functions that handle JSON serialization/deserialization.
-   **Testing Strategy (`tests/test_project_manager.py`)**:
    1.  Create a complex state dictionary.
    2.  Save it to a temporary file, load it back, and assert that the loaded object is identical to the original.

### Task 3.2: Modify `__main__.py` Workflow

-   **Goal**: Integrate all new modules into the main application logic, controlled by new CLI arguments.
-   **Files to Modify**: `PyPaperBot/__main__.py`, `README.md`, `requirements.txt`
-   **Implementation Steps**:
    1.  Add new arguments to `argparse`: `--expand-network`, `--resume-project <path>`.
    2.  At the start of `main()`, check for `--resume-project`. If present, load the state and present the user with resume options (e.g., "Continue download", "Expand deeper").
    3.  If starting a new project, modify the flow to:
        a. Get seed papers from `ScholarPapersInfo`.
        b. Pass seeds to `CitationProcessor.build_network`.
        c. Pass the network to `FilterEngine.get_filtered_list`.
        d. Pass the final, filtered list of papers to the existing `downloadPapers` function.
    4.  Update the `Paper.py` class to include new fields for journal metrics and citation counts.
    5.  Update `Paper.generateReport` to include the new columns in the CSV output.
    6.  Add `rapidfuzz` to `requirements.txt`.
    7.  Update `README.md` to document the powerful new workflow.
-   **Integration Testing**:
    1.  Perform an end-to-end run using a real query (e.g., `"Maladaptive Daydreaming"`).
    2.  Set `--scholar-pages=1` to limit the number of seed papers.
    3.  Manually verify that the interactive prompt appears and shows plausible numbers.
    4.  Select a filter level and verify that the correct papers (and only those papers) are downloaded.
    5.  Verify the new columns are present and populated in the final `result.csv`.
    6.  Interrupt a run and restart it with `--resume-project` to ensure it picks up where it left off.
