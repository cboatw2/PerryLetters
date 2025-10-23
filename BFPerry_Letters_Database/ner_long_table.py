import csv
import re

input_file = "NER_results.txt"
output_file = "NER_long_table.csv"

rows = []
year_range = None
entity_type = None

with open(input_file, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

for line in lines:
    line = line.strip()
    # Detect section header
    match = re.match(r"^=== Results from (.+?)\.txt ===$", line)
    if match:
        year_range = match.group(1).replace("BFPerry_Letters_", "").replace("_", "-")
        entity_type = None
        continue
    # Detect entity type
    if line == "Persons:":
        entity_type = "Person"
        continue
    elif line == "Places:":
        entity_type = "Place"
        continue
    # Add entity if in correct section
    if entity_type and line and not line.startswith("==="):
        rows.append([year_range, line, entity_type])

# Write to CSV
with open(output_file, "w", encoding="utf-8", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["year_range", "entity", "entity_type"])
    writer.writerows(rows)

print(f"Saved {len(rows)} rows to {output_file}")