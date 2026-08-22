import os
from app.services.reference_data import ReferenceDataService

def test_reference_data_graceful_fallback():
    # Service should initialize safely even if files don't exist
    service = ReferenceDataService(data_dir="/tmp/non_existent_dir_123")
    
    # Missing lookups should fallback to original values
    assert service.normalize_manufacturer("Acme Corp") == "Acme Corp"
    assert service.normalize_brand("SuperBrand") == "SuperBrand"
    assert service.normalize_uom("inches") == "inches"
    
    # LOV validation defaults to True (permissive) if rules don't exist
    assert service.validate_lov("Fittings", "Material", "Brass") is True
    
    print("ReferenceDataService graceful fallback test passed!")

if __name__ == "__main__":
    test_reference_data_graceful_fallback()
