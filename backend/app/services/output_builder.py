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

def map_to_output(rows: List[ProductRow], headers: List[str]) -> List[Dict[str, Any]]:
    output_rows = []
    for row in rows:
        out_row = build_empty_output_row(headers)
        
        # Pass-through input values according to Phase 1 logic
        out_row["Mfg_Part_Num"] = row.mfg_part_num or ""
        out_row["Part_Desc"] = row.part_desc or ""
        out_row["E1_Brand"] = row.e1_brand or ""
        out_row["Unilog_Brand"] = row.unilog_brand or ""
        out_row["DIB_Brand"] = row.dib_brand or ""
        out_row["Part_Manuf"] = row.part_manuf or ""
        
        # We could also pass them to PART_NUMBER if logic dictates, but for now just exactly to inputs
        out_row["PART_NUMBER"] = row.mfg_part_num or ""
        
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
