import re

input_file = "BFPerry_Letters_NER/BFPerryLetters_NER_doubleline_entity_correction.csv"
output_file = "BFPerry_Letters_NER/BFPerryLetters_NER_final.csv"

output_lines = []
prev_letter_number = ""

with open(input_file, "r", encoding="utf-8") as f:
    for line in f:
        line = line.rstrip('\n')
        parts = line.split(',')

        # Header line
        if line.startswith("letter_number,entity_name,entity_type"):
            output_lines.append(line + '\n')
            continue

        # If the first column is not a digit, fill with previous letter_number
        if not parts[0].isdigit():
            parts = [prev_letter_number] + parts

        # Update prev_letter_number if present
        if parts[0].isdigit():
            prev_letter_number = parts[0]

        # If entity_type is missing, add PERSON
        if len(parts) == 2:
            parts.append("PERSON")
        elif len(parts) == 1:
            parts += ["", "PERSON"]

        output_lines.append(','.join(parts) + '\n')

with open(output_file, "w", encoding="utf-8") as f:
    f.writelines(output_lines)

print(f"Processed file saved as {output_file}.")