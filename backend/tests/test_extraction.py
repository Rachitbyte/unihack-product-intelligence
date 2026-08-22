import os
from unittest.mock import patch, MagicMock
from app.schemas.schemas import ProductRow, IdentityResult
from app.services.extraction import extraction_service

def test_offline_extraction():
    # Setup offline row with retrieved content
    row = ProductRow(
        row_id=1,
        mfg_part_num="TEST-123",
        retrieved_content="The TEST-123 is a heavy duty tool weighing 5.5 lbs. Material: Brass.",
        identity=IdentityResult(official_source_url="https://test.com/product")
    )
    
    mock_response = MagicMock()
    mock_response.text = '''```json
{
  "status": "SUCCESS",
  "reasoning": "Extracted weight and material.",
  "facts": [
    {
      "attribute": "Weight",
      "raw_value": "5.5 lbs",
      "evidence_text": "weighing 5.5 lbs",
      "confidence": 0.95
    },
    {
      "attribute": "Material",
      "raw_value": "Brass",
      "evidence_text": "Material: Brass",
      "confidence": 0.99
    }
  ]
}
```'''
    
    # We patch the model generation
    # And temporarily bypass the self.model check
    extraction_service.model = MagicMock()
    with patch.object(extraction_service.model, 'generate_content', return_value=mock_response):
        result = extraction_service.extract(row)
            
    assert result.status == "SUCCESS"
    assert len(result.facts) == 2
    
    # Test evidence binding
    assert result.facts[0].attribute == "Weight"
    assert result.facts[0].raw_value == "5.5 lbs"
    assert result.facts[0].evidence_text == "weighing 5.5 lbs"
    assert result.facts[0].source_url == "https://test.com/product"
    assert result.facts[0].source_type == "HTML"
    
    print("Offline extraction test passed!")

def test_missing_content():
    row = ProductRow(row_id=1, mfg_part_num="TEST-123", retrieved_content=None)
    extraction_service.model = MagicMock()
    result = extraction_service.extract(row)
    assert result.status == "FAILED"
    assert "No source content" in result.reasoning
    print("Missing content test passed!")

if __name__ == "__main__":
    test_offline_extraction()
    test_missing_content()
