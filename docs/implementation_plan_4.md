# Implementation Plan 4.0: UX Refinement & CORE Fixes

This plan addresses the remaining usability issues and the CORE API failure identified in the latest test run.

## 1. UX & Filtering Overhaul

### 1.1. Interactive Workflow Improvement
**Problem:** The current CLI flow processes everything (Seed -> Expansion -> Ranking) before asking the user for input. If the expansion is huge (1000+ papers), the user is overwhelmed and the "All" default is dangerous.
**Goal:** Give the user control *earlier* and make the filtering more granular.

**Tasks:**
*   [ ] **Pause after Seed Search:** Display the number of seed papers found and ask if the user wants to proceed with Network Expansion or just download the seeds.
*   [ ] **Smart Filtering Logic:** The current buckets (30 -> 1001 -> 1092 -> 1198) are useless.
    *   Implement a "Top N" filter option (e.g., "Top 50", "Top 100", "Top 200" by Score).
    *   Refine the "Quality" presets to be more discriminative (e.g., stricter citation thresholds for "Medium").
*   [ ] **Interactive Prompt Fix:** Ensure the input prompt handles timeouts gracefully but defaults to a *safe* option (e.g., "Top 20" or "Exit") rather than "Download All 1000".

### 1.2. Preset Integration
**Problem:** The `--preset` argument (general, medicine, cs) exists in `ranking.py` but isn't effectively used to guide the *filtering* or *display*.
**Tasks:**
*   [ ] Display the active preset in the CLI header.
*   [ ] Adjust default filter thresholds based on the preset (e.g., 'medicine' might require higher Journal Impact Factors than 'cs').

---

## 2. CORE API Remediation

### 2.1. Fix 500/Rate Limit Errors
**Problem:** CORE API returned a 500 error. The documentation (lines 2783-2784) confirms free access is allowed but rate-limited. The error might be due to the payload format or strict rate limiting on the `POST` search endpoint.
**Tasks:**
*   [ ] **Switch to GET Request:** The documentation shows `GET /search/works` is the standard way for simple queries. The `POST` endpoint might be reserved or buggy for unauthenticated users.
*   [ ] **Payload Simplification:** If keeping POST, simplify the JSON body.
*   [ ] **Rate Limit Handling:** Implement a specific backoff if `429` is received (CORE sends `X-RateLimit-Retry-After`).

### 2.2. API Key Support
**Problem:** While free access exists, it's limited (100 tokens/day).
**Tasks:**
*   [ ] Add `--core-key` argument to the CLI.
*   [ ] Pass this key to the `CoreSource` to unlock higher limits.

---

## 3. Data & Reporting Integrity

### 3.1. CSV Completeness
**Problem:** Previous reports had "missile cells" (missing data).
**Tasks:**
*   [ ] **Audit `Paper.generateReport`:** Ensure all columns (DOI, SJR, H-Index) are populated from the merged data.
*   [ ] **Fill Missing Values:** If a metric is 0 or None, display "N/A" or "-" instead of leaving it blank or "0.0" which looks like a bug.

---

## 4. Testing Strategy

### Step 1: CORE Fix Verification
*   Create `tests/verification/verify_core_simple.py` using a `GET` request to confirm connectivity.

### Step 2: UX Dry Run
*   Run the CLI with a mock input to verify the new menu options appear and work.

### Step 3: Final "Happy Path"
*   Run a small query, select "Top 10", and verify the download matches exactly what was requested.

