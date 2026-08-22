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
  "resolved_manufacturer": "Freud",
  "resolved_brand": "Diablo",
  "resolved_product_name": "Diablo 1/2 in. x 18 in. Sanding Belt (6-Piece)",
  "resolved_classpath": "Abrasives / Sanding Belts",
  "confidence": 0.95,
  "status": "VERIFIED",
  "evidence_urls": ["https://www.diablotools.com/products/DCB518ASTS06G"],
  "reasoning": "Official Diablo/Freud page matches MPN and Description."
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
    print(f"Manufacturer: {result.resolved_manufacturer}")
    print(f"Brand: {result.resolved_brand}")
    print(f"Product: {result.resolved_product_name}")
    print(f"Confidence: {result.confidence}")
    print(f"Status: {result.status}")
    print(f"URLs: {result.evidence_urls}")
    print(f"Reasoning: {result.reasoning}")

    assert result.status in ["VERIFIED", "NEEDS_REVIEW", "CONFLICT", "FAILED"]
    if result.status == "VERIFIED":
        assert result.confidence > 0.8
        assert len(result.evidence_urls) > 0

if __name__ == "__main__":
    test_identity_resolution()
