import os
from app.schemas.schemas import ProductRow
from app.services.identity import identity_resolver

def test_identity_live():
    # Only run this test if an explicit live flag is passed or we want to test live
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY not found. Skipping live test.")
        return

    print("Running LIVE Gemini Identity Resolution Test...")
    
    row = ProductRow(
        row_id=1,
        mfg_part_num="DCB518ASTS06G",
        part_desc="Diablo 1/2\"x18\" - Sanding Belt 6pc",
        part_manuf="Freud Inc (2435)"
    )

    result = identity_resolver.resolve(row)

    print("--- LIVE Identity Resolution Result ---")
    print(f"Candidate Manufacturer: {result.candidate_manufacturer}")
    print(f"Candidate Brand: {result.candidate_brand}")
    print(f"Candidate Product: {result.candidate_product_name}")
    print(f"Confidence: {result.confidence}")
    print(f"Status: {result.status}")
    print(f"Official URL: {result.official_source_url}")
    print(f"Matched Evidence: {result.matched_evidence_text}")

    assert result.status in ["VERIFIED", "NEEDS_REVIEW", "CONFLICT", "FAILED"]

if __name__ == "__main__":
    test_identity_live()
