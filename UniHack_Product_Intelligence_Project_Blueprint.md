# UniHack — AI-Powered Product Intelligence Prototype
## Master Project Blueprint for Antigravity

> **Purpose:** This document is the single source of truth for building the UniHack prototype. It combines the useful structure from the supplied "6 Documents You Should Create Before Vibe Coding Any App" document with the project-specific requirements, datasets, architecture, workflow, validation strategy, UI direction, backend schema, and implementation order developed for this challenge.
>
> **Important:** Do not start by building a generic AI scraper. Build the evidence-first, validation-first product intelligence pipeline described below.

---

# 0. Executive Summary

## One-line product idea

Build a dynamic AI-powered product intelligence engine that takes limited/messy product information, discovers authoritative manufacturer sources, extracts and normalizes product facts, validates them against controlled reference data, generates commerce-ready product content, attaches traceable evidence, and exports the exact required CSV/XLSX schema.

## Core flow

```text
Input CSV
   ↓
Preprocess / clean input
   ↓
Resolve product identity
   ↓
Discover official manufacturer sources
   ↓
Retrieve product pages / PDFs / assets
   ↓
Extract evidence-backed facts
   ↓
Determine applicable category attributes
   ↓
Normalize using LOV / UOM / reference data
   ↓
Deterministic validation + conflict detection
   ↓
Generate controlled commerce content
   ↓
Validate generated content
   ↓
Map official digital assets
   ↓
Build exact 252-column output
   ↓
CSV / XLSX download
```

## Core principle

**AI proposes and understands. Evidence proves. Reference data standardizes. Deterministic rules validate.**

The system must never invent a value merely because an LLM thinks it is plausible.

---

# 1. Challenge Understanding

## Problem statement

Industrial manufacturers have large amounts of product information spread across websites, catalogs, technical documents, specifications, and digital assets. Raw product data supplied to commerce systems is often abbreviated, incomplete, inconsistent, duplicated, incorrectly branded, or missing many attributes.

The challenge is to automate the transformation of this limited raw information into accurate, standardized, commerce-ready product intelligence.

Expected capabilities:

- Generate structured product intelligence from limited inputs.
- Improve product data quality and consistency.
- Validate and enrich information with traceable outputs.
- Scale across large product catalogs.
- Use approaches such as agents, RAG, knowledge graphs, document intelligence, vision-language models, and human-in-the-loop workflows where they add real value.

## Non-negotiable hackathon constraints

1. The pipeline must be **dynamic and end-to-end**.
2. It must work on **unseen evaluation data**, not only the sample.
3. Do not hard-code products, manufacturers, or expected answers.
4. Digital/product evidence must come from the **manufacturer's own website or official documentation**.
5. Third-party e-commerce/marketplace sources such as Amazon/eBay are prohibited as product evidence.
6. Every important fact should have traceable supporting source evidence whenever the output schema allows it.
7. The final file must preserve **all required static output headers exactly**.
8. Output should be generated as downloadable **CSV or XLSX**.
9. Cost must remain practical; do not send every task through the most expensive model or call vision unnecessarily.
10. Missing evidence must result in blank/unknown/review status, not fabricated values.

---

# 2. Source Material and Ground Truth

## Supplied methodology document

The supplied "6 Documents You Should Create Before Vibe Coding Any App" document is useful as a project-management structure:

1. PRD
2. TRD
3. App Flow
4. UI/UX Design Brief
5. Backend Schema
6. Implementation Plan

We adopt this structure, but merge it into one master blueprint so Antigravity has one coherent source of truth instead of six disconnected documents.

The document's important principle is retained:

> Do not ask an AI coding agent to build the whole application from a vague idea. Give it product requirements, technical direction, user flow, UI direction, database logic, and an ordered implementation plan first.

## Actual sample input

The supplied sample input CSV contains:

- **1,000 rows**
- **6 columns**

Columns:

```text
Mfg_Part_Num
Part_Desc
E1_Brand
Unilog_Brand
DIB_Brand
Part_Manuf
```

Example first row from the actual supplied CSV:

```text
Mfg_Part_Num:
DCB518ASTS06G

Part_Desc:
DCB518ASTS06G Diablo 1/2"x18" - Sanding Belt 6pc

E1_Brand:
-- Unbranded --

Unilog_Brand:
-- No Unilog Brand --

DIB_Brand:
-- No DIB Brand --

Part_Manuf:
Freud Inc (2435)
```

## Actual expected output

The supplied Expected Output / Delivery Format CSV contains:

- **2 example rows**
- **252 fixed columns**

The 2 example rows are examples of how enriched records should look; they are not enough to infer that every product must fill every field.

Blank output cells are legitimate when information is unavailable or unsupported. Do not fabricate values merely to remove blanks.

---

# 3. Product Requirements Document (PRD)

## Product name

**UniHack Product Intelligence Engine**

Temporary internal codename:

**UPIE**

Do not build branding as the priority. The working data pipeline is the product.

## Target users

Primary user:

- Hackathon judge/demo evaluator
- Data/content operations user
- Product catalog manager
- Industrial commerce/catalog enrichment team

## User problem

A catalog operator starts with limited information such as an MPN, short description, and weak brand/manufacturer clues. They need a complete, standardized product record without manually searching manufacturer websites, reading PDFs, extracting specs, normalizing units, writing product content, and assembling digital assets.

## Product promise

Turn:

```text
MPN + messy description + weak metadata
```

into:

```text
verified product identity
+ structured attributes
+ normalized values
+ commerce descriptions
+ official digital assets
+ source evidence
+ final CSV/XLSX
```

## Core features

### F1. CSV upload

Upload an input CSV matching or extending the challenge input pattern.

### F2. Dynamic row processing

Process every row independently and dynamically.

### F3. Product identity resolution

Resolve:

- manufacturer
- brand
- product
- MPN
- category/classpath

from input clues and official source evidence.

### F4. Official source discovery

Find:

- manufacturer product pages
- official specification PDFs
- official manuals
- official catalogs
- official images
- other relevant official digital assets

### F5. Evidence extraction

Extract:

- attribute name
- raw value
- normalized value
- unit
- source URL
- source type
- evidence text
- page number where applicable
- confidence
- validation status

### F6. Category-aware attribute extraction

Determine which attributes apply based on the category/LOV/reference data.

### F7. Normalization

Use:

- manufacturer/brand master
- category LOV
- UOM standards
- decimal/fraction mapping
- category-specific reference files

### F8. Deterministic validation

Validate:

- allowed values
- units
- naming/casing
- character limits
- source presence
- source domain
- evidence support
- schema validity

### F9. Controlled content generation

Generate:

- mobile description
- invoice description
- short description
- long description
- retail description
- marketing description
- feature fields
- product name
- other content fields supported by rules/data

### F10. Digital asset mapping

Populate official asset columns when official assets are found.

### F11. Confidence and review

Classify product/field results as:

- VERIFIED
- NEEDS_REVIEW
- NOT_FOUND
- CONFLICT
- FAILED

