import os
from dotenv import load_dotenv
load_dotenv(dotenv_path="../.env")

import asyncio
from app.schemas.schemas import ProductRow
from app.services.identity import identity_resolver
from app.services.retrieval import retrieval_service
from app.services.extraction import extraction_service
from app.services.normalization import normalization_service
from app.services.content_generation import content_generation_service
from app.services.output_builder import map_to_output, load_expected_headers

def debug_custom_rows():
    from app.services.ingestion import parse_input_csv
    
    import duckduckgo_search
    OriginalDDGS = duckduckgo_search.DDGS
    
    # Mock DDGS to bypass rate limit ONLY for the 3M row
    class MockDDGS(OriginalDDGS):
        def text(self, query, max_results=5, **kwargs):
            if "3MABR-7100075678" in query:
                return [{"href": "https://www.3m.com/3M/en_US/p/d/b40065600/", "title": "3M 775L Stikit Film P150", "body": "3M 775L Stikit Film P150 - Cubitron II 50 Disc/Box 3MABR-7100075678"}]
            return super().text(query, max_results=max_results, **kwargs)
            
    import app.services.identity
    app.services.identity.DDGS = MockDDGS
    
    with open("../test_25.csv", "r", encoding="utf-8") as f:
        content = f.read()
    rows, errors = parse_input_csv(content)
    
    target_mpns = ["DCB518ASTS06G", "3MABR-7100075678", "5B-332-080", "49-94-0013", "DBDS14125G01F"]
    
    for row in rows:
        if row.mfg_part_num not in target_mpns:
            continue
            
        print(f"\n===========================================")
        print(f"TESTING ROW: {row.mfg_part_num}")
        print(f"===========================================")
        print(f"Input: Manuf='{row.part_manuf}', Brand='{row.e1_brand}', Desc='{row.part_desc}'")
        
        # 1. Identity
        try:
            row.identity = identity_resolver.resolve(row)
            resolved_clue = identity_resolver._resolve_true_manufacturer(row)
            print(f"Resolved manufacturer: {resolved_clue}")
            print(f"Selected official source: {row.identity.official_source_url if row.identity else 'None'}")
            print(f"Discovery Status: {row.identity.status if row.identity else 'None'}")
        except Exception as e:
            print(f"Exception in identity: {e}")
            continue

        # 2. Retrieval
        retrieved_source = None
        if row.identity and row.identity.official_source_url:
            try:
                retrieved_source = retrieval_service.fetch_source(row.identity)
                if retrieved_source:
                    print(f"Retrieval result: status_code={retrieved_source.status_code}, length={len(retrieved_source.content)}")
                    print(f"Identity Status updated to: {row.identity.status}")
                else:
                    print(f"Retrieval result: None returned")
            except Exception as e:
                print(f"Exception in retrieval: {e}")

        # 3. Extraction
        if retrieved_source and retrieved_source.content:
            row.retrieved_content = retrieved_source.content
            try:
                row.extraction = extraction_service.extract(row)
                if row.extraction:
                    print(f"Extracted facts: {len(row.extraction.facts) if row.extraction.facts else 0}")
                    for fact in row.extraction.facts:
                        print(f"  - {fact.attribute}: {fact.raw_value} (Evidence: {fact.evidence_text[:50]}...)")
                else:
                    print("Extracted facts: 0")
            except Exception as e:
                print(f"Exception in extraction: {e}")
        else:
            print("Extraction skipped (no content).")
            
        # 4-6. Rest of pipeline
        try:
            normalization_service.normalize(row)
            row.content = content_generation_service.generate(row)
        except:
            pass
            
        # 7. Output Builder
        try:
            headers = load_expected_headers()
            output_rows = map_to_output([row], headers)
            non_empty_keys = {k: v for k, v in output_rows[0].items() if v}
            print(f"\nFinal output fields (populated):")
            for k, v in non_empty_keys.items():
                if k not in ["SKU - MY_PART_NUMBER", "PART_NUMBER", "MANUFACTURER_PART_NUMBER"]:
                    print(f"  {k}: {v}")
        except Exception as e:
            print(f"Exception in output mapping: {e}")

if __name__ == "__main__":
    debug_custom_rows()
