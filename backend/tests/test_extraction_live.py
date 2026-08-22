import os
from dotenv import load_dotenv
from app.schemas.schemas import ProductRow, IdentityResult

# Load environment variables from .env
load_dotenv()

from app.services.extraction import extraction_service

def test_live_extraction():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY not found. Skipping live test.")
        return

    print("Running LIVE Gemini Extraction Test...")
    
    row = ProductRow(
        row_id=1,
        mfg_part_num="DCB518ASTS06G",
        retrieved_content="""
        Diablo 1/2 in. x 18 in. Sanding Belt (6-Piece).
        Brand: Diablo.
        Material: Premium Zirconium Blend.
        Length: 18 inches.
        Width: 1/2 inch.
        Ideal for: Wood, Metal, Plastics.
        """,
        identity=IdentityResult(official_source_url="https://www.diablotools.com/products/DCB518ASTS06G")
    )

    result = extraction_service.extract(row)

    print("--- LIVE Extraction Result ---")
    print(f"Status: {result.status}")
    print(f"Reasoning: {result.reasoning}")
    
    for fact in result.facts:
        print(f"[{fact.attribute}] {fact.raw_value} (Evidence: '{fact.evidence_text}') - Conf: {fact.confidence}")

    if result.status == "FAILED" and "429 API/Quota Failure" in result.reasoning:
        print("Gracefully handled 429 Quota Exceeded error.")
        assert len(result.facts) == 0

if __name__ == "__main__":
    test_live_extraction()