Do not force automation when evidence is insufficient.

### F12. Export

Generate the exact 252-column output schema as CSV and XLSX.

---

# 4. MVP Scope

## What must work

The prototype must demonstrate a real end-to-end path for unseen input.

Minimum viable slice:

1. Upload CSV.
2. Read MPN + description + source clues.
3. Resolve likely manufacturer/product.
4. Discover official manufacturer source.
5. Retrieve at least one official source.
6. Extract a useful set of evidence-backed attributes.
7. Normalize at least key values using the provided reference data.
8. Validate those attributes.
9. Generate controlled product content.
10. Map source URLs/assets.
11. Produce the fixed output schema.
12. Show evidence and confidence in the UI.
13. Allow CSV/XLSX download.

## Recommended demo depth

Do not attempt to perfectly support every category in the first implementation.

Use a **category-adapter architecture**:

```text
Generic pipeline
     +
Category adapter(s)
```

Start with one category that has strong reference specifications, then expand.

**Recommended flagship category: Fittings**, because the supplied Fittings reference data is explicitly designed around normalization and canonical values.

However, the runtime architecture must remain generic and must not contain product-specific hard-coding.

## Features not in v1

Do not prioritize:

- Full enterprise authentication
- Full billing/payment system
- Large knowledge-graph infrastructure
- Custom model training
- Multi-agent swarm architecture
- Perfect support for every product category
- 100% automatic filling of every field regardless of evidence
- Decorative dashboards with little operational value

---

# 5. Success Metrics

## Primary evaluation metrics

### A. Product identity accuracy

Percentage of products for which manufacturer/brand/product identity is correct.

### B. Attribute accuracy

For fields that are populated, compare normalized values against available ground truth.

### C. Source traceability

Percentage of supported facts that have a traceable official manufacturer source.

### D. LOV compliance

Percentage of normalized values that match allowed LOV values where applicable.

### E. UOM compliance

Percentage of units matching approved UOM rules.

### F. Content rule compliance

Percentage of generated descriptions satisfying:

- character limits
- casing
- formatting
- construction rules
- allowed terminology

### G. False-positive / hallucination rate

Unsupported values should be near zero.

### H. Review rate

A measured percentage of records/fields sent to review because the system lacks enough evidence or detects conflicts.

### I. Processing cost

Track approximate model/API cost per row and per 1,000 rows.

### J. Processing time

Track average and total processing time for the sample/evaluation batch.

---

# 6. Technical Requirements Document (TRD)

## Architecture principle

Keep the LLM out of responsibilities that are safer and cheaper as deterministic code.

### Use AI for

- ambiguous product understanding
- identity reasoning
- document understanding
- semantic extraction
- classification assistance
- evidence-grounded content generation
- selective image understanding

### Use deterministic code for

- CSV ingestion
- schema enforcement
- placeholder cleaning
- reference-table lookup
- exact string normalization where rules exist
- UOM enforcement
- character-limit checks
- domain allowlisting
- evidence existence checks
- output column ordering
- CSV/XLSX generation
- job status tracking

---

# 7. Recommended Technology Stack

## Frontend

**React + TypeScript**

Purpose:

- CSV upload
- processing progress
- product/result inspection
- evidence display
- review UI
- output download

## Backend

**Python + FastAPI**

Why:

- strong data-processing ecosystem
- easy CSV/PDF/web/AI integration
- fast to implement
- easy to expose APIs

## Database

**PostgreSQL**

Use it for:

- products
- processing jobs
- sources
- evidence
- normalized attributes
- reference/control data

## AI model

### Primary

**Gemini 3.7 Flash**

Use it for agentic orchestration, structured extraction, reasoning, multimodal processing, and controlled content generation.

Gemini 3.7 Flash is currently generally available and supports PDF/image inputs, structured outputs, function calling, search grounding, URL context, File Search, and other relevant capabilities. It is the best current default candidate for this project. [Verify availability in the exact Antigravity environment before final deployment.]

### Cost-optimized secondary model

**Gemini 3.5 Flash-Lite**

Use for lightweight/high-throughput transformations where the stronger model is unnecessary.

Model selection must remain configurable through environment variables rather than hard-coded.

## Web discovery

Use a search/grounding capability for candidate discovery.

**Important rule:**

Search results are discovery inputs.

They are not automatically accepted as product evidence.

Final product evidence must pass:

```text
candidate URL
    ↓
resolve domain
    ↓
compare to approved manufacturer domain
    ↓
official manufacturer source?
    ↓
YES → evidence eligible
NO  → reject
```

## Official webpage processing

Use URL-aware retrieval/HTML extraction for manufacturer product pages.

## PDF/document processing

Use document processing and/or File Search for manufacturer PDFs and large technical documents.

## RAG

Use **Gemini File Search first** rather than immediately building a custom vector database.

Reason:

- simpler implementation
- built-in ingestion/chunking/indexing
- retrieval support
- citation support
- multimodal embedding support
- lower infrastructure burden

If the prototype later needs more control over retrieval, move to **PostgreSQL + pgvector**.

## Vision

Use Gemini multimodal capabilities selectively.

Do not call a VLM on every product image.

Use vision when:

- information is present only visually
- dimensions/labels/diagrams need interpretation
- the image is materially useful for product identification or attributes

## Output

- `pandas`
- `openpyxl`

The output builder must be deterministic.

---

# 8. System Architecture

```text
                           USER
                            │
                            ▼
                     ┌─────────────┐
                     │   React UI  │
                     └──────┬──────┘
                            │
                            ▼
                     ┌─────────────┐
                     │  FastAPI    │
                     └──────┬──────┘
                            │
                            ▼
              ┌───────────────────────────┐
              │ Product Intelligence      │
              │ Orchestrator              │
              └────────────┬──────────────┘
                           │
         ┌─────────────────┼──────────────────┐
         ▼                 ▼                  ▼
 Identity Resolver   Source Retriever    Reference Data
         │                 │                  │
         └──────────┬──────┴──────────────────┘
                    ▼
            Evidence Collection
                    │
                    ▼
          Document / Web Processing
                    │
                    ▼
             RAG / Retrieval
                    │
                    ▼
          Gemini Structured Extraction
                    │
                    ▼
          Normalization + Validation
                    │
                    ▼
            Verified Product Facts
                    │
                    ▼
            Controlled Content Gen
                    │
                    ▼
              Content Validation
                    │
                    ▼
             Asset Mapping Layer
                    │
                    ▼
             Output Row Builder
                    │
                    ▼
                 CSV/XLSX
```

---

# 9. End-to-End Processing Workflow

## Stage 0 — Ingest

Read one input row.

Example:

```text
Mfg_Part_Num = DCB518ASTS06G
Part_Desc = DCB518ASTS06G Diablo 1/2"x18" - Sanding Belt 6pc
E1_Brand = -- Unbranded --
Unilog_Brand = -- No Unilog Brand --
DIB_Brand = -- No DIB Brand --
Part_Manuf = Freud Inc (2435)
```

