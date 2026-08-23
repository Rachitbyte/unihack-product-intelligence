import os
import sys
import logging
from dotenv import load_dotenv
load_dotenv()

from app.services.ingestion import parse_input_csv
from app.services.pipeline import process_product_row
from app.services.output_builder import load_expected_headers, map_to_output, export_to_csv

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def main():
    if len(sys.argv) < 2:
        print("Usage: python run_eval.py <csv_file>")
        return
        
    input_file = sys.argv[1]
    
    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()
        
    rows, errors = parse_input_csv(content)
    print(f"Parsed {len(rows)} rows from {input_file}")
    
    # Metrics
    metrics = {
        "discovery_attempted": 0,
        "discovery_success": 0,
        "discovery_failed": 0,
        "manufacturer_found_product_not_found": 0,
        "needs_review": 0,
        "retrieval_success": 0,
        "extraction_success": 0
    }
    
    processed_rows = []
    enriched_examples = []
    
    for idx, row in enumerate(rows):
        print(f"Processing row {idx+1}/{len(rows)}: {row.mfg_part_num}")
        
        # We process manually to track step by step or let pipeline do it and check results
        metrics["discovery_attempted"] += 1
        
        row = process_product_row(row)
        
        # Update metrics based on row state
        if row.identity:
            status = row.identity.status
            if status in ["OFFICIAL_SOURCE_FOUND", "OFFICIAL_DOCUMENT_FOUND", "OFFICIAL_SOURCE_BLOCKED"]:
                metrics["discovery_success"] += 1
            elif status == "DISCOVERY_FAILED":
                metrics["discovery_failed"] += 1
            elif status == "MANUFACTURER_FOUND_PRODUCT_NOT_FOUND":
                metrics["manufacturer_found_product_not_found"] += 1
            elif status == "NEEDS_REVIEW":
                metrics["needs_review"] += 1
                
        if row.retrieved_content:
            metrics["retrieval_success"] += 1
            
        if row.extraction and row.extraction.facts:
            metrics["extraction_success"] += 1
            if len(enriched_examples) < 5:
                enriched_examples.append(row)
                
        processed_rows.append(row)
        
    print("\n--- METRICS ---")
    for k, v in metrics.items():
        print(f"{k}: {v}")
        
    print(f"\n--- ENRICHED EXAMPLES ({len(enriched_examples)}) ---")
    for r in enriched_examples:
        print(f"\nMPN: {r.mfg_part_num}")
        print(f"Desc: {r.part_desc}")
        print(f"Identity Status: {r.identity.status if r.identity else 'N/A'}")
        print(f"URL: {r.identity.official_source_url if r.identity else 'N/A'}")
        print("Extracted Facts:")
        if r.extraction and r.extraction.facts:
            for f in r.extraction.facts[:3]:
                print(f"  - {f.attribute}: {f.raw_value}")
        if r.content:
            print(f"Generated Content Keys: {list(r.content.dict().keys())[:3]}")

if __name__ == "__main__":
    main()
