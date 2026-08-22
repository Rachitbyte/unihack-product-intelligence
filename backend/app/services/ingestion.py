import csv
import io
from typing import List, Tuple
from app.schemas.schemas import ProductRow

PLACEHOLDERS = {
    "-- Unbranded --",
    "-- No Unilog Brand --",
    "-- No DIB Brand --",
    "",
    " ",
    "null",
    "none"
}

def clean_value(val: str) -> str:
    if not val:
        return ""
    val = val.strip()
    if val in PLACEHOLDERS:
        return ""
    return val

def parse_input_csv(content: str) -> Tuple[List[ProductRow], List[dict]]:
    rows = []
    errors = []
    
    if content.startswith('\ufeff'):
        content = content[1:]
        
    # Use io.StringIO to parse content
    reader = csv.DictReader(io.StringIO(content))
    
    # Required headers
    required = {"Mfg_Part_Num", "Part_Desc", "E1_Brand", "Unilog_Brand", "DIB_Brand", "Part_Manuf"}
    
    if reader.fieldnames:
        actual_headers = set([h.strip() for h in reader.fieldnames if h])
        if not required.issubset(actual_headers):
            errors.append({"row": 0, "error": f"Missing required headers. Expected: {required}, Got: {actual_headers}"})
            return [], errors

    for idx, row in enumerate(reader, start=1):
        try:
            mfg_part_num = row.get("Mfg_Part_Num", "").strip()
            if not mfg_part_num:
                errors.append({"row": idx, "error": "Missing Mfg_Part_Num"})
                continue
                
            p_row = ProductRow(
                row_id=idx,
                mfg_part_num=mfg_part_num,
                part_desc=clean_value(row.get("Part_Desc", "")),
                e1_brand=clean_value(row.get("E1_Brand", "")),
                unilog_brand=clean_value(row.get("Unilog_Brand", "")),
                dib_brand=clean_value(row.get("DIB_Brand", "")),
                part_manuf=clean_value(row.get("Part_Manuf", ""))
            )
            rows.append(p_row)
        except Exception as e:
            errors.append({"row": idx, "error": f"Malformed row: {str(e)}"})
            
    return rows, errors
