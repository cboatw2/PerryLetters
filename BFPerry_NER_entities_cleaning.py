import csv

input_file = "BFPerry_NER_entities.csv"

output_lines = []
with open(input_file, "r", encoding="utf-8") as f:
    for line in f:
        if '"' in line and "\n" in line:
            prefix, quoted, suffix = line.partition('"')
            entity_block, _, entity_type = quoted.partition('",')
            entities = entity_block.splitlines()
            letter_number = prefix.strip(',').split(',')[0]
            # First line: PERSON
            if entities:
                output_lines.append(f'{letter_number},{entities[0].strip()},PERSON\n')
            # Second line: LOCATION (if present)
            if len(entities) > 1:
                output_lines.append(f'{letter_number},{entities[1].strip()},LOCATION\n')
        else:
            output_lines.append(line)

with open(input_file, "w", encoding="utf-8") as f:
    f.writelines(output_lines)

print(f"Overwritten {input_file} with cleaned lines.")