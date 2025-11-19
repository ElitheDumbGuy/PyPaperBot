# Performance Optimizations

## Changes Made for Faster Downloads

### 1. Removed Unnecessary Delays
- **Before**: `time.sleep(random.randint(1, 3))` when extracting PDF links from HTML
- **After**: Removed sleep - no delay needed
- **Impact**: Saves 1-3 seconds per paper that requires HTML parsing
- **Files**: `PyPaperBot/scihub_client.py`, `PyPaperBot/Downloader.py`

### 2. Reduced HTTP Timeouts
- **Before**: 30 second timeout for all HTTP requests
- **After**: 15 second timeout
- **Impact**: Faster failure on dead mirrors/blocked sites, move to fallback faster
- **Files**: `PyPaperBot/scihub_client.py`, `PyPaperBot/Downloader.py`

### 3. Reduced Crossref API Delays
- **Before**: `time.sleep(random.randint(1, 10))` between Crossref lookups
- **After**: `time.sleep(random.uniform(0.5, 2.0))`
- **Impact**: For 100 papers, saves ~6-8 minutes of just waiting
- **Files**: `PyPaperBot/Crossref.py`

### 4. Changed Default Browser Mode
- **Before**: Headless mode by default (gets blocked by Google Scholar)
- **After**: Non-headless mode by default (visible browser, but works reliably)
- **Impact**: Prevents "0 papers found" failures due to bot detection
- **Files**: `PyPaperBot/__main__.py`

## Download Strategy (Fastest to Slowest)

1. **Google Scholar Direct PDF Link** (HTTP, ~1-2 seconds)
   - Try direct PDF link from Scholar results
   - Validate PDF header

2. **Google Scholar PDF Link** (HTTP, ~1-2 seconds)
   - Try scholar_link if it ends with `.pdf`
   - Validate PDF header

3. **SciDB/Anna's Archive** (HTTP, ~2-5 seconds)
   - Try SciDB with DOI
   - Extract PDF link if HTML page returned
   - Validate PDF header

4. **Sci-Hub (DOI)** (HTTP then Selenium fallback, ~3-15 seconds)
   - Try up to 2 Sci-Hub mirrors
   - HTTP first (fast)
   - Selenium fallback if HTTP fails
   - Validate PDF header
   - Detect "not available" vs other errors

5. **Sci-Hub (Scholar Link)** (HTTP then Selenium fallback, ~3-15 seconds)
   - Same as above but using Scholar link instead of DOI
   - Last resort attempt

## Error Handling

- Each download attempt wrapped in try-except
- Individual paper failures don't crash the entire process
- CSV updated every 10 papers to prevent data loss
- Specific error messages for:
  - "Paper not available in Sci-Hub database"
  - Network timeouts
  - Invalid PDF content
  - Captcha/Cloudflare challenges

## Expected Performance

For 100 papers with mixed availability:
- **Scholar scraping**: ~5-10 minutes (includes Crossref lookups)
- **Direct PDF downloads**: ~1-2 seconds per paper
- **SciDB downloads**: ~2-5 seconds per paper
- **Sci-Hub downloads**: ~5-15 seconds per paper (tries 2 mirrors)
- **Total time**: ~15-30 minutes for 100 papers (depends on availability)

## Bottlenecks That Remain

1. **Crossref API lookups**: Still requires 0.5-2 second delay to avoid rate limiting
2. **Google Scholar rate limiting**: May require IP changes if scraping many pages
3. **Sci-Hub mirrors**: Some mirrors are slow or blocked, tries 2 before giving up
4. **Browser automation**: Non-headless mode shows browser window (distraction but necessary)