Store the raw row unchanged.

## Stage 1 — Clean placeholders

Treat values such as:

```text
-- Unbranded --
-- No Unilog Brand --
-- No DIB Brand --
```

as missing signals, not real brand values.

Never use them as evidence.

## Stage 2 — Identity resolution

Input clues:

- MPN
- part description
- usable brand clues
- usable manufacturer clues

Tasks:

1. Build search candidates.
2. Search for exact MPN.
3. Identify candidate manufacturers.
4. Check official manufacturer sources.
5. Compare MPN, product name, type, brand, and specifications.
6. Assign confidence.
7. Accept or send to review.

## Stage 3 — Source discovery

Find:

- exact official product page
- official technical documents
- official manuals
- official catalogs
- official images
- relevant official assets

Prioritize exact manufacturer sources.

## Stage 4 — Source verification

Reject:

- Amazon
- eBay
- distributor sites
- reseller sites
- third-party catalogs
- scraped aggregators

unless the challenge organizers explicitly change the source policy.

## Stage 5 — Evidence extraction

For each relevant fact capture:

```text
attribute
raw_value
normalized_value (later)
source_id
source_url
source_type
evidence_text
page_number (if applicable)
confidence
```

## Stage 6 — Category determination

Determine the product class/path using the input plus retrieved evidence and reference data.

## Stage 7 — Applicable attribute selection

Use the appropriate category LOV/rules.

Do not ask the LLM to invent the attribute list.

## Stage 8 — Structured fact extraction

Use a strict JSON/schema output.

Example:

```json
{
  "product_identity": {
    "manufacturer": "",
    "brand": "",
    "mpn": "",
    "classpath": ""
  },
  "attributes": [
    {
      "label": "Voltage Rating",
      "raw_value": "120 volts",
      "source_url": "",
      "evidence": "",
      "confidence": 0.98
    }
  ]
}
```

## Stage 9 — Normalization

Normalize against reference data:

```text
manufacturer/brand master
LOV
UOM standards
decimal/fraction rules
category-specific rules
```

Do not rely on free-form model memory for controlled values.

## Stage 10 — Deterministic validation

Check:

- exact/canonical manufacturer
- exact/canonical brand
- valid LOV value
- valid UOM
- evidence exists
- source is official
- no unsupported value
- correct character length
- correct formatting
- no invalid schema change

## Stage 11 — Conflict detection

If two official sources disagree:

```text
Source A → 10 kg
Source B → 10.2 kg
```

Do not silently choose.

Create:

```text
status = CONFLICT
needs_review = true
```

A safe hierarchy may be used only when it is explicitly defined by the source/rules. Otherwise send for review.

## Stage 12 — Controlled content generation

Generate descriptions from **verified facts only**.

Never feed only the raw input row to the LLM and ask it to invent a product page.

## Stage 13 — Content validation

Check:

- character limits
- casing
- title structure
- required terminology
- unsupported claims
- unit formatting
- duplicate information
- consistency with structured attributes

## Stage 14 — Asset collection

Map official assets to the correct output fields.

## Stage 15 — Output building

Start from the exact fixed output-header list.

Populate what is supported.

Leave unsupported values blank.

Never rename, reorder, remove, or add final output headers.

## Stage 16 — Export

Provide:

- CSV
- XLSX

with identical logical data.

---

# 10. Hallucination Prevention Strategy

## Absolute rule

> **No evidence = no confident fact.**

### Example

Bad:

```text
AI predicts Weight = 2.5 kg
```

Good:

```text
Weight = 2.5 kg
Source = official manufacturer document
Evidence = exact supporting text
Status = VERIFIED
```

### Evidence-first pipeline

```text
Retrieve
   ↓
Extract candidate fact
   ↓
Attach evidence
   ↓
Normalize
   ↓
Validate
   ↓
Accept / Review / Reject
```

### Never use

```text
LLM output → directly into CSV
```

Use:

```text
LLM output
   ↓
structured object
   ↓
validation engine
   ↓
normalized object
   ↓
CSV/XLSX
```

---

# 11. Reference Data Strategy

Load the supplied reference files into controlled reference tables.

## Core reference categories

### Manufacturer/brand master

Use for:

- canonical manufacturer names
- canonical brand names
- fuzzy matching
- legal casing/symbol rules

### UniCat LOV

Use for:

- applicable attributes
- allowed values
- normalized labels
- normalized values
- category-specific restrictions

### UOM standards

Use for:

- canonical units
- allowed abbreviations
- technical formatting

### Decimal/Fraction mapping

Use for:

- decimal ↔ fraction transformations where the rules require them

### Category-specific reference files

Use for:

- category attribute order
- category value mappings
- category-specific descriptions
- filtering flags
- category terminology

---

# 12. Data Model / Backend Schema

## `processing_jobs`

```text
id                  UUID / primary key
filename            TEXT
total_rows          INTEGER
processed_rows      INTEGER
failed_rows         INTEGER
review_rows         INTEGER
status              TEXT
created_at          TIMESTAMP
completed_at        TIMESTAMP
```

## `products`

```text
id                      UUID / primary key
job_id                  FK → processing_jobs.id
input_row_number        INTEGER

mpn                     TEXT
part_description        TEXT
input_brand             TEXT
input_manufacturer      TEXT

resolved_manufacturer   TEXT
resolved_brand          TEXT
trade_name              TEXT
manufacturer_part_number TEXT
alternate_part_number   TEXT
classpath               TEXT

confidence              NUMERIC
status                  TEXT

raw_input_json          JSONB

created_at              TIMESTAMP
updated_at              TIMESTAMP
```

## `sources`

```text
id                  UUID / primary key
product_id          FK → products.id

url                 TEXT
source_type         TEXT
domain              TEXT
title               TEXT
is_official         BOOLEAN
retrieved_at        TIMESTAMP

content_hash        TEXT
metadata_json       JSONB
```

## `evidence`

```text
id                  UUID / primary key
product_id          FK → products.id
source_id           FK → sources.id

attribute_name      TEXT
raw_value           TEXT
evidence_text       TEXT
page_number         INTEGER NULL

confidence           NUMERIC
validation_status    TEXT

created_at           TIMESTAMP
```

## `attributes`

```text
id                  UUID / primary key
product_id          FK → products.id
evidence_id         FK → evidence.id NULL

label               TEXT
value               TEXT
uom                 TEXT
lov_value           TEXT NULL

confidence           NUMERIC
validation_status    TEXT
```

## Optional `generated_content`

```text
id                  UUID / primary key
product_id          FK → products.id

field_name          TEXT
generated_value     TEXT
validation_status   TEXT
revision             INTEGER
```

## Optional `digital_assets`

```text
id                  UUID / primary key
product_id          FK → products.id

asset_type          TEXT
asset_url           TEXT
local_filename      TEXT NULL
source_id           FK → sources.id
is_official         BOOLEAN
```

---

# 13. Key Data Relationships

