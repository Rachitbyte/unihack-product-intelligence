# Master Memory

## Project Goal
Build a dynamic AI-powered product intelligence engine (UPIE) that takes limited/messy product information, discovers authoritative manufacturer sources, extracts and normalizes product facts, validates them against controlled reference data, generates commerce-ready product content, attaches traceable evidence, and exports an exact 252-column schema.

## Current Phase
Phase 4 - Source Retrieval

## What's Done
- Formulated and approved the implementation plan.
- Completed Phase 0, Phase 1, and Phase 2.
- Completed Phase 3 (Product Identity):
  - Built `IdentityResolver` utilizing Gemini Search to pinpoint official manufacturer sources using MPN as the primary signal.
  - Set up dynamic resolution allowing four states (`VERIFIED`, `NEEDS_REVIEW`, `CONFLICT`, `FAILED`).
  - Added strict confidence and evidence URL tracking.
  - Linked `IdentityResult` non-destructively to `ProductRow` schema.

## What's Next
- Proceed with Phase 4 (Source Retrieval).
- Implement web crawling/scraping using the verified `evidence_urls` from Phase 3.
- Handle fetching raw content for attribute extraction.
