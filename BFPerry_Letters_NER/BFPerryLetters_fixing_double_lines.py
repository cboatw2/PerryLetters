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

# Overwrite lines without a letter_number and change entity_type from PERSON to LOCATION
final_output_lines = []
for line in output_lines:
    parts = line.rstrip('\n').split(',')
    # Skip header
    if line.startswith("letter_number,entity_name,entity_type"):
        final_output_lines.append(line)
        continue
    # If letter_number is missing or not a digit, change entity_type to LOCATION
    if (not parts[0].isdigit()) and len(parts) == 3 and parts[2] == "PERSON":
        parts[2] = "LOCATION"
        final_output_lines.append(','.join(parts) + '\n')
    else:
        final_output_lines.append(line if line.endswith('\n') else line + '\n')

with open(output_file, "w", encoding="utf-8") as f:
    f.writelines(final_output_lines)

print(f"Processed file overwritten: {output_file}")