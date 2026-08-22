import os
from app.services.ingestion import parse_input_csv
from app.services.output_builder import load_expected_headers, map_to_output, export_to_csv, export_to_xlsx

def main():
    input_file = "data/sample/input.csv"
    
    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()
        
    print(f"Read {len(content)} bytes from {input_file}")
    
    # 1. Parse Input
    rows, errors = parse_input_csv(content)
    print(f"Parsed {len(rows)} rows, found {len(errors)} errors")
    
    if errors:
        print(f"Sample error: {errors[0]}")
    
    # 2. Output Builder
    headers = load_expected_headers()
    print(f"Loaded {len(headers)} expected output headers")
    
    output_rows = map_to_output(rows, headers)
    
    # 3. Export CSV and XLSX
    csv_out = export_to_csv(output_rows, headers)
    
    os.makedirs("data/sample/output", exist_ok=True)
    with open("data/sample/output/expected_output_generated.csv", "w", encoding="utf-8", newline="") as f:
        f.write(csv_out)
        
    xlsx_out = export_to_xlsx(output_rows, headers)
    with open("data/sample/output/expected_output_generated.xlsx", "wb") as f:
        f.write(xlsx_out)
        
    print("Exported CSV and XLSX successfully to data/sample/output/")
    print(f"Processed Rows: {len(rows)}")
    print(f"Output Columns: {len(headers)}")

if __name__ == "__main__":
    main()
