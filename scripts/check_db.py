import sqlite3
import json

conn = sqlite3.connect('../backend/upie.db')
c = conn.cursor()
c.execute("SELECT result_data FROM job_rows WHERE job_id = 'a802f513-05bb-4c3b-bb92-8844b53b951c' LIMIT 15")
rows = c.fetchall()

for r in rows:
    data = json.loads(r[0])
    print(f"MPN: {data.get('mfg_part_num')}")
    print(f"  Identity URL: {data.get('identity', {}).get('official_source_url')}")
    print(f"  Retrieved Content len: {len(data.get('retrieved_content') or '')}")
    if data.get('extraction') and data['extraction'].get('facts'):
        print(f"  Facts: {len(data['extraction']['facts'])}")
        for f in data['extraction']['facts'][:3]:
            print(f"    - {f.get('attribute')}: {f.get('raw_value')} | Valid: {f.get('is_valid')} | Status: {f.get('validation_status')}")
    else:
        print("  No facts")
    
    if data.get('content'):
        print(f"  Content present: Marketing Desc len: {len(data['content'].get('marketing_description', ''))}")
    else:
        print("  No content")
