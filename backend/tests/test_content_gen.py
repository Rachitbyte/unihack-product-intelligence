from unittest.mock import patch, MagicMock
from app.schemas.schemas import ProductRow, ExtractionResult, ExtractedFact
from app.services.content_generation import content_generation_service

def _create_test_row(facts):
    return ProductRow(
        row_id=1,
        mfg_part_num="TEST-123",
        extraction=ExtractionResult(facts=facts)
    )

def test_content_generation_scope():
    print("Testing content generation constraints...")
    
    # 1. NOT_VALIDATED_REFERENCE_DATA_MISSING facts are NOT passed to content generation
    # 2. Invalid facts are excluded
    # Only VALIDATED is used.
    
    facts = [
        ExtractedFact(attribute="ValidFact", raw_value="V1", normalized_value="V1", is_valid=True, validation_status="VALIDATED", evidence_text="", source_id="", source_url="", source_type="", confidence=1.0),
        ExtractedFact(attribute="MissingRef", raw_value="V2", normalized_value="V2", is_valid=True, validation_status="NOT_VALIDATED_REFERENCE_DATA_MISSING", evidence_text="", source_id="", source_url="", source_type="", confidence=1.0),
        ExtractedFact(attribute="InvalidFact", raw_value="V3", normalized_value="V3", is_valid=False, validation_status="NEEDS_REVIEW", evidence_text="", source_id="", source_url="", source_type="", confidence=1.0)
    ]
    
    row = _create_test_row(facts)
    
    mock_response = MagicMock()
    mock_response.text = '''```json
{
  "marketing_description": "Mocked",
  "short_description": "Mocked",
  "item_features": ["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12", "F13", "F14", "F15", "F16", "F17", "F18", "F19", "F20", "F21"]
}
```'''
    
    content_generation_service.model = MagicMock()
    with patch.object(content_generation_service.model, 'generate_content', return_value=mock_response) as mock_gen:
        result = content_generation_service.generate(row)
        
        # Check that prompt only received the VALIDATED fact
        prompt_arg = mock_gen.call_args[0][0]
        assert "ValidFact" in prompt_arg
        assert "MissingRef" not in prompt_arg
        assert "InvalidFact" not in prompt_arg
        
        # 3. Maximum 20 feature bullets is enforced
        assert len(result.item_features) == 20
        assert "F21" not in result.item_features
        
    print("Content generation tests passed!")

if __name__ == "__main__":
    test_content_generation_scope()
