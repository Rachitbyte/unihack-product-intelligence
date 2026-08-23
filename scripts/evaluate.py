import requests
import time
import os
import sys

API_URL = os.getenv("API_URL", "http://localhost:8000/api/jobs")

def main():
    if len(sys.argv) < 2:
        print("Usage: python evaluate.py <path_to_csv>")
        sys.exit(1)
        
    file_path = sys.argv[1]
    
    print("1. Creating Job...")
    res = requests.post(API_URL)
    if not res.ok:
        print(f"Failed to create job: {res.text}")
        sys.exit(1)
        
    job = res.json()
    job_id = job["id"]
    print(f"Created Job ID: {job_id}")
    
    print(f"2. Uploading {file_path}...")
    start_time = time.time()
    
    with open(file_path, "rb") as f:
        files = {"file": f}
        upload_res = requests.post(f"{API_URL}/{job_id}/upload", files=files)
        
    if not upload_res.ok:
        print(f"Failed to upload: {upload_res.text}")
        sys.exit(1)
        
    print("3. Waiting for processing to complete...")
    while True:
        status_res = requests.get(f"{API_URL}/{job_id}")
        if not status_res.ok:
            print(f"Error fetching status: {status_res.text}")
            sys.exit(1)
            
        current_job = status_res.json()
        print(f"\rStatus: {current_job['status']} | Processed: {current_job['processed_rows']}/{current_job['total_rows']} | Failed: {current_job['failed_rows']}", end="")
        
        if current_job["status"] not in ["CREATED", "PROCESSING"]:
            print()
            break
            
        time.sleep(2)
        
    end_time = time.time()
    total_time = end_time - start_time
    
    print("\n--- EVALUATION RESULTS ---")
    print(f"Total Rows: {current_job['total_rows']}")
    print(f"Processed: {current_job['processed_rows']}")
    print(f"Failed: {current_job['failed_rows']}")
    
    import sqlite3
    import json
    
    print(f"\n--- DISCOVERY METRICS ---")
    try:
        conn = sqlite3.connect('../backend/upie.db')
        c = conn.cursor()
        c.execute("SELECT result_data FROM job_rows WHERE job_id = ?", (job_id,))
        rows = c.fetchall()
        
        statuses = {
            "OFFICIAL_PRODUCT_PAGE_FOUND": 0,
            "OFFICIAL_DOCUMENT_FOUND": 0,
            "MANUFACTURER_FOUND_PRODUCT_NOT_FOUND": 0,
            "DISCOVERY_FAILED": 0,
            "NEEDS_REVIEW": 0
        }
        extraction_success = 0
        populated_outputs = 0
        
        for r in rows:
            data = json.loads(r[0])
            status = data.get("identity", {}).get("status", "DISCOVERY_FAILED") if data.get("identity") else "DISCOVERY_FAILED"
            statuses[status] = statuses.get(status, 0) + 1
            
            if data.get("extraction") and data["extraction"].get("facts"):
                extraction_success += 1
                populated_outputs += 1 # Rough proxy for now
                
        print(f"Discovery Success (Product + Doc): {statuses['OFFICIAL_PRODUCT_PAGE_FOUND'] + statuses['OFFICIAL_DOCUMENT_FOUND']}")
        print(f"  - Product-Page Success: {statuses['OFFICIAL_PRODUCT_PAGE_FOUND']}")
        print(f"  - Document Success: {statuses['OFFICIAL_DOCUMENT_FOUND']}")
        print(f"Discovery Failure: {statuses['DISCOVERY_FAILED']}")
        print(f"Manufacturer-Found-But-Product-Not-Found: {statuses['MANUFACTURER_FOUND_PRODUCT_NOT_FOUND']}")
        print(f"Needs Review: {statuses['NEEDS_REVIEW']}")
        print(f"Extraction Success: {extraction_success}")
        print(f"Populated Output Rows: {populated_outputs}")
    except Exception as e:
        print(f"Error reading DB: {e}")

    
    print(f"\n--- PERFORMANCE ---")
    print(f"Total Time: {total_time:.2f} seconds")
    if current_job['processed_rows'] > 0:
        print(f"Avg Time per Row: {total_time / current_job['processed_rows']:.2f} seconds")
        
    print("\n4. Downloading output schema...")
    csv_res = requests.get(f"{API_URL}/{job_id}/download/csv")
    if csv_res.ok:
        out_path = f"job_{job_id}_eval_output.csv"
        with open(out_path, "wb") as f:
            f.write(csv_res.content)
        print(f"Saved {out_path}")
        
        # Verify 252 columns (very basic check of first line)
        first_line = csv_res.content.decode('utf-8').split('\n')[0]
        columns = first_line.split(',')
        print(f"Output columns count: {len(columns)}")
        if len(columns) == 252:
            print("SCHEMA VERIFICATION: PASS (252 columns)")
        else:
            print("SCHEMA VERIFICATION: FAIL")
    else:
        print("Failed to download CSV.")

if __name__ == "__main__":
    main()
