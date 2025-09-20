input_file = "BFPerry_Letters_NER/BFPerry_NER_entities_fixed_2.csv"
output_file = "BFPerry_Letters_NER/BFPerry_NER_entities_fixed_3.csv"

output_lines = []
prev_letter_number = ""

with open(input_file, "r", encoding="utf-8") as f:
    for line in f:
        parts = line.rstrip('\n').split(',')
        # Header line
        if line.startswith("letter_number,entity_name,entity_type"):
            output_lines.append(line if line.endswith('\n') else line + '\n')
            continue
        # If 3 columns, update prev_letter_number
        if len(parts) == 3:
            prev_letter_number = parts[0]
            output_lines.append(line if line.endswith('\n') else line + '\n')
        # If 2 columns, fill letter_number from previous row
        elif len(parts) == 2:
            output_lines.append(f"{prev_letter_number},{parts[0]},{parts[1]}\n")
        else:
            output_lines.append(line if line.endswith('\n') else line + '\n')

with open(output_file, "w", encoding="utf-8") as f:
    f.writelines(output_lines)

print(f"Processed file saved as {output_file}.")