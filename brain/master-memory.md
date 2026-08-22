# Master Memory

## Project Goal
Build a dynamic AI-powered product intelligence engine (UPIE) that takes limited/messy product information, discovers authoritative manufacturer sources, extracts and normalizes product facts, validates them against controlled reference data, generates commerce-ready product content, attaches traceable evidence, and exports an exact 252-column schema.

## Current Phase
Phase 2 - Reference Data

## What's Done
- Formulated and approved the implementation plan.
- Completed Phase 0 (base project setup).
- Built Phase 1 input ingestion layer handling blanks, placeholders, and BOM characters.
- Built Phase 1 deterministic fixed-schema (252-column) output mapper and CSV/XLSX export functions.
- Implemented `/api/jobs` REST endpoints and a minimal React frontend (`App.tsx`, `App.css`).
- Created automated schema tests validating the exact 252 header output.
- Processed the actual `Unihack_ Sample Dataset - Input.csv` successfully yielding 1000 processed rows and valid export files.

## What's Next
- Obtain approval to proceed with Phase 2.
- Wait for user to provide the reference datasets (LOV, UOM, Manufacturer/Brand master).
- Load/Mock reference master data and setup validation logic.