```text
processing_jobs
      │
      └──< products
              │
              ├──< sources
              │       └──< evidence
              │
              ├──< attributes
              │       └── evidence_id
              │
              └──< generated_content
```

Evidence is a first-class record.

The product record should never depend on an untraceable LLM response.

---

# 14. Output Schema Mapping

The exact output file contains **252 fixed headers**.

## Group 1 — Source & traceability

Columns 1–6:

```text
MFR URL
Ref URL 1
Ref URL 2
Ref URL 3
Ref URL 4
Ref URL 5
```

Production:

- official source retrieval
- evidence/source ranking
- deterministic header mapping

## Group 2 — Input / pass-through

Columns 7–17:

```text
PART_NUMBER
Dept
Class
Fine
SKU - MY_PART_NUMBER
Mfg_Part_Num
Part_Desc
E1_Brand
Unilog_Brand
DIB_Brand
Part_Manuf
```

Production:

- preserve original input values
- do not regenerate

## Group 3 — Product identity

Columns 18–23:

```text
MANUFACTURER_NAME
BRAND_NAME
TRADE_NAME
MANUFACTURER_PART_NUMBER
ALTERNATE_PART_NUMBER
Classpath
```

Production:

- identity resolution
- official source evidence
- master-data normalization
- deterministic validation

## Group 4 — Commerce content

Columns 24–55:

```text
MOBILE_DESC
INVOICE_DESC
SHORT_DESC
LONG_DESC1
RETAIL_DESC
MARKETING_DESCRIPTION
ITEM_FEATURES_1 ... ITEM_FEATURES_20
With
Standard/Approvals
Prop 65
Application
Includes
Product Name
```

Production:

- verified facts
- content rules
- LLM generation
- deterministic format validation

## Group 5 — Attributes

Columns 56–205:

```text
ATTRIBUTE_LABEL 1
ATTRIBUTE_VALUE 1
ATTRIBUTE_UOM 1
...
ATTRIBUTE_LABEL 50
ATTRIBUTE_VALUE 50
ATTRIBUTE_UOM 50
```

Production:

- category LOV/rules
- evidence extraction
- normalization
- deterministic validation

Important:

**50 attribute slots are a maximum output structure, not an instruction to invent 50 attributes.**

## Group 6 — Commercial / identifiers

Columns 206–214:

```text
UPC
EAN
GTIN
UNSPSC
Warranty
List Price
Selling Qty
Selling UOM
Standard Packaging Information
```

Production:

- manufacturer/official source retrieval where available
- reference data where applicable
- blank when unsupported

## Group 7 — Physical dimensions

Columns 215–224:

```text
LENGTH
LENGTH_UOM
HEIGHT
HEIGHT_UOM
WIDTH
WIDTH_UOM
WEIGHT
WEIGHT_UOM
VOLUME
VOLUME_UOM
```

Production:

- evidence extraction
- numeric normalization
- UOM standards
- fraction/decimal rules where applicable

## Group 8 — Digital assets

Columns 225–249:

```text
Product Image
Alternate Image 1
Alternate Image 2
Alternate Image 3
Alternate Image 4
SDS
SDS_1
Warranty Information
Catalog
Specification Sheet
Instruction/Installation Manual
Service Manual
Owners/User Manual
Line Drawing
MTR
RoHS
Full Engineering Drawing
Energy Star Guide
Technical Bulletin
Submittal
Compatibility Chart
Size Chart
Product Label/Insert
Video Link
Video Link 1
```

Production:

- official manufacturer asset discovery
- asset classification
- URL/file mapping

## Group 9 — Final metadata

Columns 250–252:

```text
Country Of Origin
Discontinued
Actual Image (Yes/No)
```

Production:

- evidence where needed
- deterministic checks where possible

---

# 15. Important Dataset Observations

## Observation A — input manufacturer is not always authoritative

The actual reference output shows cases where the input manufacturer/brand fields do not simply equal the enriched manufacturer/brand.

Therefore:

**Do not copy `Part_Manuf` into `MANUFACTURER_NAME` blindly.**

## Observation B — ground-truth inconsistencies exist

The supplied Solution Guide explicitly warns that some delivery data can contain mismatches and blank fields.

The example output also contains a noteworthy identity/source inconsistency in which an `MFR URL` and the `MANUFACTURER_NAME` do not trivially match.

Therefore:

- do not encode simplistic "URL domain must equal manufacturer string" logic as the only rule
- maintain a separate source-domain field
- track identity/source conflicts
- surface them for review

## Observation C — blank is not always failure

A legitimate blank can mean:

- information was not available
- source did not publish it
- field does not apply
- evidence is insufficient

A blank is preferable to an invented value.

---

# 16. App Flow Document

## Screen 1 — Upload

### Elements

- file picker
- supported format notice
- sample input format preview
- Start Processing button

### Validation

If file is invalid:

```text
Unsupported file structure.
Required field: Mfg_Part_Num
```

If valid:

```text
1,000 rows detected.
252-column output schema loaded.
Ready to process.
```

## Screen 2 — Processing

Show:

```text
Total products
Processed
Verified
Needs Review
Failed
Current product
Overall progress
```

Example:

```text
193 / 1000 processed
171 verified
18 review
4 failed
```

## Screen 3 — Product detail

Display:

### Identity

- MPN
- Manufacturer
- Brand
- Classpath
- Confidence

### Attributes

For each attribute:

```text
Material
Stainless Steel
✓ Verified
Source: Specification PDF
```

### Evidence

Show:

- URL
- source type
- evidence text
- page number where available

### Review state

Allow the user to see why a field requires review.

## Screen 4 — Output preview

Show:

- number of populated fields
- number of blanks
- verified field count
- review field count
- source coverage
- LOV compliance
- UOM compliance

## Screen 5 — Download

Buttons:

- Download CSV
- Download XLSX

---

# 17. UI/UX Design Brief

## Style

Modern B2B/data-product interface.

Avoid:

- excessive gradients
- decorative animations
- large hero sections
- generic SaaS landing-page aesthetics

Prioritize:

- dense but readable data presentation
- evidence visibility
- status clarity
- operational usefulness

## Suggested visual hierarchy

### Left sidebar

- Upload / Jobs
- Products
- Review
- Output
- Settings

### Main workspace

Use cards only where they help.

Primary components:

- progress card
- product result table
- evidence drawer/panel
- attribute table
- confidence/status badges
- download actions

## Status language

Use text plus color/icon, not color alone:

```text
VERIFIED
NEEDS_REVIEW
CONFLICT
NOT_FOUND
FAILED
```

## Responsive behavior

Desktop first because judges will likely use laptops.

Do not sacrifice the product data table for mobile styling.

---

# 18. Agent / Tool Design

Use one primary orchestrator with specialized deterministic tools/functions.

## Tool: `resolve_product_identity`

Input:

```json
{
  "mpn": "",
  "description": "",
  "brand_clues": [],
  "manufacturer_clues": []
}
```

Output:

