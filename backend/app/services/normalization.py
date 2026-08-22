import re
import logging
from app.schemas.schemas import ProductRow, ExtractedFact
from app.services.reference_data import reference_db

logger = logging.getLogger(__name__)

class CategoryAdapter:
    # A simple adapter mapping classpath to internal category names
    def map_category(self, classpath: str) -> str:
        if not classpath:
            return ""
        
        cp_lower = classpath.lower()
        
        # Example mappings
        if "sanding" in cp_lower and "belt" in cp_lower:
            return "Sanding Belts"
        elif "drill" in cp_lower and "bit" in cp_lower:
            return "Drill Bits"
            
        # Fallback to returning the classpath itself as a category, 
        # but the validation service will mark it NEEDS_REVIEW if it doesn't match LOV
        return classpath.strip()

class NormalizationService:
    def __init__(self):
        self.category_adapter = CategoryAdapter()
        # Regex to detect numeric value + string unit (e.g. "5.5 lbs", "18 inches")
        self.uom_pattern = re.compile(r"^([\d\.]+)\s+([a-zA-Z\/\-]+)$")

    def normalize(self, row: ProductRow) -> None:
        if not row.extraction or not row.extraction.facts:
            return

        # 1. Category Resolution
        classpath = ""
        if row.identity and row.identity.candidate_classpath:
            classpath = row.identity.candidate_classpath
            
        category = self.category_adapter.map_category(classpath)

        # 2. Process each fact
        for fact in row.extraction.facts:
            self._process_fact(fact, category)

    def _process_fact(self, fact: ExtractedFact, category: str):
        raw_val = fact.raw_value.strip()
        normalized_val = raw_val

        # Step 1: Detect and Normalize UOM
        match = self.uom_pattern.match(raw_val)
        if match:
            numeric_part = match.group(1)
            raw_unit = match.group(2)
            
            # Driven entirely by ReferenceDataService
            canonical_unit = reference_db.normalize_uom(raw_unit)
            
            if canonical_unit != raw_unit:
                # Normalization occurred
                normalized_val = f"{numeric_part} {canonical_unit}"
            else:
                # No normalization occurred, could be missing data or already canonical
                pass

        fact.normalized_value = normalized_val

        # Step 2: Validate LOV
        self._validate_lov(fact, category)

    def _validate_lov(self, fact: ExtractedFact, category: str):
        # If the LOV file wasn't even loaded, we can't truly validate
        if not reference_db.lov_loaded:
            fact.is_valid = True
            fact.validation_status = "NOT_VALIDATED_REFERENCE_DATA_MISSING"
            fact.validation_message = "LOV reference data missing. Permissive fallback applied."
            return

        if not category:
            fact.is_valid = False
            fact.validation_status = "NEEDS_REVIEW"
            fact.validation_message = "Category could not be resolved from classpath."
            return
            
        cat_key = category.strip().lower()
        attr_key = fact.attribute.strip().lower()

        # If category doesn't exist in our known LOV map, it's ambiguous
        if cat_key not in reference_db.lov_data:
            fact.is_valid = False
            fact.validation_status = "NEEDS_REVIEW"
            fact.validation_message = f"Category '{category}' is unknown in reference data."
            return

        # If the attribute has rules for this category, check the value
        if attr_key in reference_db.lov_data[cat_key]:
            if fact.normalized_value.strip() in reference_db.lov_data[cat_key][attr_key]:
                fact.is_valid = True
                fact.validation_status = "VALIDATED"
                fact.validation_message = "Value matches LOV constraints."
            else:
                fact.is_valid = False
                fact.validation_status = "NEEDS_REVIEW"
                fact.validation_message = "Value is not present in the allowed LOV values for this attribute."
        else:
            # Attribute doesn't have strict LOV rules for this category, so it's inherently valid
            fact.is_valid = True
            fact.validation_status = "VALIDATED"
            fact.validation_message = "No strict LOV rules exist for this attribute; assumed valid."

normalization_service = NormalizationService()
