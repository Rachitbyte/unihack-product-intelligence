from unittest.mock import patch, MagicMock
from app.schemas.schemas import ProductRow, IdentityResult, ExtractionResult, ExtractedFact
from app.services.normalization import normalization_service
from app.services.reference_data import reference_db

def _create_test_row(classpath, attribute, raw_value):
    return ProductRow(
        row_id=1,
        mfg_part_num="TEST",
        identity=IdentityResult(candidate_classpath=classpath),
        extraction=ExtractionResult(facts=[
            ExtractedFact(
                attribute=attribute,
                raw_value=raw_value,
                evidence_text="mock",
                source_id="mock",
                source_url="mock",
                source_type="HTML",
                confidence=1.0
            )
        ])
    )

def test_normalization():
    print("Running Normalization Tests...")

    # 1. Mock ReferenceDataService to simulate loaded data
    reference_db.manufacturers_loaded = True
    reference_db.uom_loaded = True
    reference_db.lov_loaded = True
    
    reference_db.uom_map = {"lbs": "Pounds", "in": "Inches"}
    reference_db.lov_data = {
        "sanding belts": {
            "material": {"Premium Zirconium Blend", "Ceramic"}
        }
    }

    # Test 1: Classpath -> Category mapping & valid LOV (Non-UOM)
    # Plus raw-value preservation
    row_1 = _create_test_row("Sanding Belt", "Material", "Premium Zirconium Blend")
    normalization_service.normalize(row_1)
    f1 = row_1.extraction.facts[0]
    
    assert f1.raw_value == "Premium Zirconium Blend" # preserved
    assert f1.normalized_value == "Premium Zirconium Blend"
    assert f1.is_valid is True
    assert f1.validation_status == "VALIDATED"

    # Test 2: Invalid LOV value (Non-UOM)
    row_2 = _create_test_row("Sanding Belt", "Material", "Steel")
    normalization_service.normalize(row_2)
    f2 = row_2.extraction.facts[0]
    
    assert f2.raw_value == "Steel"
    assert f2.normalized_value == "Steel"
    assert f2.is_valid is False
    assert f2.validation_status == "NEEDS_REVIEW"
    assert "not present in the allowed LOV" in f2.validation_message

    # Test 3: Numeric value + Unit (Normalization driven by ref data)
    # Even if attribute has no strict LOV rules, it is inherently valid
    row_3 = _create_test_row("Sanding Belt", "Weight", "5.5 lbs")
    normalization_service.normalize(row_3)
    f3 = row_3.extraction.facts[0]
    
    assert f3.raw_value == "5.5 lbs"
    assert f3.normalized_value == "5.5 Pounds"
    assert f3.is_valid is True
    assert f3.validation_status == "VALIDATED"

    # Test 4: Missing UOM data (driven by reference data, if "oz" not in map, no norm occurs)
    row_4 = _create_test_row("Sanding Belt", "Weight", "10 oz")
    normalization_service.normalize(row_4)
    f4 = row_4.extraction.facts[0]
    
    assert f4.raw_value == "10 oz"
    assert f4.normalized_value == "10 oz" # Not changed
    
    # Test 5: Ambiguous classpath (unknown category)
    row_5 = _create_test_row("Random Stuff", "Material", "Wood")
    normalization_service.normalize(row_5)
    f5 = row_5.extraction.facts[0]
    
    assert f5.is_valid is False
    assert f5.validation_status == "NEEDS_REVIEW"
    assert "unknown in reference data" in f5.validation_message
    
    # Test 6: Missing LOV Data (simulate file not loaded)
    reference_db.lov_loaded = False
    row_6 = _create_test_row("Sanding Belt", "Material", "Rubber")
    normalization_service.normalize(row_6)
    f6 = row_6.extraction.facts[0]
    
    assert f6.is_valid is True
    assert f6.validation_status == "NOT_VALIDATED_REFERENCE_DATA_MISSING"

    print("All normalization tests passed!")

if __name__ == "__main__":
    test_normalization()
