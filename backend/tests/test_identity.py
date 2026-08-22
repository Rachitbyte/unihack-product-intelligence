import os
from unittest.mock import patch, MagicMock
from app.schemas.schemas import ProductRow
from app.services.identity import identity_resolver

def test_identity_resolution():
    row = ProductRow(
        row_id=1,
        mfg_part_num="DCB518ASTS06G",
        part_desc="Diablo 1/2\"x18\" - Sanding Belt 6pc",
        part_manuf="Freud Inc (2435)"
    )

    # If no API key is present, we will mock the model response
    # just to test the logic flow
    if not os.environ.get("GEMINI_API_KEY"):
        print("No GEMINI_API_KEY found, mocking the AI response...")
        mock_response = MagicMock()
        mock_response.text = '''```json
{
  "candidate_manufacturer": "Freud",
  "candidate_brand": "Diablo",
  "candidate_product_name": "Diablo 1/2 in. x 18 in. Sanding Belt (6-Piece)",
  "candidate_classpath": "Abrasives / Sanding Belts",
  "urls": [
    {
      "url": "https://www.diablotools.com/products/DCB518ASTS06G",
      "snippet": "DCB518ASTS06G Diablo Sanding Belt",
      "has_mpn": true
    }
  ]
}
```'''
        # We also need to patch the GEMINI_API_KEY check in identity.py
        with patch('app.services.identity.GEMINI_API_KEY', 'mocked_key'):
            with patch.object(identity_resolver.model, 'generate_content', return_value=mock_response):
                result = identity_resolver.resolve(row)
    else:
        print("Using real Gemini API...")
        result = identity_resolver.resolve(row)

    print("--- Identity Resolution Result ---")
    print(f"Candidate Manufacturer: {result.candidate_manufacturer}")
    print(f"Candidate Brand: {result.candidate_brand}")
    print(f"Candidate Product: {result.candidate_product_name}")
    print(f"Confidence: {result.confidence}")
    print(f"Status: {result.status}")
    print(f"Official URL: {result.official_source_url}")
    print(f"Matched Evidence: {result.matched_evidence_text}")

    assert result.status in ["VERIFIED", "NEEDS_REVIEW", "CONFLICT", "FAILED"]
    if result.status == "VERIFIED":
        assert result.confidence > 0.8
        assert result.official_source_url != ""

if __name__ == "__main__":
    test_identity_resolution()