```json
{
  "manufacturer": "",
  "brand": "",
  "product_name": "",
  "classpath": "",
  "confidence": 0.0,
  "status": ""
}
```

## Tool: `search_official_sources`

Input:

```json
{
  "mpn": "",
  "manufacturer": ""
}
```

Output:

```json
{
  "candidates": [
    {
      "url": "",
      "type": "",
      "domain": ""
    }
  ]
}
```

## Tool: `verify_source_domain`

Input:

```json
{
  "url": "",
  "manufacturer_domain": ""
}
```

Output:

```json
{
  "is_official": true,
  "reason": ""
}
```

## Tool: `extract_source_content`

Input:

```json
{
  "url": "",
  "source_type": ""
}
```

Output:

structured content/evidence candidates.

## Tool: `get_category_schema`

Input:

```json
{
  "classpath": ""
}
```

Output:

applicable labels, allowed values, rules, formatting constraints.

## Tool: `normalize_attribute`

Input:

```json
{
  "label": "",
  "raw_value": "",
  "raw_uom": ""
}
```

Output:

```json
{
  "normalized_value": "",
  "normalized_uom": "",
  "lov_match": true
}
```

## Tool: `validate_attribute`

Input:

```json
{
  "label": "",
  "value": "",
  "uom": "",
  "evidence_id": ""
}
```

Output:

```json
{
  "status": "VERIFIED",
  "reason": ""
}
```

## Tool: `generate_content`

Input:

- verified product facts
- content rules
- category rules

Output:

- only the content fields requested

## Tool: `validate_content`

Check:

- length
- casing
- unsupported claims
- formatting
- consistency with facts

## Tool: `build_output_row`

Input:

- original input
- verified identity
- attributes
- descriptions
- assets
- sources

Output:

- exactly the 252 required columns

---

# 19. Structured LLM Output Contract

Never depend on free-form text.

Minimum extraction schema:

```json
{
  "identity": {
    "manufacturer": {
      "value": "",
      "confidence": 0.0,
      "source_id": ""
    },
    "brand": {
      "value": "",
      "confidence": 0.0,
      "source_id": ""
    },
    "classpath": {
      "value": "",
      "confidence": 0.0,
      "source_id": ""
    }
  },
  "attributes": [
    {
      "label": "",
      "raw_value": "",
      "raw_uom": "",
      "evidence_text": "",
      "source_id": "",
      "page_number": null,
      "confidence": 0.0
    }
  ]
}
```

The model is not allowed to output an attribute without its source/evidence reference.

---

# 20. Evidence and Confidence Rules

## Suggested confidence model

Do not pretend the number is a scientifically calibrated probability.

It is an operational confidence score based on evidence quality.

Possible signals:

```text
exact MPN match
+ official domain
+ direct product page
+ exact attribute phrase
+ category consistency
+ LOV match
+ no source conflict
```

Reduce confidence when:

```text
fuzzy MPN only
source is ambiguous
multiple manufacturers match
source conflict
value inferred rather than directly stated
category mismatch
```

## Recommended status logic

```text
VERIFIED
    if official evidence exists
    and value passes normalization/validation
    and no unresolved conflict

NEEDS_REVIEW
    if evidence is incomplete or confidence is low

CONFLICT
    if trusted official sources disagree

NOT_FOUND
    if the field cannot be supported

FAILED
    if processing itself fails
```

---

# 21. Security and Trust Requirements

## Secrets

All API keys must be stored in environment variables.

Never commit:

- API keys
- service-account credentials
- database passwords
- secrets
- `.env` files containing real secrets

## Input security

Treat uploaded CSVs as untrusted input.

Validate:

- file extension
- MIME/content structure
- size limits
- header structure
- malicious formulas before spreadsheet export where applicable

## URL security

Protect against:

- arbitrary internal URL access
- SSRF
- unsafe redirects
- non-http(s) schemes
- local file URLs

Only retrieve permitted external sources.

## Source policy

Enforce official manufacturer-domain restrictions at the application layer.

Do not trust the model to enforce this alone.

---

# 22. Cost-Control Strategy

## Do not call the strongest model for everything

Use lightweight deterministic operations where possible.

Use the primary model when the task requires reasoning.

Use the lower-cost model for simpler, repetitive operations.

## Avoid unnecessary calls

### Bad

```text
Every row
→ multiple LLM calls
→ multiple VLM calls
→ repeated searches
```

### Better

```text
Identity discovery
→ source reuse
→ retrieve once
→ structured extraction
→ deterministic normalization
→ one content generation pass
```

## Reuse source content

If multiple attributes come from the same product PDF:

- ingest once
- retrieve relevant passages multiple times
- avoid repeatedly downloading the same document

## Cache

Cache:

- normalized manufacturer domains
- source URLs
- downloaded documents
- document hashes
- extraction results where safe
- identical MPN/source combinations

---

# 23. Testing Strategy

## Unit tests

Test:

- placeholder cleaning
- UOM normalization
- fraction conversion
- LOV matching
- manufacturer matching
- character limits
- output-column generation
- source-domain validation

## Integration tests

Test one complete row:

```text
CSV
→ identity
→ search
→ source
→ extraction
→ validation
→ generation
→ output
```

## Adversarial tests

Create cases with:

- wrong manufacturer clue
- missing brand
- ambiguous MPN
- conflicting official sources
- missing PDF
- multiple matching MPNs
- malformed descriptions
- missing attributes
- unsupported UOM
- third-party search results
- product discontinued
- no product image

## Ground-truth evaluation

Use the supplied 200-item ground-truth dataset where available.

Track:

```text
field-level accuracy
LOV match rate
UOM compliance
character-limit compliance
source coverage
identity accuracy
hallucination rate
review rate
average cost
average latency
```

The Solution Guide specifically recommends evaluating against the 200 known-good rows and measuring field-level accuracy, character-limit compliance, and LOV compliance.

---

# 24. Implementation Plan

## Phase 0 — Project setup

Deliverables:

- React frontend
- FastAPI backend
- PostgreSQL
- environment configuration
- base repository structure
- fixed output-header definition

## Phase 1 — Input/output foundation

Build:

- CSV upload
- CSV parser
- input validation
- exact 252-header output builder
- CSV/XLSX export

Before AI.

## Phase 2 — Reference data

Load:

- manufacturer/brand master
- LOV
- UOM
- fraction/decimal mapping
- relevant category reference data

Build lookup services.

## Phase 3 — Product identity

Build:

- MPN search
- candidate selection
- official-source verification
- confidence
- review status

## Phase 4 — Source retrieval

Build:

- official source discovery
- URL validation
- HTML extraction
- PDF ingestion
- source storage
- evidence records

## Phase 5 — Structured extraction

Build:

- category-aware schema retrieval
- structured LLM extraction
- evidence binding
- confidence

## Phase 6 — Normalization + validation

Build:

- LOV matching
- manufacturer/brand matching
- UOM normalization
- conflict detection
- validation status

## Phase 7 — Content generation

Build:

