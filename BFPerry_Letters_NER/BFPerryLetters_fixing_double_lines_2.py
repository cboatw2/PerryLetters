input_file = "BFPerry_NER_entities_fixed.csv"
output_file = "BFPerry_NER_entities_fixed_2.csv"

output_lines = []
with open(input_file, "r", encoding="utf-8") as f:
    for line in f:
        parts = line.rstrip('\n').split(',')
        # Skip header
        if line.startswith("letter_number,entity_name,entity_type"):
            output_lines.append(line + '\n')
            continue
        # If letter_number is missing or not a digit, change entity_type to LOCATION
        if (not parts[0].isdigit()):
            # If entity_type exists and is PERSON, change to LOCATION
            if len(parts) == 3 and parts[2] == "PERSON":
                parts[2] = "LOCATION"
                output_lines.append(','.join(parts) + '\n')
            # If only two columns and second is PERSON, change to LOCATION
            elif len(parts) == 2 and parts[1] == "PERSON":
                parts[1] = "LOCATION"
                output_lines.append(','.join(parts) + '\n')
            else:
                output_lines.append(line if line.endswith('\n') else line + '\n')
        else:
            output_lines.append(line if line.endswith('\n') else line + '\n')

with open(output_file, "w", encoding="utf-8") as f:
    f.writelines(output_lines)

print(f"Processed file saved as {output_file}.")