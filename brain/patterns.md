# Patterns

## Coding Conventions
- **Evidence-First:** AI proposes and understands; evidence proves; reference data standardizes; deterministic rules validate. No evidence = no confident fact.
- **Agent Design:** Single orchestration agent calling strict specialized deterministic tools. No agent swarm.
- **LLM Usage:** LLMs are used for reasoning, extraction, and generation. They are NOT used for schema formatting, deterministic normalization (e.g., UOM conversion), validation, or CSV generation. Model selection via environment variables.
- **Security:** API keys and credentials handled securely via environment variables.

## File & Structure
- **Backend Services:** Separated by functional domain (`identity`, `retrieval`, `extraction`, `normalization`, `validation`, `content`, `assets`).
- **Data Flow:** Strictly controlled transitions through product state enum (`RECEIVED`, `IDENTIFYING`, etc.).

## Error Handling
- **Review and Conflict States:** `NEEDS_REVIEW` and `CONFLICT` are legitimate states, not fatal exceptions. Blank fields are preferred over hallucinations.
- **Failures:** Hard failures trigger `FAILED` status, logging exceptions without crashing the pipeline.