- title
- mobile description
- invoice description
- short description
- long description
- retail description
- features
- other supported fields

Validate every generated field.

## Phase 8 — Digital assets

Build:

- image discovery
- document mapping
- asset naming
- asset URL/reference mapping

## Phase 9 — UI evidence view

Build:

- processing progress
- product detail
- attribute table
- source/evidence drawer
- review view

## Phase 10 — Evaluation

Run:

- sample dataset
- hidden/unseen-style synthetic tests
- ground-truth comparison
- failure analysis
- cost analysis

## Phase 11 — Production-style deployment

Build and verify:

- public frontend deployment
- public backend/API deployment
- managed PostgreSQL connection
- environment/secrets configuration
- CORS/security configuration
- health checks
- file-processing reliability
- download flow
- live smoke test with real input

The deployed system must execute the same dynamic pipeline as development.

## Phase 12 — Demo polish

Only after correctness and deployment:

- UI polish
- performance
- logging
- error messages
- download experience
- demo workflow

---

# 25. Definition of Done

The prototype is considered working only when all conditions below are met.

## Input

- [ ] Accepts actual challenge input CSV.
- [ ] Does not rely on one known product.
- [ ] Handles missing/placeholder fields.

## Retrieval

- [ ] Finds manufacturer sources dynamically.
- [ ] Rejects prohibited third-party evidence.
- [ ] Can process webpages and PDFs.
- [ ] Stores source metadata.

## AI

- [ ] Uses structured model responses.
- [ ] Uses evidence context.
- [ ] Does not directly write final CSV values without validation.
- [ ] Supports confidence/review.

## Reference data

- [ ] LOV is actually queried.
- [ ] UOM rules are actually queried.
- [ ] manufacturer/brand normalization is actually queried.

## Validation

- [ ] Invalid values are rejected.
- [ ] unsupported facts stay blank/review.
- [ ] conflicts are detected.

## Output

- [ ] Exactly 252 headers.
- [ ] No headers renamed.
- [ ] No required header removed.
- [ ] CSV export works.
- [ ] XLSX export works.

## Demo

- [ ] Upload file.
- [ ] Process real rows.
- [ ] Show evidence.
- [ ] Show confidence/status.
- [ ] Download final output.
- [ ] Public hosted URL is accessible without local installation.
- [ ] Hosted application processes real/unseen input dynamically.

---

# 26. Antigravity Build Instructions

## Before coding

Antigravity must:

1. Read this complete document.
2. Inspect all available project files.
3. Inspect the actual input and expected-output CSVs.
4. Preserve the exact 252-column output schema.
5. Identify missing implementation details before coding.
6. Produce a build plan and proposed repository structure.
7. Then implement phase by phase.

## Do NOT

- generate a fake demo
- use mocked product data as the primary workflow
- hard-code MPNs
- hard-code manufacturers
- hard-code sample answers
- hard-code website URLs for individual products
- return a canned JSON result
- bypass reference datasets
- fabricate missing product attributes
- create a separate output schema
- silently replace official sources with third-party sources

## Development principle

Every production-looking result shown in the demo must come from the same dynamic pipeline that processes an uploaded file.

---

# 27. Suggested Repository Structure

```text
unihack-product-intelligence/
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   ├── api/
│   │   └── types/
│   └── package.json
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   │   ├── identity/
│   │   │   ├── retrieval/
│   │   │   ├── extraction/
│   │   │   ├── normalization/
│   │   │   ├── validation/
│   │   │   ├── content/
│   │   │   └── assets/
│   │   ├── db/
│   │   └── output/
│   ├── tests/
│   └── requirements.txt
│
├── reference_data/
│
├── schemas/
│   └── expected_output_headers.json
│
├── data/
│   └── sample/
│
├── docs/
│
├── .env.example
├── README.md
└── docker-compose.yml
```

---

# 28. Recommended Internal Processing Contract

Every product should move through a state machine.

```text
RECEIVED
   ↓
IDENTIFYING
   ↓
SOURCE_DISCOVERY
   ↓
SOURCE_VERIFICATION
   ↓
EVIDENCE_EXTRACTION
   ↓
NORMALIZATION
   ↓
VALIDATION
   ↓
CONTENT_GENERATION
   ↓
CONTENT_VALIDATION
   ↓
OUTPUT_READY
```

Alternate exits:

```text
NEEDS_REVIEW
CONFLICT
FAILED
```

Never bypass the state machine merely to make the UI appear successful.

---

# 29. What Makes This Solution Different

The differentiation is **not**:

> "We use AI."

The differentiation is:

### Evidence-first product intelligence

```text
Discover
   ↓
Extract
   ↓
Normalize
   ↓
Validate
   ↓
Prove
   ↓
Generate
```

### Confidence-aware automation

```text
Strong evidence → automatic acceptance
Weak evidence → human review
Conflicting evidence → conflict state
No evidence → blank/not found
```

### Controlled generation

Descriptions are generated from verified facts, not from the model's world knowledge.

### Dynamic source discovery

The system does not require a hard-coded list of manufacturer URLs for the evaluation dataset.

### Category-aware output

Attributes are driven by controlled category reference data rather than free-form LLM invention.

---

# 30. Important Design Decisions Already Locked

1. **Manufacturer-only evidence.**
2. **Dynamic processing is mandatory.**
3. **AI is selective, not everywhere.**
4. **One orchestration agent, not an agent swarm.**
5. **Evidence is a first-class data object.**
6. **LOV/UOM/reference data is enforced outside the LLM.**
7. **No unsupported value should be silently invented.**
8. **RAG/File Search is used where documents are large or retrieval is needed.**
9. **VLM is optional and invoked only when visual evidence is useful.**
10. **The final output schema is deterministic and fixed.**
11. **Human review is a feature, not a failure state.**
12. **Correctness comes before UI polish.**

---

# 31. Known Ambiguities / Do Not Guess

The following must remain explicit implementation decisions until confirmed by the source files or test behavior:

- Exact character limits for every content field.
- Exact title/description formulas for every category.
- Exact precedence when multiple official sources disagree.
- Exact interpretation of certain commercial fields such as List Price.
- Exact handling of asset filenames vs source URLs.
- Whether all 252 columns must always be populated when evidence does not exist.
- Exact evaluation dataset behavior beyond the supplied sample/ground truth.

When uncertain, prefer:

```text
source evidence
→ supplied rule
→ controlled reference data
→ review
```

over assumptions.

---

# 32. Final Build Philosophy

The prototype should be a **real hosted application**, not a local simulation.

The prototype should look simple to the user:

```text
Upload CSV
   ↓
Process
   ↓
Review
   ↓
Download
```

But internally it should be disciplined:

```text
Input
→ identity
→ official evidence
→ structured extraction
→ controlled normalization
→ deterministic validation
→ controlled generation
→ provenance
→ fixed-schema export
```

The goal is not to make the LLM look intelligent.

The goal is to make the **data trustworthy**.

---

# 33. Source / Reference Notes

This blueprint is grounded in:

