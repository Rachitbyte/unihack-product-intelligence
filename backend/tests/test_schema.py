import json
import csv
import io
import os
import pytest
from app.services.ingestion import parse_input_csv
from app.services.output_builder import load_expected_headers, map_to_output, export_to_csv

def test_schema_exact_match():
    # 1. Load expected headers directly
    headers = load_expected_headers()
    assert len(headers) == 252, f"Expected 252 headers, got {len(headers)}"

    # 2. Mock input CSV with normal and missing values
    mock_csv = """Mfg_Part_Num,Part_Desc,E1_Brand,Unilog_Brand,DIB_Brand,Part_Manuf
12345,Test Desc,-- Unbranded --,,DIB_BRAND,Test Manuf
,Missing MPN,,,,
"""
    rows, errors = parse_input_csv(mock_csv)
    
    # We expect 1 valid row, and 1 error row (missing MPN)
    assert len(rows) == 1
    assert len(errors) == 1
    
    # 3. Map to output
    output_rows = map_to_output(rows, headers)
    
    # 4. Generate CSV
    out_csv = export_to_csv(output_rows, headers)
    
    # 5. Parse output CSV and check headers
    reader = csv.reader(io.StringIO(out_csv))
    out_headers = next(reader)
    
    assert len(out_headers) == 252, "Output CSV does not have 252 columns"
    assert out_headers == headers, "Output headers do not exactly match expected headers"
    
    # 6. Check that the row was processed and mapped correctly without crashing
    data_row = next(reader)
    assert len(data_row) == 252
    
    # Check simple passthrough
    header_idx = headers.index("Mfg_Part_Num")
    assert data_row[header_idx] == "12345"
    
    header_idx_unbranded = headers.index("E1_Brand")
    assert data_row[header_idx_unbranded] == "", "Placeholder was not cleared"

if __name__ == "__main__":
    test_schema_exact_match()
    print("Test passed successfully!")

