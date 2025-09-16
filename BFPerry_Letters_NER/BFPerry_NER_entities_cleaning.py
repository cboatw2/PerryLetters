import csv

input_file = "BFPerry_NER_entities.csv"
output_file = "BFPerry_NER_entities_cleaned.csv"

output_lines = []
with open(input_file, "r", encoding="utf-8") as f:
    for line in f:
        if '"' in line:
            # Extract letter number and entity_type
            prefix, quoted, suffix = line.partition('"')
            entity_block, _, entity_type = quoted.partition('",')
            letter_number = prefix.strip(',').split(',')[0]
            # Split the quoted block into lines and remove empty lines
            entities = [e.strip() for e in entity_block.splitlines() if e.strip()]
            if len(entities) == 2:
                output_lines.append(f'{letter_number},{entities[0]},PERSON\n')
                output_lines.append(f'{letter_number},{entities[1]},LOCATION\n')
            elif len(entities) == 1:
                output_lines.append(f'{letter_number},{entities[0]},PERSON\n')
            # If no valid entities, skip
        else:
            output_lines.append(line)

cleaned_lines = [line.replace('"', "'") for line in output_lines]

with open(output_file, "w", encoding="utf-8") as f:
    f.writelines(cleaned_lines)

print(f"Cleaned lines saved to {output_file}.")