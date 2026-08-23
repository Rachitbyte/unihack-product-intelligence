# UniHack Product Intelligence Engine (UPIE)

UPIE is an AI-powered pipeline built to solve the messy product catalog challenge. It dynamically takes minimal inputs (e.g., just an MPN and a description), discovers the official manufacturer source, extracts product facts with evidence, normalizes them against reference data, generates e-commerce content, and deterministically builds an exact 252-column export schema.

**Live Demo:** <HOSTED_URL>

## Hackathon Constraints Enforced
* **Manufacturer-Only Evidence:** We explicitly forbid scraping aggregators (Amazon, Walmart, eBay). All truth must trace to the manufacturer.
* **Dynamic Processing:** No hard-coded MPNs, websites, or canned responses. The pipeline reasons dynamically in real-time.
* **Exact 252-Column Output:** Data is precisely mapped without modifying the requested static headers.
* **Evidence-First Validation:** No hallucination. If evidence cannot be found, fields are gracefully left blank or flagged for review.
* **No Mock Data:** The deployed pipeline executes the real processing engine on every row.

## Architecture Pipeline
1. **Identity Resolution:** Resolves the true Manufacturer and MPN using web searches.
2. **Official Source Discovery:** Rejects distributors; finds the true product webpage or PDF.
3. **Structured Extraction:** Gemini extracts raw attribute/value pairs from HTML/PDFs.
4. **Deterministic Normalization & Validation:** Translates raw values using category LOV reference tables.
5. **Content Generation:** AI drafts short descriptions and marketing features strictly from verified facts.
6. **Output Builder:** Dumps the JSON state into the strict 252-column CSV layout.

## Local Setup

### Environment Variables
You must supply a `.env` file in the root directory. Do not commit this file.

```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_IDENTITY_MODEL=gemini-1.5-flash
GEMINI_EXTRACTION_MODEL=gemini-1.5-flash
DATABASE_URL=postgresql://postgres:password@db/upie_db
```

### Running the Application

Ensure Docker is installed, then run:

```bash
docker-compose up --build
```

The services will be available at:
* **Frontend UI:** `http://localhost:80`
* **Backend API:** `http://localhost:8000`

### End-to-End Evaluation

To evaluate the pipeline's capabilities against the 1,000-row sample dataset (or any custom CSV), run:

```bash
python scripts/evaluate.py data/sample/input.csv
```
This script will upload the file, poll the job status, measure the processing time, report failure rates, and download the finalized 252-column output.