# PyPaperBot Testing Strategy

This document outlines the testing regime for PyPaperBot.

## 1. Test Structure

The `tests/` directory contains the active test suite. Deprecated or manual diagnostic scripts have been moved to `tests/archive/`.

### Active Tests
*   **`test_citation_processor.py`**: Unit tests for `CitationProcessor`. Verifies network building, metadata enrichment, and co-citation calculations using mocked OpenAlex responses.
*   **`test_filter_engine.py`**: Unit tests for `FilterEngine`. Verifies that papers are correctly filtered based on citation counts, journal metrics, and user preferences.
*   **`test_journal_ranking.py`**: Unit tests for `JournalRanker`. Verifies exact and fuzzy matching of journal titles against the SJR database.
*   **`test_project_manager.py`**: Unit tests for `ProjectManager`. Verifies state serialization and deserialization.
*   **`test_scihub_client.py`**: Unit tests for `SciHubClient`. Verifies PDF validation, error handling, and mirror fallback logic (mocked).
*   **`test_cli_smoke.py`**: Smoke tests for the Command Line Interface. Verifies that the entry point works and arguments are parsed correctly.

## 2. Testing Levels

### Level 1: Unit Tests (Run on every commit)
*   **Command**: `pytest tests/`
*   **Scope**: All active tests in `tests/`.
*   **Dependencies**: None (external APIs are mocked).
*   **Goal**: Verify logic correctness and catch regressions.

### Level 2: Integration Tests (Run locally before release)
*   **Command**: Manual execution of `tests/archive/test_scihub_client.py` (if updated) or ad-hoc CLI runs.
*   **Scope**: Tests that hit real external APIs (Google Scholar, OpenAlex, Sci-Hub).
*   **Goal**: Verify API connectivity and handling of real-world data formats.
*   **Note**: These are often fragile due to rate limiting and captcha.

### Level 3: End-to-End CLI Tests
*   **Command**: `python -m PyPaperBot --query="machine learning" --scholar-pages=1 --dwn-dir="test_output"`
*   **Goal**: Verify the full application flow from argument parsing to file download.

## 3. CI/CD Pipeline

The project uses GitHub Actions (`.github/workflows/test.yml`) to automate Level 1 tests.
*   **Trigger**: Push to `master`/`main`, Pull Requests.
*   **Actions**:
    1.  Set up Python environment.
    2.  Install dependencies.
    3.  Run `pytest tests/ -v`.
    4.  Run `flake8` linter on `src/PyPaperBot/`.

## 4. Adding New Tests

1.  **Unit Tests**: Add a new `test_*.py` file in `tests/`. Use `unittest.mock` to avoid external network calls.
2.  **Integration Tests**: If a test requires network access, mark it explicitly or keep it in a separate `tests/integration/` folder (future work).

## 5. Maintenance

*   **Archive**: Old diagnostic scripts are in `tests/archive/`. Do not run these in CI.
*   **Cleanup**: Periodically review `tests/archive/` and delete files that are no longer useful.