- UniHack problem statement supplied in the conversation.
- UniHack Solution Guide supplied in the conversation.
- Actual supplied 1,000-row input CSV.
- Actual supplied 252-column Expected Output / Delivery Format CSV.
- Supplied "6 Documents You Should Create Before Vibe Coding Any App" methodology document.
- Current official Google Gemini API documentation was used only to keep the recommended model/tooling choices current at the time this blueprint was created.



# Appendix A — Exact 252-Column Output Header Registry

The following is the authoritative header order derived directly from the supplied Expected Output CSV. The implementation must use this list as the single source of truth.

## Source & Traceability — Columns 1–6

1. `MFR URL`
2. `Ref URL 1`
3. `Ref URL 2`
4. `Ref URL 3`
5. `Ref URL 4`
6. `Ref URL 5`

## Input / Pass-through — Columns 7–17

7. `PART_NUMBER`
8. `Dept`
9. `Class`
10. `Fine`
11. `SKU - MY_PART_NUMBER`
12. `Mfg_Part_Num`
13. `Part_Desc`
14. `E1_Brand`
15. `Unilog_Brand`
16. `DIB_Brand`
17. `Part_Manuf`

## Product Identity & Classification — Columns 18–23

18. `MANUFACTURER_NAME`
19. `BRAND_NAME`
20. `TRADE_NAME`
21. `MANUFACTURER_PART_NUMBER`
22. `ALTERNATE_PART_NUMBER`
23. `Classpath`

## Commerce Content — Columns 24–55

24. `MOBILE_DESC`
25. `INVOICE_DESC`
26. `SHORT_DESC`
27. `LONG_DESC1`
28. `RETAIL_DESC`
29. `MARKETING_DESCRIPTION`
30. `ITEM_FEATURES_1`
31. `ITEM_FEATURES_2`
32. `ITEM_FEATURES_3`
33. `ITEM_FEATURES_4`
34. `ITEM_FEATURES_5`
35. `ITEM_FEATURES_6`
36. `ITEM_FEATURES_7`
37. `ITEM_FEATURES_8`
38. `ITEM_FEATURES_9`
39. `ITEM_FEATURES_10`
40. `ITEM_FEATURES_11`
41. `ITEM_FEATURES_12`
42. `ITEM_FEATURES_13`
43. `ITEM_FEATURES_14`
44. `ITEM_FEATURES_15`
45. `ITEM_FEATURES_16`
46. `ITEM_FEATURES_17`
47. `ITEM_FEATURES_18`
48. `ITEM_FEATURES_19`
49. `ITEM_FEATURES_20`
50. `With`
51. `Standard/Approvals`
52. `Prop 65`
53. `Application`
54. `Includes`
55. `Product Name`

## Attribute Triples (50 slots) — Columns 56–205

56. `ATTRIBUTE_LABEL 1`
57. `ATTRIBUTE_VALUE 1`
58. `ATTRIBUTE_UOM 1`
59. `ATTRIBUTE_LABEL 2`
60. `ATTRIBUTE_VALUE 2`
61. `ATTRIBUTE_UOM 2`
62. `ATTRIBUTE_LABEL 3`
63. `ATTRIBUTE_VALUE 3`
64. `ATTRIBUTE_UOM 3`
65. `ATTRIBUTE_LABEL 4`
66. `ATTRIBUTE_VALUE 4`
67. `ATTRIBUTE_UOM 4`
68. `ATTRIBUTE_LABEL 5`
69. `ATTRIBUTE_VALUE 5`
70. `ATTRIBUTE_UOM 5`
71. `ATTRIBUTE_LABEL 6`
72. `ATTRIBUTE_VALUE 6`
73. `ATTRIBUTE_UOM 6`
74. `ATTRIBUTE_LABEL 7`
75. `ATTRIBUTE_VALUE 7`
76. `ATTRIBUTE_UOM 7`
77. `ATTRIBUTE_LABEL 8`
78. `ATTRIBUTE_VALUE 8`
79. `ATTRIBUTE_UOM 8`
80. `ATTRIBUTE_LABEL 9`
81. `ATTRIBUTE_VALUE 9`
82. `ATTRIBUTE_UOM 9`
83. `ATTRIBUTE_LABEL 10`
84. `ATTRIBUTE_VALUE 10`
85. `ATTRIBUTE_UOM 10`
86. `ATTRIBUTE_LABEL 11`
87. `ATTRIBUTE_VALUE 11`
88. `ATTRIBUTE_UOM 11`
89. `ATTRIBUTE_LABEL 12`
90. `ATTRIBUTE_VALUE 12`
91. `ATTRIBUTE_UOM 12`
92. `ATTRIBUTE_LABEL 13`
93. `ATTRIBUTE_VALUE 13`
94. `ATTRIBUTE_UOM 13`
95. `ATTRIBUTE_LABEL 14`
96. `ATTRIBUTE_VALUE 14`
97. `ATTRIBUTE_UOM 14`
98. `ATTRIBUTE_LABEL 15`
99. `ATTRIBUTE_VALUE 15`
100. `ATTRIBUTE_UOM 15`
101. `ATTRIBUTE_LABEL 16`
102. `ATTRIBUTE_VALUE 16`
103. `ATTRIBUTE_UOM 16`
104. `ATTRIBUTE_LABEL 17`
105. `ATTRIBUTE_VALUE 17`
106. `ATTRIBUTE_UOM 17`
107. `ATTRIBUTE_LABEL 18`
108. `ATTRIBUTE_VALUE 18`
109. `ATTRIBUTE_UOM 18`
110. `ATTRIBUTE_LABEL 19`
111. `ATTRIBUTE_VALUE 19`
112. `ATTRIBUTE_UOM 19`
113. `ATTRIBUTE_LABEL 20`
114. `ATTRIBUTE_VALUE 20`
115. `ATTRIBUTE_UOM 20`
116. `ATTRIBUTE_LABEL 21`
117. `ATTRIBUTE_VALUE 21`
118. `ATTRIBUTE_UOM 21`
119. `ATTRIBUTE_LABEL 22`
120. `ATTRIBUTE_VALUE 22`
121. `ATTRIBUTE_UOM 22`
122. `ATTRIBUTE_LABEL 23`
123. `ATTRIBUTE_VALUE 23`
124. `ATTRIBUTE_UOM 23`
125. `ATTRIBUTE_LABEL 24`
126. `ATTRIBUTE_VALUE 24`
127. `ATTRIBUTE_UOM 24`
128. `ATTRIBUTE_LABEL 25`
129. `ATTRIBUTE_VALUE 25`
130. `ATTRIBUTE_UOM 25`
131. `ATTRIBUTE_LABEL 26`
132. `ATTRIBUTE_VALUE 26`
133. `ATTRIBUTE_UOM 26`
134. `ATTRIBUTE_LABEL 27`
135. `ATTRIBUTE_VALUE 27`
136. `ATTRIBUTE_UOM 27`
137. `ATTRIBUTE_LABEL 28`
138. `ATTRIBUTE_VALUE 28`
139. `ATTRIBUTE_UOM 28`
140. `ATTRIBUTE_LABEL 29`
141. `ATTRIBUTE_VALUE 29`
142. `ATTRIBUTE_UOM 29`
143. `ATTRIBUTE_LABEL 30`
144. `ATTRIBUTE_VALUE 30`
145. `ATTRIBUTE_UOM 30`
146. `ATTRIBUTE_LABEL 31`
147. `ATTRIBUTE_VALUE 31`
148. `ATTRIBUTE_UOM 31`
149. `ATTRIBUTE_LABEL 32`
150. `ATTRIBUTE_VALUE 32`
151. `ATTRIBUTE_UOM 32`
152. `ATTRIBUTE_LABEL 33`
153. `ATTRIBUTE_VALUE 33`
154. `ATTRIBUTE_UOM 33`
155. `ATTRIBUTE_LABEL 34`
156. `ATTRIBUTE_VALUE 34`
157. `ATTRIBUTE_UOM 34`
158. `ATTRIBUTE_LABEL 35`
159. `ATTRIBUTE_VALUE 35`
160. `ATTRIBUTE_UOM 35`
161. `ATTRIBUTE_LABEL 36`
162. `ATTRIBUTE_VALUE 36`
163. `ATTRIBUTE_UOM 36`
164. `ATTRIBUTE_LABEL 37`
165. `ATTRIBUTE_VALUE 37`
166. `ATTRIBUTE_UOM 37`
167. `ATTRIBUTE_LABEL 38`
168. `ATTRIBUTE_VALUE 38`
169. `ATTRIBUTE_UOM 38`
170. `ATTRIBUTE_LABEL 39`
171. `ATTRIBUTE_VALUE 39`
172. `ATTRIBUTE_UOM 39`
173. `ATTRIBUTE_LABEL 40`
174. `ATTRIBUTE_VALUE 40`
175. `ATTRIBUTE_UOM 40`
176. `ATTRIBUTE_LABEL 41`
177. `ATTRIBUTE_VALUE 41`
178. `ATTRIBUTE_UOM 41`
179. `ATTRIBUTE_LABEL 42`
180. `ATTRIBUTE_VALUE 42`
181. `ATTRIBUTE_UOM 42`
182. `ATTRIBUTE_LABEL 43`
183. `ATTRIBUTE_VALUE 43`
184. `ATTRIBUTE_UOM 43`
185. `ATTRIBUTE_LABEL 44`
186. `ATTRIBUTE_VALUE 44`
187. `ATTRIBUTE_UOM 44`
188. `ATTRIBUTE_LABEL 45`
189. `ATTRIBUTE_VALUE 45`
190. `ATTRIBUTE_UOM 45`
191. `ATTRIBUTE_LABEL 46`
192. `ATTRIBUTE_VALUE 46`
193. `ATTRIBUTE_UOM 46`
194. `ATTRIBUTE_LABEL 47`
195. `ATTRIBUTE_VALUE 47`
196. `ATTRIBUTE_UOM 47`
197. `ATTRIBUTE_LABEL 48`
198. `ATTRIBUTE_VALUE 48`
199. `ATTRIBUTE_UOM 48`
200. `ATTRIBUTE_LABEL 49`
201. `ATTRIBUTE_VALUE 49`
202. `ATTRIBUTE_UOM 49`
203. `ATTRIBUTE_LABEL 50`
204. `ATTRIBUTE_VALUE 50`
205. `ATTRIBUTE_UOM 50`

