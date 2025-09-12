input_file = "BFPerry_NER_entities_cleaned.csv"
output_file = "BFPerry_NER_entities_fixed.csv"

output_lines = []
with open(input_file, "r", encoding="utf-8") as f:
    for line in f:
        line = line.rstrip('\n')
        # Skip header
        if line.startswith("letter_number,entity_name,entity_type"):
            output_lines.append(line + '\n')
            continue
        # If line does not end with ,PERSON or ,LOCATION, add ,PERSON
        if not (line.endswith(",PERSON") or line.endswith(",LOCATION")):
            output_lines.append(line + ",PERSON\n")
        else:
            output_lines.append(line + '\n')

with open(output_file, "w", encoding="utf-8") as f:
    f.writelines(output_lines)

print(f"Fixed lines saved to {output_file}.")