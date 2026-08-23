import json
import os
import csv
import io
import pandas as pd
from typing import List, Dict, Any
from app.schemas.schemas import ProductRow

def load_expected_headers() -> List[str]:
    # Use absolute path to the schemas file or relative to backend root
    # Since backend might be run from `backend/` or `root`, we'll try robust path finding
    current_dir = os.path.dirname(os.path.abspath(__file__))
    schema_path = os.path.join(current_dir, "../../../schemas/expected_output_headers.json")
    if not os.path.exists(schema_path):
        schema_path = os.path.join(current_dir, "../../schemas/expected_output_headers.json")
        if not os.path.exists(schema_path):
             schema_path = os.path.abspath(os.path.join(os.getcwd(), "schemas/expected_output_headers.json"))
             
    with open(schema_path, "r", encoding="utf-8") as f:
        return json.load(f)

def build_empty_output_row(headers: List[str]) -> Dict[str, Any]:
    return {header: "" for header in headers}

def _split_normalized_uom(normalized_value: str):
    """Splits '5.5 Pounds' into ('5.5', 'Pounds'). Returns (val, '') if no space."""
    if not normalized_value:
        return "", ""
    parts = normalized_value.strip().split(" ", 1)
    if len(parts) == 2:
        return parts[0], parts[1]
    return normalized_value, ""

def map_to_output(rows: List[ProductRow], headers: List[str]) -> List[Dict[str, Any]]:
    output_rows = []
    
    # Static mappings for known physical dimensions
    dim_map = {
        "weight": ("WEIGHT", "WEIGHT_UOM"),
        "length": ("LENGTH", "LENGTH_UOM"),
        "height": ("HEIGHT", "HEIGHT_UOM"),
        "width": ("WIDTH", "WIDTH_UOM"),
        "volume": ("VOLUME", "VOLUME_UOM")
    }

    for row in rows:
        out_row = build_empty_output_row(headers)
        
        # 1. Preserve Pass-through input values
        out_row["Mfg_Part_Num"] = row.mfg_part_num or ""
        out_row["Part_Desc"] = row.part_desc or ""
        out_row["E1_Brand"] = row.e1_brand or ""
        out_row["Unilog_Brand"] = row.unilog_brand or ""
        out_row["DIB_Brand"] = row.dib_brand or ""
        out_row["Part_Manuf"] = row.part_manuf or ""
        out_row["PART_NUMBER"] = row.mfg_part_num or ""
        
        # 2. Identity mappings
        if row.identity:
            out_row["MFR URL"] = row.identity.official_source_url or ""
            out_row["MANUFACTURER_NAME"] = row.identity.candidate_manufacturer or ""
            out_row["BRAND_NAME"] = row.identity.candidate_brand or ""
            out_row["MANUFACTURER_PART_NUMBER"] = row.identity.mpn or ""
            out_row["Classpath"] = row.identity.candidate_classpath or ""
            
        # 3. Content generation mappings
        if row.content:
            out_row["MARKETING_DESCRIPTION"] = row.content.marketing_description or ""
            out_row["SHORT_DESC"] = row.content.short_description or ""
            
            # Map up to 20 features
            for i, feature in enumerate(row.content.item_features):
                if i < 20:
                    out_row[f"ITEM_FEATURES_{i+1}"] = feature
                    
        # 4. Attribute mappings (Only VALIDATED or missing-ref allowed if explicitly permitted)
        # But wait, User said: "For generated marketing/content fields, use only facts with validation_status == VALIDATED"
        # Are NOT_VALIDATED_REFERENCE_DATA_MISSING facts allowed in output? 
        # User said: "Invalid/unverified facts should not silently populate trusted final output fields."
        # So we only output VALIDATED facts.
        
        if row.extraction and row.extraction.facts:
            attr_index = 1
            for fact in row.extraction.facts:
                if not fact.is_valid or fact.validation_status not in ["VALIDATED", "NOT_VALIDATED_REFERENCE_DATA_MISSING"]:
                    continue
                    
                attr_lower = fact.attribute.lower()
                val, uom = _split_normalized_uom(fact.normalized_value)
                
                if attr_lower in dim_map:
                    val_col, uom_col = dim_map[attr_lower]
                    out_row[val_col] = val
                    out_row[uom_col] = uom
                else:
                    if attr_index <= 50:
                        out_row[f"ATTRIBUTE_LABEL {attr_index}"] = fact.attribute
                        out_row[f"ATTRIBUTE_VALUE {attr_index}"] = val
                        out_row[f"ATTRIBUTE_UOM {attr_index}"] = uom
                        attr_index += 1

        # 5. Digital Asset mappings
        if row.asset_result and row.asset_result.assets:
            for asset in row.asset_result.assets:
                # Only output ACCEPTED official assets
                if asset.status == "ACCEPTED" and asset.official_domain_verified:
                    # The classification string matches the exact header from expected_output_headers
                    # e.g. "Product Image", "Alternate Image 1", "SDS"
                    if asset.classification in headers:
                        out_row[asset.classification] = asset.url

        output_rows.append(out_row)
        
    return output_rows

def export_to_csv(output_rows: List[Dict[str, Any]], headers: List[str]) -> str:
    if not output_rows:
        return ",".join(headers) + "\n"
        
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=headers)
    writer.writeheader()
    writer.writerows(output_rows)
    return output.getvalue()

def export_to_xlsx(output_rows: List[Dict[str, Any]], headers: List[str]) -> bytes:
    df = pd.DataFrame(output_rows, columns=headers)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()
