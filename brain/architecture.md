# Architecture

## Tech Stack
- **Frontend:** React + TypeScript
- **Backend:** Python + FastAPI
- **Database:** PostgreSQL (with potential pgvector if required later)
- **AI Models:** Gemini 3.7 Flash (Primary/Reasoning) & Gemini 3.5 Flash-Lite (High-throughput/Simple tasks)

## Folder Structure
```text
unihack-product-intelligence/
├── frontend/
│   ├── src/ (pages, components, api, types)
│   └── package.json
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/ (identity, retrieval, extraction, normalization, validation, content, assets)
│   │   ├── db/
│   │   └── output/
│   ├── tests/
│   └── requirements.txt
├── reference_data/
├── schemas/
├── data/
├── brain/
└── docker-compose.yml
```

## How Components Connect
- **React UI** communicates with **FastAPI Backend** via REST APIs.
- **FastAPI Backend** triggers the **Product Intelligence Orchestrator**.
- The Orchestrator drives products through a strict state machine: `RECEIVED -> IDENTIFYING -> SOURCE_DISCOVERY -> SOURCE_VERIFICATION -> EVIDENCE_EXTRACTION -> NORMALIZATION -> VALIDATION -> CONTENT_GENERATION -> CONTENT_VALIDATION -> OUTPUT_READY`.
- **Database** acts as the definitive store for products, jobs, sources, evidence, generated content, and reference data.

## Key API Contracts
- Data flow is strongly typed.
- LLM output follows strict JSON schema contracts requiring evidence binding.
- Final output builder is strictly deterministic mapped to the exact 252-column schema.
