from app.schemas.schemas import ProductRow, ExtractionResult, ExtractedFact
from app.services.output_builder import map_to_output, load_expected_headers

def test_output_builder_rules():
    print("Testing Output Builder Constraints...")
    headers = load_expected_headers()
    
    # Create facts
    facts = [
        # 4. Weight maps only to WEIGHT / WEIGHT_UOM
        ExtractedFact(attribute="Weight", raw_value="5.5 lbs", normalized_value="5.5 Pounds", is_valid=True, validation_status="VALIDATED", evidence_text="", source_id="", source_url="", source_type="", confidence=1.0),
        # 5. Length maps only to LENGTH / LENGTH_UOM
        ExtractedFact(attribute="Length", raw_value="18 inches", normalized_value="18 Inches", is_valid=True, validation_status="VALIDATED", evidence_text="", source_id="", source_url="", source_type="", confidence=1.0),
        # 6. Other attributes map deterministically to generic slots
        ExtractedFact(attribute="Material", raw_value="Steel", normalized_value="Steel", is_valid=True, validation_status="VALIDATED", evidence_text="", source_id="", source_url="", source_type="", confidence=1.0),
        ExtractedFact(attribute="Color", raw_value="Silver", normalized_value="Silver", is_valid=True, validation_status="VALIDATED", evidence_text="", source_id="", source_url="", source_type="", confidence=1.0),
        # 2. Invalid facts are excluded (Missing reference facts are also excluded by our strict mapping)
        ExtractedFact(attribute="BadFact", raw_value="Bad", normalized_value="Bad", is_valid=False, validation_status="NEEDS_REVIEW", evidence_text="", source_id="", source_url="", source_type="", confidence=1.0),
    ]
    
    row = ProductRow(
        row_id=1,
        mfg_part_num="ORIGINAL_MPN",
        part_desc="ORIGINAL_DESC",
        extraction=ExtractionResult(facts=facts)
    )
    
    # Generate output
    output_rows = map_to_output([row], headers)
    out = output_rows[0]
    
    # 8. Original input fields remain unchanged
    assert out["Mfg_Part_Num"] == "ORIGINAL_MPN"
    assert out["Part_Desc"] == "ORIGINAL_DESC"
    
    # 9. Exact 252-column header order is preserved
    assert list(out.keys()) == headers
    assert len(out) == 252
    
    # 4 & 5. Physical mappings
    assert out["WEIGHT"] == "5.5"
    assert out["WEIGHT_UOM"] == "Pounds"
    assert out["LENGTH"] == "18"
    assert out["LENGTH_UOM"] == "Inches"
    
    # Check that Weight and Length are NOT duplicated into generic slots
    for i in range(1, 51):
        label = out.get(f"ATTRIBUTE_LABEL {i}")
        if label:
            assert label.lower() not in ["weight", "length"]
            
    # 6. Generic slots deterministically mapped
    assert out["ATTRIBUTE_LABEL 1"] == "Material"
    assert out["ATTRIBUTE_VALUE 1"] == "Steel"
    assert out["ATTRIBUTE_UOM 1"] == ""
    
    assert out["ATTRIBUTE_LABEL 2"] == "Color"
    assert out["ATTRIBUTE_VALUE 2"] == "Silver"
    assert out["ATTRIBUTE_UOM 2"] == ""
    
    # BadFact is excluded
    assert out.get("ATTRIBUTE_LABEL 3", "") == ""
    
    # 10. Missing facts produce blanks
    assert out["HEIGHT"] == ""
    assert out["VOLUME"] == ""
    
    print("Output builder tests passed!")

if __name__ == "__main__":
    test_output_builder_rules()
