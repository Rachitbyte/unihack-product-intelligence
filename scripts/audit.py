import csv
import json

filename = "job_a802f513-05bb-4c3b-bb92-8844b53b951c_eval_output.csv"

with open(filename, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)
    
total_rows = len(rows)

groups = {
    "Identity & Evidence": ["MFR URL", "Classpath"], # Exclude MPN and Manufacturer since they are pass-through
    "Generated Content": ["MARKETING_DESCRIPTION", "SHORT_DESC", "ITEM_FEATURES_1", "ITEM_FEATURES_2"],
    "Digital Assets": ["Product Image", "Alternate Image 1", "SDS", "Specification Sheet", "Instruction/Installation Manual"],
    "Extracted Specs": []
}

for col in rows[0].keys():
    if col not in groups["Identity & Evidence"] and col not in groups["Generated Content"] and col not in groups["Digital Assets"]:
        if col not in ["Mfg_Part_Num", "Part_Desc", "Part_Manuf", "E1_Brand", "Unilog_Brand", "DIB_Brand", "PART_NUMBER", "MANUFACTURER_PART_NUMBER", "MANUFACTURER_NAME", "BRAND_NAME"]:
            if col.startswith("ATTRIBUTE_LABEL") or col.startswith("WEIGHT") or col.startswith("LENGTH"):
                groups["Extracted Specs"].append(col)

counts = {k: 0 for k in groups.keys()}
enriched_examples = []

for row in rows:
    has_identity = any(row.get(c, "").strip() for c in groups["Identity & Evidence"])
    has_content = any(row.get(c, "").strip() for c in groups["Generated Content"])
    has_assets = any(row.get(c, "").strip() for c in groups["Digital Assets"])
    has_specs = any(row.get(c, "").strip() for c in groups["Extracted Specs"])
    
    if has_identity: counts["Identity & Evidence"] += 1
    if has_content: counts["Generated Content"] += 1
    if has_assets: counts["Digital Assets"] += 1
    if has_specs: counts["Extracted Specs"] += 1
    
    # We will grab any row that has AT LEAST some enrichment
    if has_identity or has_content or has_specs or has_assets:
        enriched_examples.append(row)

print("=== ENRICHMENT AUDIT ===")
print(f"Total Rows Processed: {total_rows}")
for k, v in counts.items():
    print(f"{k}: {v} rows with meaningful enrichment")
    
print("\n=== ENRICHED EXAMPLES ===")
for idx, row in enumerate(enriched_examples[:3]):
    print(f"\n--- Example {idx+1} ---")
    print(f"MPN: {row.get('Mfg_Part_Num')}")
    print(f"Input Desc: {row.get('Part_Desc')}")
    print(f"Source URL: {row.get('MFR URL')}")
    print(f"Marketing Desc: {row.get('MARKETING_DESCRIPTION')[:150]}...")
    specs = {k: row[k] for k in groups["Extracted Specs"] if row.get(k, "").strip()}
    print(f"Specs Extracted: {specs}")