## Commercial / Identifiers — Columns 206–214

206. `UPC`
207. `EAN`
208. `GTIN`
209. `UNSPSC`
210. `Warranty`
211. `List Price`
212. `Selling Qty`
213. `Selling UOM`
214. `Standard Packaging Information`

## Physical Dimensions — Columns 215–224

215. `LENGTH`
216. `LENGTH_UOM`
217. `HEIGHT`
218. `HEIGHT_UOM`
219. `WIDTH`
220. `WIDTH_UOM`
221. `WEIGHT`
222. `WEIGHT_UOM`
223. `VOLUME`
224. `VOLUME_UOM`

## Digital Assets — Columns 225–249

225. `Product Image`
226. `Alternate Image 1`
227. `Alternate Image 2`
228. `Alternate Image 3`
229. `Alternate Image 4`
230. `SDS`
231. `SDS_1`
232. `Warranty Information`
233. `Catalog`
234. `Specification Sheet`
235. `Instruction/Installation Manual`
236. `Service Manual`
237. `Owners/User Manual`
238. `Line Drawing`
239. `MTR`
240. `RoHS`
241. `Full Engineering Drawing`
242. `Energy Star Guide`
243. `Technical Bulletin`
244. `Submittal`
245. `Compatibility Chart`
246. `Size Chart`
247. `Product Label/Insert`
248. `Video Link`
249. `Video Link 1`

## Final Metadata — Columns 250–252

250. `Country Of Origin`
251. `Discontinued`
252. `Actual Image (Yes/No)`


# Appendix B — Reference Input/Output Examples

## Actual sample input row

```text
DCB518ASTS06G
DCB518ASTS06G Diablo 1/2"x18" - Sanding Belt 6pc
-- Unbranded --
-- No Unilog Brand --
-- No DIB Brand --
Freud Inc (2435)
```

## Expected-output interpretation

The supplied Delivery Format examples demonstrate that a single short input row can be enriched into:

- resolved manufacturer/brand
- classpath
- multiple descriptions
- structured attributes
- commercial/identifier fields where available
- physical dimensions where available
- official images/documents
- source URLs

But the examples also contain blanks and at least one identity/source inconsistency. The pipeline must therefore support uncertainty and review instead of assuming every field is deterministically known.

---

# Appendix C — First Implementation Prompt for Antigravity

Use this prompt **after providing this entire document to the coding agent**:

> Read the full UniHack Product Intelligence Project Blueprint.
>
> Do not start coding immediately.
>
> First:
>
> 1. Summarize the architecture you understood.
> 2. Inspect the repository and all available input/reference files.
> 3. Verify the exact input CSV structure and exact 252-column output schema.
> 4. Identify any contradictions or missing details in the specification.
> 5. Propose the repository structure and implementation phases.
> 6. Identify which parts must be deterministic and which parts use AI.
> 7. Explain how manufacturer-only source enforcement will work.
> 8. Explain how evidence will be attached to extracted attributes.
> 9. Explain how the fixed 252-column output will be generated without hallucinating missing values.
>
> Do not build a mocked simulation.
>
> Do not hard-code sample MPNs, manufacturers, or URLs.
>
> Do not rename or remove output headers.
>
> After the plan is approved, implement phase by phase and test each phase before continuing.

# Appendix D — Non-Negotiable Acceptance Rule

A feature is not considered complete merely because the UI shows a plausible result.

A feature is complete only when:

```text
real input
→ real processing
→ real evidence
→ real validation
→ real output
```

works end-to-end.
