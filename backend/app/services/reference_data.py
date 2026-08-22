import os
import csv
import logging

logger = logging.getLogger(__name__)

class ReferenceDataService:
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            # Default to backend/../reference_data/
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.data_dir = os.path.abspath(os.path.join(current_dir, "../../../reference_data"))
        else:
            self.data_dir = data_dir

        self.manufacturers_map = {}
        self.brands_map = {}
        self.uom_map = {}
        self.lov_data = {}
        
        # Phase 6 tracking
        self.manufacturers_loaded = False
        self.uom_loaded = False
        self.lov_loaded = False
        
        self.load_all()

    def _get_path(self, filename: str) -> str:
        return os.path.join(self.data_dir, filename)

    def load_all(self):
        self._load_manufacturers()
        self._load_uom()
        self._load_lov()

    def _load_manufacturers(self):
        """
        Expects a CSV with headers: alias, canonical_name, type (Manufacturer/Brand)
        """
        path = self._get_path("manufacturer_master.csv")
        if not os.path.exists(path):
            logger.warning(f"Reference file not found: {path}. Manufacturer normalization will be disabled.")
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    alias = row.get("alias", "").strip().lower()
                    canonical = row.get("canonical_name", "").strip()
                    m_type = row.get("type", "").strip().lower()
                    
                    if not alias or not canonical:
                        continue
                        
                    if m_type == "brand":
                        self.brands_map[alias] = canonical
                    else:
                        self.manufacturers_map[alias] = canonical
            self.manufacturers_loaded = True
        except Exception as e:
            logger.error(f"Error loading {path}: {e}")

    def _load_uom(self):
        """
        Expects a CSV with headers: raw_uom, canonical_uom
        """
        path = self._get_path("uom_master.csv")
        if not os.path.exists(path):
            logger.warning(f"Reference file not found: {path}. UOM normalization will be disabled.")
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    raw = row.get("raw_uom", "").strip().lower()
                    canonical = row.get("canonical_uom", "").strip()
                    if raw and canonical:
                        self.uom_map[raw] = canonical
            self.uom_loaded = True
        except Exception as e:
            logger.error(f"Error loading {path}: {e}")

    def _load_lov(self):
        """
        Expects a CSV with headers: category, attribute, allowed_value
        """
        path = self._get_path("lov.csv")
        if not os.path.exists(path):
            logger.warning(f"Reference file not found: {path}. LOV validation will be disabled.")
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    category = row.get("category", "").strip().lower()
                    attribute = row.get("attribute", "").strip().lower()
                    allowed_val = row.get("allowed_value", "").strip()
                    
                    if not category or not attribute or not allowed_val:
                        continue
                        
                    if category not in self.lov_data:
                        self.lov_data[category] = {}
                    if attribute not in self.lov_data[category]:
                        self.lov_data[category][attribute] = set()
                        
                    self.lov_data[category][attribute].add(allowed_val)
            self.lov_loaded = True
        except Exception as e:
            logger.error(f"Error loading {path}: {e}")

    def normalize_manufacturer(self, raw_name: str) -> str:
        """Returns canonical manufacturer if found, else original raw name."""
        if not raw_name:
            return raw_name
        lookup = raw_name.strip().lower()
        return self.manufacturers_map.get(lookup, raw_name.strip())

    def normalize_brand(self, raw_name: str) -> str:
        """Returns canonical brand if found, else original raw name."""
        if not raw_name:
            return raw_name
        lookup = raw_name.strip().lower()
        return self.brands_map.get(lookup, raw_name.strip())

    def normalize_uom(self, raw_uom: str) -> str:
        """Returns canonical UOM if found, else original raw uom."""
        if not raw_uom:
            return raw_uom
        lookup = raw_uom.strip().lower()
        return self.uom_map.get(lookup, raw_uom.strip())

    def validate_lov(self, category: str, attribute: str, value: str) -> bool:
        """
        Returns True if the value is allowed for the category/attribute.
        If no LOV rules exist for this category/attribute, defaults to True (permissive).
        """
        if not category or not attribute or not value:
            return True
            
        cat_key = category.strip().lower()
        attr_key = attribute.strip().lower()
        
        if cat_key not in self.lov_data:
            return True # No rules for this category
            
        if attr_key not in self.lov_data[cat_key]:
            return True # No rules for this attribute
            
        return value.strip() in self.lov_data[cat_key][attr_key]

# Singleton instance to be used across the app
reference_db = ReferenceDataService()
